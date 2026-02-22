from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ShopProfileViewSet, JobVacancyViewSet, JobApplicationViewSet, VacancyCommentViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'shops', ShopProfileViewSet)
router.register(r'jobs', JobVacancyViewSet)
router.register(r'applications', JobApplicationViewSet)
router.register(r'comments', VacancyCommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
