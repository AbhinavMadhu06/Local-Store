from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('SHOP_OWNER', 'Shop Owner'),
        ('JOB_SEEKER', 'Job Seeker'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='JOB_SEEKER')
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

class ShopProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop_profile')
    company_name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name

class JobVacancy(models.Model):
    JOB_TYPE_CHOICES = (
        ('FULL_TIME', 'Full-Time'),
        ('PART_TIME', 'Part-Time'),
        ('REMOTE', 'Remote'),
        ('ON_SITE', 'On-Site'),
        ('HYBRID', 'Hybrid'),
        ('CONTRACT', 'Contract'),
    )
    shop = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, related_name='vacancies')
    title = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default='FULL_TIME')
    description = models.TextField()
    skills_required = models.TextField()
    experience_required = models.CharField(max_length=255)
    education_required = models.CharField(max_length=255)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='job_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.shop.company_name}"

from django.core.files.storage import storages

def select_raw_storage():
    return storages['raw_media']

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SHORTLISTED', 'Shortlisted'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    )
    job = models.ForeignKey(JobVacancy, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    meets_requirements = models.BooleanField(default=False)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    cv = models.FileField(upload_to='cvs/', blank=True, null=True, storage=select_raw_storage)
    notes = models.TextField(blank=True, null=True)
    owner_note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.username} for {self.job.title}"

class VacancyComment(models.Model):
    job = models.ForeignKey(JobVacancy, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.job.title}"
