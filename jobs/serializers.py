from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, ShopProfile, JobVacancy, JobApplication, VacancyComment

class UserSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(write_only=True, required=False)
    description = serializers.CharField(write_only=True, required=False)
    location = serializers.CharField(write_only=True, required=False)
    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    logo = serializers.ImageField(write_only=True, required=False, allow_null=True)
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'password', 'mobile_number', 'profile_photo', 'company_name', 'description', 'location', 'latitude', 'longitude', 'logo')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def get_profile_photo(self, obj):
        if obj.profile_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
            return obj.profile_photo.url
        return None

    def create(self, validated_data):
        company_name = validated_data.pop('company_name', None)
        description = validated_data.pop('description', None)
        location = validated_data.pop('location', None)
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        logo = validated_data.pop('logo', None)
        
        is_shop_owner = validated_data.get('role') == 'SHOP_OWNER'
        
        user = User.objects.create_user(**validated_data)
        
        # Create ShopProfile if Shop Owner
        if is_shop_owner and company_name and description and location:
            ShopProfile.objects.create(
                user=user,
                company_name=company_name,
                description=description,
                location=location,
                latitude=latitude,
                longitude=longitude,
                logo=logo
            )
            
        return user

class ShopProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = ShopProfile
        fields = ('id', 'user', 'company_name', 'description', 'location', 'latitude', 'longitude', 'logo', 'is_verified', 'created_at')

    def get_logo(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None

class VacancyCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = VacancyComment
        fields = ('id', 'job', 'user', 'text', 'parent', 'created_at', 'replies')
        read_only_fields = ('user', 'job')

    def get_replies(self, obj):
        if obj.replies.exists():
            return VacancyCommentSerializer(obj.replies.all(), many=True).data
        return []

class JobVacancySerializer(serializers.ModelSerializer):
    shop = ShopProfileSerializer(read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = JobVacancy
        fields = (
            'id', 'shop', 'title', 'job_type', 'description', 'skills_required', 
            'experience_required', 'education_required', 'salary_range', 'image',
            'is_active', 'created_at', 'comments'
        )

    def get_comments(self, obj):
        # Only serialize top-level comments
        top_level_comments = obj.comments.filter(parent__isnull=True)
        return VacancyCommentSerializer(top_level_comments, many=True).data

class JobApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    job_details = JobVacancySerializer(source='job', read_only=True)

    class Meta:
        model = JobApplication
        fields = (
            'id', 'job', 'job_details', 'applicant', 'meets_requirements', 
            'contact_number', 'cv', 'notes', 'owner_note', 'status', 'applied_at'
        )
        read_only_fields = ('applicant', 'job')
