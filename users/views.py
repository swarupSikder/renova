from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm

# - - - - - - - - - - #
#     Sign Up View    #
# - - - - - - - - - - #
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            messages.success(request, "Account created successfully! Welcome 🎉")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})  # Moved to users/signup.html


# - - - - - - - - - #
#     Login View    #
# - - - - - - - - - #
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'users/login.html')  # Moved to users/login.html


# - - - - - - - - - - #
#     Logout View     #
# - - - - - - - - - - #
def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out.")
    return redirect('home')