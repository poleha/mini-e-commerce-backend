from django.contrib import admin
from . import models


@admin.register(models.VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    pass