from django.shortcuts import render, redirect
from .models import Course, Profile
from django.contrib.auth.models import User
from .models import PaymentRequest, Package
from django.utils import timezone
import uuid
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Associate
from .utils import get_withdrawable_balance

# Home Page – active courses list
def home(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'home.html', {'courses': courses})


# Login Page
def login_page(request):
    return render(request, 'login.html')


# Signup Page
def signup_page(request):
    return render(request, 'signup.html')


# Dashboard Page
def dashboard_page(request):
    return render(request, 'dashboard.html')


def affiliate_dashboard(request):
    withdrawable = get_withdrawable_balance(request.user)

    return render(request, "affiliate_dashboard.html", {
        "withdrawable": withdrawable,
    })

# ⭐ PROFILE PAGE (NEW)
def profile_page(request):
    profile = None

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except:
            profile = Profile.objects.create(user=request.user)

    return render(request, 'profile.html', {'profile': profile})


# ⭐ UPDATE PROFILE PAGE (NEW)
def update_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = request.user.profile

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        gender = request.POST.get("gender")
        avatar = request.FILES.get("avatar")

        # Update Django User table
        request.user.first_name = name
        request.user.save()

        # Update Profile table
        profile.phone = phone
        profile.gender = gender

        if avatar:
            profile.avatar = avatar

        profile.save()

        return redirect('profile')

    return render(request, 'profile_update.html', {"profile": profile})
from django.shortcuts import render
from .models import KYC
from .forms import KYCForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def kyc_page(request):
    try:
        kyc_obj = request.user.kyc
    except:
        kyc_obj = None

    if request.method == "POST":
        form = KYCForm(request.POST, instance=kyc_obj)
        if form.is_valid():
            kyc_new = form.save(commit=False)
            kyc_new.user = request.user
            kyc_new.save()

            messages.success(request, "🎉 Your KYC details were submitted successfully!")
    else:
        form = KYCForm(instance=kyc_obj)

    return render(request, "kyc.html", {"form": form})

from .models import AffiliateProfile, Package, User

def affiliate_link(request):

    # Agar user login nahi hai to default user lelo
    if not request.user.is_authenticated:
        # ID = 1 wala koi default user rakh lena admin me
        default_user = User.objects.get(id=1)
        profile, created = AffiliateProfile.objects.get_or_create(user=default_user)
    else:
        profile = AffiliateProfile.objects.get(user=request.user)

    packages = Package.objects.all()
    base_url = "https://thriveon.in"
    referral_link = f"{base_url}?ref={profile.referral_code}"

    selected_package = None
    package_link = None

    if request.GET.get("package"):
        selected_package = Package.objects.get(id=request.GET.get("package"))
        package_link = f"{base_url}/pay/{selected_package.name}/?ref={profile.referral_code}"

    return render(request, "affiliate_link.html", {
        "profile": profile,
        "referral_link": referral_link,
        "packages": packages,
        "selected_package": selected_package,
        "package_link": package_link,
    })
def my_courses(request):
    return render(request, "my_courses.html")

def leaderboard(request):
    return render(request, 'leaderboard.html')

from django.shortcuts import render
from .models import LeaderboardEntry

def leaderboard(request):
    period = request.GET.get("period", "today")  # default = today

    # Filter according to selected period
    if period == "today":
        entries = LeaderboardEntry.objects.filter(period="Today").order_by("rank")[:10]

    elif period == "7days":
        entries = LeaderboardEntry.objects.filter(period="7days").order_by("rank")[:10]

    elif period == "30days":
        entries = LeaderboardEntry.objects.filter(period="30days").order_by("rank")[:10]

    else:  # all time
        entries = LeaderboardEntry.objects.filter(period="all").order_by("rank")[:10]

    return render(request, "leaderboard.html", {
        "entries": entries,
        "period": period,
    })
from django.shortcuts import render, redirect
from django.conf import settings
import uuid, requests

