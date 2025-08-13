from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

# - - - - - - - - - - #
#     Sign Up View    #
# - - - - - - - - - - #
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)  # Include files for profile picture
        if form.is_valid():
            user = form.save(commit=False)  # password is hashed by form
            user.is_active = False  # Require email activation
            user.save()
            messages.success(request, "A confirmation mail was sent. Please check your email.")
            return redirect('login')
        else:
            messages.error(request, "Form is not valid!")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

# - - - - - - - - - - - #
#     Activation View   #
# - - - - - - - - - - - #
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can now log in.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid or has expired.")
        return redirect('signup')

# - - - - - - - - - #
#     Login View    #
# - - - - - - - - - #
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Please activate your account before logging in.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "users/login.html")

# - - - - - - - - - - #
#     Logout View     #
# - - - - - - - - - - #
def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out.")
    return redirect('home')