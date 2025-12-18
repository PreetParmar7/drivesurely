from django.contrib import admin
from .models import Car
from django.contrib import admin
from .models import DealerProfile
from django.core.mail import send_mail
from django.conf import settings
"""
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'brand',
        'engine_capacity',
        'price',
        'fuel_type',
        'status',
        'dealer',
        'transmission',
        'mileage',
    )
    list_filter = ('brand', 'fuel_type', 'status')
    search_fields = ('title', 'brand')
"""
# Register your models here.
# admin.site.register(Car, CarAdmin)
from django.contrib import admin
from .models import Car, CarImage

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 3

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'price', 'status', 'dealer')
    inlines = [CarImageInline]
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
from django.core.mail import send_mail
from django.conf import settings

from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings

from .models import DealerProfile


@admin.register(DealerProfile)
class DealerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('company_name', 'user__username')

    fields = (
        'user',
        'company_name',
        'about',
        'gst_number',
        'gst_document',
        'id_document',
        'is_verified',
        'admin_message',
    )

    def save_model(self, request, obj, form, change):
        if change:
            old = DealerProfile.objects.get(pk=obj.pk)

            if old.is_verified != obj.is_verified:
                status = "APPROVED" if obj.is_verified else "UNDER REVIEW"

                send_mail(
                    subject=f"Dealer Verification {status}",
                    message=(
                        f"Hello {obj.user.username},\n\n"
                        f"Your dealer verification status has been updated.\n\n"
                        f"Status: {status}\n\n"
                        f"Message from admin:\n"
                        f"{obj.admin_message or 'No message provided.'}\n\n"
                        f"— DriveSurely Team"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.user.email],
                    fail_silently=True,
                )

        super().save_model(request, obj, form, change)

