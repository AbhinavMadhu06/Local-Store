from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
import csv
from .models import User, ShopProfile, JobVacancy, JobApplication, VacancyComment
from .serializers import (
    UserSerializer, ShopProfileSerializer, JobVacancySerializer, 
    JobApplicationSerializer, VacancyCommentSerializer
)

class IsShopOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SHOP_OWNER'

class IsVerifiedShopOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user.is_authenticated and user.role == 'SHOP_OWNER'):
            return False
        return hasattr(user, 'shop_profile') and user.shop_profile.is_verified

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'detail': 'New passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({'detail': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user)
        except DjangoValidationError as exc:
            return Response({'detail': ' '.join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated], parser_classes=[MultiPartParser, FormParser, JSONParser])
    def update_profile(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ShopProfileViewSet(viewsets.ModelViewSet):
    queryset = ShopProfile.objects.all()
    serializer_class = ShopProfileSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'analytics']:
            return [IsShopOwner()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    @action(detail=False, methods=['get'], permission_classes=[IsShopOwner])
    def my_shop(self, request):
        try:
            shop = request.user.shop_profile
            serializer = self.get_serializer(shop)
            return Response(serializer.data)
        except ShopProfile.DoesNotExist:
            return Response({'detail': 'No shop profile found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[IsShopOwner])
    def analytics(self, request):
        shop = request.user.shop_profile
        
        # Aggregate stats
        total_jobs = JobVacancy.objects.filter(shop=shop).count()
        total_views = JobVacancy.objects.filter(shop=shop).aggregate(Sum('views'))['views__sum'] or 0
        total_applications = JobApplication.objects.filter(job__shop=shop).count()
        
        # Application breakdown
        accepted = JobApplication.objects.filter(job__shop=shop, status='ACCEPTED').count()
        rejected = JobApplication.objects.filter(job__shop=shop, status='REJECTED').count()
        pending = JobApplication.objects.filter(job__shop=shop, status='PENDING').count()
        
        # Job performance (views per job)
        jobs_performance = JobVacancy.objects.filter(shop=shop).values('title', 'views')
        
        return Response({
            'shop_verified': shop.is_verified,
            'kpis': {
                'total_jobs': total_jobs,
                'total_views': total_views,
                'total_applications': total_applications,
            },
            'applications_status': [
                {'name': 'Pending', 'value': pending},
                {'name': 'Accepted', 'value': accepted},
                {'name': 'Rejected', 'value': rejected},
            ],
            'jobs_performance': list(jobs_performance)
        })

class JobVacancyViewSet(viewsets.ModelViewSet):
    queryset = JobVacancy.objects.all()
    serializer_class = JobVacancySerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsVerifiedShopOwner()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        shop = self.request.user.shop_profile
        serializer.save(shop=shop)
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def apply(self, request, pk=None):
        job = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            return Response({'detail': 'You must be logged in to apply.'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if user.role != 'JOB_SEEKER':
            return Response({'detail': 'Only job seekers can apply.'}, status=status.HTTP_403_FORBIDDEN)
            
        if JobApplication.objects.filter(job=job, applicant=user).exists():
            return Response({'detail': 'You have already applied.'}, status=status.HTTP_400_BAD_REQUEST)

        # Allow multipart form data for CV upload
        serializer = JobApplicationSerializer(data=request.data)
        if serializer.is_valid():
            if not serializer.validated_data.get('meets_requirements', False):
                return Response({'detail': 'You must declare that you meet the requirements.'}, status=status.HTTP_400_BAD_REQUEST)
                
            serializer.save(applicant=user, job=job)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsVerifiedShopOwner])
    def bulk_reject_pending(self, request, pk=None):
        job = self.get_object()
        user = request.user
        
        # Verify ownership
        if getattr(user, 'shop_profile', None) != job.shop:
            return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)
            
        owner_note = request.data.get('owner_note', '')
        
        # Find all pending or shortlisted applications and reject them
        applications_to_reject = JobApplication.objects.filter(
            job=job, 
            status__in=['PENDING', 'SHORTLISTED']
        )
        
        count = applications_to_reject.count()
        applications_to_reject.update(status='REJECTED', owner_note=owner_note)
        
        return Response({'detail': f'Successfully rejected {count} applicants.', 'count': count}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsVerifiedShopOwner])
    def export_applicants_csv(self, request, pk=None):
        job = self.get_object()
        user = request.user
        
        # Verify ownership
        if getattr(user, 'shop_profile', None) != job.shop:
            return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)
            
        applications = JobApplication.objects.filter(job=job).select_related('applicant')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="applicants_job_{job.id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Mobile Number', 'Status', 'Applied Date', 'Meets Requirements', 'Applicant Notes'])
        
        for app in applications:
            writer.writerow([
                app.applicant.username,
                app.applicant.email,
                app.applicant.mobile_number,
                app.status,
                app.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if app.meets_requirements else 'No',
                app.notes
            ])
            
        return response

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comment(self, request, pk=None):
        job = self.get_object()
        serializer = VacancyCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, job=job)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser) # to handle file uploads and JSON updates

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'SHOP_OWNER':
            return JobApplication.objects.filter(job__shop__user=user)
        return JobApplication.objects.filter(applicant=user)

    def perform_create(self, serializer):
        # Prevent direct creation via this endpoint, use job apply action instead
        pass

class VacancyCommentViewSet(viewsets.ModelViewSet):
    queryset = VacancyComment.objects.all()
    serializer_class = VacancyCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        user = request.user
        
        # Check if user is shop owner and owns the job
        is_job_owner = (
            user.role == 'SHOP_OWNER' 
            and hasattr(user, 'shop_profile') 
            and comment.job.shop == user.shop_profile
        )
        
        # Also allow the user who posted the comment to delete it
        is_comment_author = comment.user == user

        if not (is_job_owner or is_comment_author):
            return Response({'detail': 'Not permitted to delete this comment.'}, status=status.HTTP_403_FORBIDDEN)
            
        return super().destroy(request, *args, **kwargs)
