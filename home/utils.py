# home/utils.py

def calculate_commission(package_price):
    """
    Seller ko kitna commission milega?
    Rule: 70% of seller active package price.
    Example: 999 -> 699
    """
    try:
        return int(round(package_price * 0.70))
    except Exception:
        return 0



from django.db import models
from .models import WalletTransaction


def get_withdrawable_balance(user):
    # Total earned amount
    total_credits = WalletTransaction.objects.filter(
        user=user, tx_type="credit"
    ).aggregate(total=models.Sum("amount"))["total"] or 0

    # Total amount withdrawn
    total_debits = WalletTransaction.objects.filter(
        user=user, tx_type="debit"
    ).aggregate(total=models.Sum("amount"))["total"] or 0

    # Balance = Earnings - Withdrawals
    return total_credits - total_debits