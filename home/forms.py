from django import forms
from .models import KYC

class KYCForm(forms.ModelForm):
    class Meta:
        model = KYC
        fields = '__all__'
        exclude = ['user']

        widgets = {
            'bank_type': forms.Select(attrs={'class': 'input'}),
            'bank_name': forms.TextInput(attrs={'class': 'input'}),
            'holder_name': forms.TextInput(attrs={'class': 'input'}),
            'ifsc_code': forms.TextInput(attrs={'class': 'input'}),
            'account_number': forms.TextInput(attrs={'class': 'input'}),
            'upi_id': forms.TextInput(attrs={'class': 'input'}),
        }


from django import forms
from django.contrib.auth.models import User
from .models import Profile

class ManualIDForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    state = forms.CharField(max_length=50)
    sponsor_code = forms.CharField(max_length=50, required=False)
    package_name = forms.CharField(max_length=50)