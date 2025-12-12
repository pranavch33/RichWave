from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Course, Package, AffiliateProfile, KYC, Profile, Video, LeaderboardEntry

admin.site.register(Course)
admin.site.register(Package)
admin.site.register(AffiliateProfile)
admin.site.register(KYC)
admin.site.register(Profile)
admin.site.register(Video)
admin.site.register(LeaderboardEntry)

from django.contrib import admin
from .models import PaymentRequest

admin.site.register(PaymentRequest)




from django.contrib import admin
from .models import RegistrationRequest

@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'plan', 'amount', 'status', 'created_at')
    list_filter = ('status', 'plan', 'created_at')
    search_fields = ('name', 'email', 'phone')
    ordering = ('-created_at',)


# file: home/admin.py
from django.contrib import admin
from .models import UpgradeRequest

@admin.register(UpgradeRequest)
class UpgradeRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'plan', 'amount', 'status', 'created_at')
    list_filter = ('status', 'plan', 'created_at')
    search_fields = ('name', 'email', 'phone')


# file: home/admin.py
from django.contrib import admin
from .models import WalletTransaction, UpgradeRequest, UpgradeRequest  # existing models kept

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "source", "tx_type", "created_at")
    list_filter = ("tx_type", "created_at")
    search_fields = ("source",)

# file: home/admin.py
from django.contrib import admin
from .models import Associate

@admin.register(Associate)
class AssociateAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "name", "phone", "email", "course_name", "joined_at")
    list_filter = ("joined_at",)
    search_fields = ("name", "email", "phone", "course_name")