def checkout(request, slug):

    package_prices = {
        "basic": 529,
        "grow": 999,
        "prime": 1498,
        "elite": 2699,
        "power": 5698,
        "ultimate": 11699,
    }

    amount = package_prices.get(slug)
    if not amount:
        return redirect("/")

    if request.method == "GET":
        return render(request, "checkout.html", {
            "amount": amount,
            "slug": slug
        })

    # ---------- POST ----------
    order_id = f"order_{uuid.uuid4().hex[:10]}"

    headers = {
        "x-client-id": settings.CASHFREE_CLIENT_ID,
        "x-client-secret": settings.CASHFREE_CLIENT_SECRET,
        "x-api-version": "2023-08-01",
        "Content-Type": "application/json"
    }

    payload = {
        "order_id": order_id,
        "order_amount": amount,
        "order_currency": "INR",
        "customer_details": {
            "customer_id": "cust_001",
            "customer_email": request.POST.get("email"),
            "customer_phone": request.POST.get("phone")
        },
        "order_meta": {
            "return_url": "https://thriveonindia.com/payment/success/?order_id={order_id}"
        }
    }

    url = "https://sandbox.cashfree.com/pg/orders"

    res = requests.post(url, json=payload, headers=headers)
    data = res.json()

    if "payment_session_id" not in data:
        print(data)
        return redirect("/payment-failed/")

    return redirect(
        f"https://sandbox.cashfree.com/pg/view/payment-session?payment_session_id={data['payment_session_id']}"
    )
# ----------------------------
# PAYMENT SYSTEM
# ----------------------------

from django.shortcuts import redirect, render

def payment_checkout(request, package_name):
    try:
        package = Package.objects.get(name=package_name)
    except:
        return render(request, "error.html", {"msg": "Package not found"})

    pay = PaymentRequest.objects.create(
        buyer_name=request.POST.get("name"),
        buyer_email=request.POST.get("email"),
        buyer_phone=request.POST.get("phone"),
        package_name=package.name,
        amount=package.price,
        referral_code_used=request.POST.get("sponsor_code"),
        status="pending",
        created_at=timezone.now()
    )

    return redirect(f"/payment-waiting/{pay.id}/")


def payment_waiting(request, payment_id):
    try:
        pay = PaymentRequest.objects.get(id=payment_id)
    except:
        return render(request, "error.html", {"msg": "Invalid Payment"})

    return render(request, "payment_waiting.html", {"pay": pay})

def seller_pending_payments(request):
    pending = PaymentRequest.objects.filter(status="pending").order_by("-created_at")
    return render(request, "pending_payments.html", {"pending": pending})

from .models import PaymentRequest

def seller_pending_payments(request):
    pending = PaymentRequest.objects.filter(status="pending").order_by("-created_at")
    return render(request, "pending_payments.html", {"pending": pending})

def verify_payment(request, pay_id):
    try:
        pay = PaymentRequest.objects.get(id=pay_id)

        # 1) Mark payment as success
        pay.status = "success"
        pay.save()

        # 2) Create new user account automatically
        user = User.objects.create_user(
            username = pay.buyer_email,
            email = pay.buyer_email,
            password = "123456"
        )

        # 3) Create profile for new user
        new_profile = Profile.objects.create(
            user = user,
            phone = pay.buyer_phone,
            state = "Unknown",
            referral_code = pay.referral_code_used,
            purchased_package = pay.package_name,
            wallet_balance = 0
        )

        # 4) Give commission to seller if exists
        if pay.seller:
            seller_profile = Profile.objects.get(user=pay.seller)
            commission = float(pay.amount) * 0.70
            seller_profile.wallet_balance += commission
            seller_profile.save()

        # 5) Update leaderboard points
        if pay.seller:
            seller_profile.leaderboard_points += float(pay.amount)
            seller_profile.save()

    except Exception as e:
        print("Payment Verify Error:", e)

    return redirect("seller_pending_payments")

def reject_payment(request, pay_id):
    try:
        pay = PaymentRequest.objects.get(id=pay_id)
        pay.status = "failed"
        pay.save()
    except:
        pass

    return redirect("seller_pending_payments")

def payment_status(request, pay_id):
    from .models import PaymentRequest

    try:
        pay = PaymentRequest.objects.get(id=pay_id)
    except PaymentRequest.DoesNotExist:
        return render(request, "error.html", {"msg": "Payment Not Found"})

    return render(request, "payment_status.html", {"pay": pay})

from django.shortcuts import render

def payment_success(request):
    return render(request, "payment_success.html")

def payment_failed(request):
    return render(request, "payment_failed.html")



from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile

# Manual ID secret
MANUAL_ID_SECRET = "THRIVEON-9999"


