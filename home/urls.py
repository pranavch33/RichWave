

from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),

    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('affiliate-dashboard/', views.affiliate_dashboard, name='affiliate_dashboard'),

    #  NEW: Profile Page Route
    path('profile/', views.profile_page, name='profile'),

    # (Optional) Profile Update Route
    path('profile/update/', views.update_profile, name='update_profile'),
    #  NEW – KYC PAGE
    path('kyc/', views.kyc_page, name='kyc'),
    path("affiliate-link/", views.affiliate_link, name="affiliate_link"),
    path("my-courses/", views.my_courses, name="my_courses"),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path("checkout/<slug:slug>/", views.checkout, name="checkout"),
    path("buy/<str:package_name>/", views.payment_checkout, name="payment_checkout"),
    path("payment-waiting/<int:payment_id>/", views.payment_waiting, name="payment_waiting"),
    path("seller/pending-payments/", views.seller_pending_payments, name="seller_pending_payments"),
    path("verify-payment/<int:pay_id>/", views.verify_payment, name="verify_payment"),
    path('payment-status/<int:pay_id>/', views.payment_status, name='payment_status'),
    path("reject-payment/<int:pay_id>/", views.reject_payment, name="reject_payment"),
    path("verify-payment/", views.verify_payment, name="verify_payment"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/failed/", views.payment_failed, name="payment_failed"),
    path("manual-id/", views.manual_id_form, name="manual_id_form"),
    path("manual-id-create/", views.manual_id_create, name="manual_id_create"),
    path("registration-request/", views.registration_request_list, name="registration_request_list"),
    path("registration-request/<int:pk>/", views.registration_request_detail, name="registration_request_detail"),
    path("registration-request/create/", views.registration_request_create, name="registration_request_create"),
    path("upgrade-request/", views.upgrade_request_list, name="upgrade_request_list"),
    path("upgrade-request/create/", views.upgrade_request_create, name="upgrade_request_create"),
    path("upgrade-request/<int:pk>/", views.upgrade_request_detail, name="upgrade_request_detail"),
    path("upgrade-request/<int:pk>/approve/", views.upgrade_request_approve, name="upgrade_request_approve"),
    path("upgrade-request/<int:pk>/reject/", views.upgrade_request_reject, name="upgrade_request_reject"),
    path("wallet-transaction/", views.wallet_transaction_list, name="wallet_transaction"),
    path("my-associate/", views.my_associate_list, name="my_associate"),
    path('referrals/', views.referrals_list, name='referrals'),
    path("withdrawal-request/", views.withdrawal_request_list, name="withdrawal_request"),
           ]


 

