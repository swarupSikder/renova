from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply common widget attributes
        common_attrs = {
            'class': 'form-input w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-400',
        }

        # Add placeholders and apply attributes
        placeholders = {
            'username': 'Username',
            'email': 'Email address',
            'first_name': 'First name',
            'last_name': 'Last name',
            'password1': 'Password',
            'password2': 'Confirm password',
        }

        for field_name, field in self.fields.items():
            field.widget.attrs.update(common_attrs)
            field.widget.attrs['placeholder'] = placeholders.get(field_name, '')