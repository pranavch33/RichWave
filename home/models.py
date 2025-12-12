from django.db import models
from django.conf import settings

# Create your models here.
from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200)
    banner_url = models.URLField()
    short_description = models.TextField(blank=True)
    price = models.IntegerField()
    level = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_url = models.URLField()

    def __str__(self):
        return self.title

# home/models.py

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return self.user.username

from django.db import models
from django.contrib.auth.models import User

class KYC(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    type = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=200)
    holder_name = models.CharField(max_length=200)
    ifsc = models.CharField(max_length=20)
    account_number = models.CharField(max_length=30)
    upi_id = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

from django.db import models
from django.contrib.auth.models import User

class AffiliateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.user.username


class Package(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price = models.IntegerField(default=0)  # <-- IMPORTANT FIELD

    def __str__(self):
        return self.name

class LeaderboardEntry(models.Model):
    RANK_CHOICES = [
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('all', 'All Time'),
    ]

    name = models.CharField(max_length=150)
    avatar_url = models.URLField(blank=True)  # photo link, optional
    total_earning = models.DecimalField(max_digits=12, decimal_places=2)
    rank = models.PositiveIntegerField()  # 1,2,3,...10
    period = models.CharField(max_length=20, choices=RANK_CHOICES, default='all')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return f"{self.rank}. {self.name}"

from django.db import models
from django.contrib.auth.models import User


class PaymentRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    # Kis seller ka referral code use hua
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="payment_requests"
    )

    buyer_name = models.CharField(max_length=150)
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=20)

    sponsor_code = models.CharField(max_length=50, blank=True)

    package_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer_name} • {self.package_name} • {self.status}"

from django.db import models
from django.contrib.auth.models import User

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.IntegerField()
    status = models.CharField(max_length=20, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"


# home/models.py  (paste at end if not present)
from django.db import models
from django.utils import timezone

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('success', 'Success'),
    ('failed', 'Failed'),
)

class RegistrationRequest(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    plan = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# file: home/models.py
from django.db import models
from django.utils import timezone

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('success', 'Success'),
    ('failed', 'Failed'),
)

class UpgradeRequest(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    plan = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id} - {self.name} - {self.plan}"


from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

user = get_user_model()

class WalletTransaction(models.Model):
    TYPE_CHOICES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    user = models.ForeignKey(user, on_delete=models.CASCADE)   # ⭐ REQUIRED FIELD

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=255, blank=True, null=True)
    tx_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='credit')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id} - {self.tx_type} - ₹{self.amount}"

# file: home/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Associate(models.Model):
    # jo user ne refer kiya (owner)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="associates")
    # associate user details (if stored separately)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    course_name = models.CharField(max_length=255, blank=True, null=True)
    joined_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.email})"


class WithdrawalRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.amount} - {self.status}"