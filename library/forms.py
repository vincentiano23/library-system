from django import forms
from django.contrib.auth.models import User
from .models import Student

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    role = forms.ChoiceField(choices=[('student', 'Student'), ('admin', 'Admin')], required=True, label="Register As")

    class Meta:
        model = Student
        fields = ['full_name', 'registration_number', 'email']
        labels = {
            'full_name': 'Full Name',
            'registration_number': 'Registration Number',
            'email': 'Email Address',
        }

    def clean_registration_number(self):
        registration_number = self.cleaned_data.get('registration_number')
        if User.objects.filter(username=registration_number).exists():
            raise forms.ValidationError("This registration number is already taken.")
        return registration_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        # Create the User object first
        user = User.objects.create_user(
            username=self.cleaned_data['registration_number'],  
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )

        # Create the Student object
        student = super().save(commit=False)
        student.user = user
        
        # If the user is an admin, grant admin privileges
        if self.cleaned_data['role'] == 'admin':
            user.is_staff = True
            user.save()

        if commit:
            student.save()
        
        return student