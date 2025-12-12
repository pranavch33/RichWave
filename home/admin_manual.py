from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Profile, Package

@staff_member_required
def manual_id_admin_view(request):
    packages = Package.objects.values_list("name", flat=True)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        state = request.POST.get("state")
        sponsor = request.POST.get("sponsor")
        package_name = request.POST.get("package")

        # Create User
        user = User.objects.create_user(username=email, email=email, password="123456")

        # Create Profile
        Profile.objects.create(
            user=user,
            phone=phone,
            state=state,
            referral_code=sponsor,
            purchased_package=package_name,
            wallet_balance=0
        )

        return render(request, "admin/manual_id_form.html", {
            "success": f"ID Created Successfully! Username: {email}, Password: 123456"
        })

    return render(request, "admin/manual_id_form.html", {"packages": packages})