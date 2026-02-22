from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ShopProfile, JobVacancy, JobApplication, VacancyComment

class ShopProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'is_verified', 'created_at')
    list_filter = ('is_verified',)
    list_editable = ('is_verified',)

admin.site.register(User, UserAdmin)
admin.site.register(ShopProfile, ShopProfileAdmin)
admin.site.register(JobVacancy)
admin.site.register(JobApplication)
admin.site.register(VacancyComment)
