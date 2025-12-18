from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Car, Enquiry, Profile, Wishlist, EnquiryReply


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        exclude = ['dealer']


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['name', 'email', 'phone', 'message']

class RegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('dealer', 'Dealer'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user   # ❌ DO NOT create Profile here

from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }
class EnquiryReplyForm(forms.ModelForm):
    class Meta:
        model = EnquiryReply
        fields = ['message']
from django import forms
from .models import DealerReview

class DealerReviewForm(forms.ModelForm):
    class Meta:
        model = DealerReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this dealer'
            })
        }

from .models import DealerProfile
from django import forms
class DealerProfileForm(forms.ModelForm):
    class Meta:
        model = DealerProfile
        fields = (
            'company_name',
            'about',
            'gst_number',
            'gst_document',
            'id_document',
        )
        class Meta:
            model = DealerProfile
            exclude = ('user', 'is_verified', 'created_at')
