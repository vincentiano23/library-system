from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from .models import Visit, Student
from django.utils import timezone
from django.db.models import Count
from .forms import RegistrationForm
from django.contrib.auth import logout
from django.contrib import messages
from .models import NewsletterSubscriber
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def home(request):
    return render(request, 'library/home.html')

def dashboard(request):
    if request.user.is_authenticated:
        # Check if the user is a student
        if hasattr(request.user, 'student'):
            visits = Visit.objects.filter(student=request.user.student)
            total_visits = visits.count()
            total_days = 30  # You can adjust this as needed
            visit_percentage = (total_visits / total_days) * 100 if total_days > 0 else 0

            return render(request, 'library/dashboard.html', {
                'total_visits': total_visits,
                'visit_percentage': round(visit_percentage, 2),
                'visits': visits,
            })
        else:
            messages.error(request, "You do not have access to this dashboard.")
            return redirect('home')  # Redirect to a safe page if the user is not a student

    messages.error(request, "You must be logged in to access the dashboard.")
    return redirect('login')

def admin_dashboard(request):
    if request.user.is_authenticated and request.user.is_staff:
        visits = Visit.objects.values('student__registration_number').annotate(total_visits=Count('id'))

        if not visits:
            messages.info(request, "No visits recorded yet.")
        
        return render(request, 'library/admin_dashboard.html', {'visits': visits})
    
    messages.error(request, "You do not have permission to access this page.")
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            username = form.cleaned_data['registration_number'] if role == 'student' else form.cleaned_data['email']

            # Check if the username or email already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "This username is already taken. Please choose another.")
                return render(request, 'library/register.html', {'form': form})

            if role == 'student':
                # Check if the registration number already exists
                if Student.objects.filter(registration_number=form.cleaned_data['registration_number']).exists():
                    messages.error(request, "This registration number is already registered. Please use a different one.")
                    return render(request, 'library/register.html', {'form': form})

            # Create the user
            user = User.objects.create_user(
                username=username,
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email'],
            )

            if role == 'admin':
                user.is_staff = True  # Admins get staff permission
                user.save()
                messages.success(request, "Admin registration successful!")
                return redirect('login')  # Redirect to login page after successful registration

            # If registering as a student, create a Student instance
            Student.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                registration_number=form.cleaned_data['registration_number']
            )

            messages.success(request, "Student registration successful!")
            return redirect('login')  # Redirect to login page after successful registration
        else:
            messages.error(request, "Registration failed. Please check the form fields.")
    else:
        form = RegistrationForm()

    return render(request, 'library/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        password = request.POST.get('password')

        if role == 'student':
            registration_number = request.POST.get('registration_number')

            try:
                student = Student.objects.get(registration_number=registration_number)
                username = student.user.username  # Use associated user account
            except Student.DoesNotExist:
                messages.error(request, "Invalid registration number.")
                return redirect('login')

        else:
            # Admin login: use input from the 'username' field
            username = request.POST.get('username')


        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            if role == 'student' and hasattr(user, 'student'):
                messages.success(request, "Login successful! Welcome to your dashboard.")
                return redirect('dashboard')

            elif role == 'admin' and (user.is_staff or user.is_superuser):  # ✅ Include superuser check
                messages.success(request, "Login successful! Welcome to the admin dashboard.")
                return redirect('admin_dashboard')

            else:
                messages.error(request, "You do not have permission to access this page.")
        else:
            messages.error(request, "Invalid credentials. Please try again.")
        return redirect('login')

    return render(request, 'library/login.html')
    
def user_logout(request):
    logout(request)
    return redirect('home')

def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if email:
            try:
                validate_email(email)  # Validate email format

                if not NewsletterSubscriber.objects.filter(email=email).exists():
                    NewsletterSubscriber.objects.create(email=email)
                    send_mail(
                        subject="Library Newsletter Subscription",
                        message="Thank you for subscribing to the University Library newsletter!",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )

                    messages.success(request, "Subscription successful! A confirmation email has been sent.")
                    return redirect("thank_you")  # Redirect to a thank-you page
                else:
                    messages.warning(request, "You are already subscribed.")
            except ValidationError:
                messages.error(request, "Invalid email address.")

    return redirect("home")