@staff_member_required
def manual_id_form(request):
    """
    STEP 0:
    Sirf manual ID form dikhao
    """
    return render(request, "manual_id_form.html")


@staff_member_required
def manual_id_create(request):
    """
    STEP 1: Secret code verify
    STEP 2: Manual ID create
    """

    # ---------- STEP 1 : SECRET VERIFY ----------
    if not request.session.get("manual_id_verified"):

        if request.method == "POST" and "secret_code" in request.POST:
            entered = request.POST.get("secret_code")

            if entered == MANUAL_ID_SECRET:
                request.session["manual_id_verified"] = True
                return redirect("manual_id_form")
            else:
                return render(
                    request,
                    "enter_secret.html",
                    {"error": "Galat secret code hai"}
                )

        return render(request, "enter_secret.html")

    # ---------- STEP 2 : MANUAL ID CREATE ----------
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        state = request.POST.get("state")
        sponsor = request.POST.get("sponsor")
        package = request.POST.get("package")

        # Same email check
        if User.objects.filter(username=email).exists():
            return render(
                request,
                "manual_id_form.html",
                {"error": "Is email se user already bana hua hai."}
            )

        # User create
        user = User.objects.create_user(
            username=email,
            email=email,
            password="123456"
        )

        # Profile create
        Profile.objects.create(
            user=user,
            phone=phone,
            state=state,
            sponsor_code=sponsor,
            package=package
        )

        return render(
            request,
            "manual_id_form.html",
            {"success": "Manual ID successfully created"}
        )

    # GET request
    return render(request, "manual_id_form.html")
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import models
from .models import RegistrationRequest

def registration_request_list(request):
    q = request.GET.get("q", "")
    status = request.GET.get("status", "")

    qs = RegistrationRequest.objects.all().order_by("-created_at")

    if q:
        qs = qs.filter(
            models.Q(name__icontains=q) |
            models.Q(email__icontains=q) |
            models.Q(phone__icontains=q)
        )

    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 10)
    page = request.GET.get("page")
    objects = paginator.get_page(page)

    return render(request, "home/registration_request.html", {
        "requests": objects,
        "q": q,
        "status": status,
    })


def registration_request_detail(request, pk):
    r = get_object_or_404(RegistrationRequest, pk=pk)

    return JsonResponse({
        "name": r.name,
        "email": r.email,
        "phone": r.phone,
        "state": r.state,
        "plan": r.plan,
        "amount": str(r.amount),
        "status": r.status,
        "created_at": r.created_at.strftime("%Y-%m-%d %H:%M"),
        "notes": r.notes or "",
    })


@require_POST
def registration_request_create(request):
    name = request.POST.get("name", "User")
    RegistrationRequest.objects.create(name=name)
    return redirect("home:registration_request_list")



# file: home/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db.models import Sum
from .models import UpgradeRequest

