from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import InvestmentListing

User = get_user_model()


class StyledFormMixin:
    def _apply_styles(self):
        for field_name, field in self.fields.items():
            widget = field.widget
            css_class = 'form-checkbox' if isinstance(widget, forms.CheckboxInput) else 'form-input'
            widget.attrs['class'] = css_class
            if field_name != 'password2':
                widget.attrs.setdefault('placeholder', field.label)


class SignUpForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styles()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class InvestmentListingForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = InvestmentListing
        fields = [
            'restaurant_name',
            'business_type',
            'location',
            'funding_goal',
            'equity_offer',
            'summary',
            'story',
            'use_of_funds',
            'target_timeline',
            'website',
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'story': forms.Textarea(attrs={'rows': 6}),
            'use_of_funds': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styles()