def upgrade_request_list(request):
    # filters (optional)
    q = request.GET.get("q", "")
    status = request.GET.get("status", "")

    qs = UpgradeRequest.objects.all().order_by("-created_at")
    if q:
        qs = qs.filter(
            models.Q(name__icontains=q) |
            models.Q(email__icontains=q) |
            models.Q(phone__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)

    # wallet balance example: sum of successful amounts (you can replace logic)
    wallet_balance = UpgradeRequest.objects.filter(status='success').aggregate(total=Sum('amount'))['total'] or 0

    # pagination optional: can add Paginator later
    return render(request, "home/upgrade_request.html", {
        "requests": qs,
        "wallet_balance": wallet_balance,
        "q": q,
        "status": status,
    })


def upgrade_request_detail(request, pk):
    r = get_object_or_404(UpgradeRequest, pk=pk)
    return JsonResponse({
        "id": r.id,
        "name": r.name,
        "email": r.email,
        "phone": r.phone,
        "plan": r.plan,
        "amount": str(r.amount),
        "status": r.status,
        "created_at": r.created_at.strftime("%Y-%m-%d %H:%M"),
        "notes": r.notes or "",
    })


@require_POST
def upgrade_request_create(request):
    name = request.POST.get("name", "User")
    email = request.POST.get("email")
    phone = request.POST.get("phone")
    plan = request.POST.get("plan")
    amount = request.POST.get("amount") or 0
    UpgradeRequest.objects.create(
        name=name, email=email, phone=phone, plan=plan, amount=amount
    )
    return redirect("home:upgrade_request_list")


@require_POST
def upgrade_request_approve(request, pk):
    r = get_object_or_404(UpgradeRequest, pk=pk)
    r.status = 'success'
    r.save()
    return JsonResponse({"ok": True, "status": r.status})


@require_POST
def upgrade_request_reject(request, pk):
    r = get_object_or_404(UpgradeRequest, pk=pk)
    r.status = 'failed'
    r.save()
    return JsonResponse({"ok": True, "status": r.status})


# file: home/views.py
from django.shortcuts import render
from django.db.models import Sum, Q
from .models import WalletTransaction

def wallet_transaction_list(request):
    # optional filters
    q = request.GET.get("q", "")
    tx_type = request.GET.get("tx_type", "")

    qs = WalletTransaction.objects.all().order_by("-created_at")
    if q:
        qs = qs.filter(Q(source__icontains=q))
    if tx_type:
        qs = qs.filter(tx_type=tx_type)

    # compute total wallet balance: credits - debits
    total_credits = WalletTransaction.objects.filter(tx_type='credit').aggregate(total=Sum('amount'))['total'] or 0
    total_debits = WalletTransaction.objects.filter(tx_type='debit').aggregate(total=Sum('amount'))['total'] or 0
    total_wallet = total_credits - total_debits

    total_withdrawal = total_debits

    return render(request, "home/wallet_transaction.html", {
        "transactions": qs,
        "total_wallet": total_wallet,
        "total_withdrawal": total_withdrawal,
        "q": q,
        "tx_type": tx_type,
    })

from django.contrib.auth.models import AnonymousUser

def my_associate_list(request):
    # Agar user login nahi hai → blank data show karo
    if isinstance(request.user, AnonymousUser):
        qs = []
    else:
        qs = Associate.objects.filter(owner=request.user).order_by('-joined_at')

    # optional filters
    q = request.GET.get('q', '')
    course = request.GET.get('course', '')

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q))

    if course:
        qs = qs.filter(course_name__icontains=course)

    return render(request, "home/my_associate.html", {
        "associates": qs,
        "q": q,
        "course": course,
    })


# home/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# NOTE: change this import if your model name / location is different
# You showed earlier an Associate model; if you have a Referral model, import that instead.
from .models import Associate

@login_required
def referrals_list(request):
    """
    Referrals list (premium table).
    Adjust the queryset below according to your model/field names:
      - If you store referrals in Associate model where 'sponsor' is the current user:
          qs = Associate.objects.filter(sponsor=request.user)
      - If you store referrals in Associate model where 'owner' is current user:
          qs = Associate.objects.filter(owner=request.user)
    """
    # Basic queryset (change filter field as needed)
    try:
        qs = Associate.objects.filter(sponsor=request.user).order_by('-joined_at')
    except Exception:
        # fallback if 'sponsor' doesn't exist, try owner
        qs = Associate.objects.filter(owner=request.user).order_by('-joined_at')

    # optional search (q param)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            # use fields available in your model; adjust if different
            name__icontains=q
        )

    # pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(qs, 15)
    try:
        associates = paginator.page(page)
    except PageNotAnInteger:
        associates = paginator.page(1)
    except EmptyPage:
        associates = paginator.page(paginator.num_pages)

    context = {
        "associates": associates,
        "q": q,
    }
    return render(request, "home/referrals.html", context)




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import WithdrawalRequest

@login_required
def withdrawal_request_list(request):
    # User ka balance yaha se aayega
    wallet_balance = request.user.wallet_balance if hasattr(request.user, 'wallet_balance') else 0

    # POST = Form submitted
    if request.method == "POST":
        amount = int(request.POST.get("amount"))

        # Balance check
        if amount > wallet_balance:
            messages.error(request, "Insufficient Balance!")
        else:
            WithdrawalRequest.objects.create(
                user=request.user,
                amount=amount,
                status="pending",
            )
            messages.success(request, "Withdrawal Request Submitted Successfully!")

        return redirect("withdrawal_request")

    # Withdrawal list
    qs = WithdrawalRequest.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "home/withdrawal_request.html", {
        "requests_list": qs,
        "wallet_balance": wallet_balance,
    })
