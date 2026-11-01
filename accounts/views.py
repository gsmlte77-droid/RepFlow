"""
Accounts views for FixSoftRepair
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
import json

from .forms import LoginForm, UserRegistrationForm, UserUpdateForm, PasswordChangeCustomForm
from .models import User


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_admin()


def login_view(request):
    """Login view with AJAX support"""
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
                remember_me = data.get('remember_me', False)
                
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    login(request, user)
                    if not remember_me:
                        request.session.set_expiry(0)  # Session expires on browser close
                    return JsonResponse({
                        'success': True,
                        'redirect': '/dashboard/'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'errors': [_('Invalid username or password')]
                    }, status=401)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'errors': [_('Invalid request format')]
                }, status=400)
        else:
            # Regular form submission
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)
                messages.success(request, _('Login successful!'))
                return redirect('dashboard:home')
            else:
                for error in form.errors.values():
                    messages.error(request, error[0])
    else:
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
@require_POST
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.info(request, _('You have been logged out.'))
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile updated successfully!'))
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def password_change_view(request):
    """Password change view"""
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Password changed successfully!'))
            return redirect('accounts:profile')
    else:
        form = PasswordChangeCustomForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})


@user_passes_test(is_admin)
@login_required
def user_list_view(request):
    """List all users (admin only)"""
    users = User.objects.all().order_by('-date_created')
    return render(request, 'accounts/user_list.html', {'users': users})


@user_passes_test(is_admin)
@login_required
def user_create_view(request):
    """Create new user (admin only)"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, _('User created successfully!'))
            return redirect('accounts:user_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/user_form.html', {'form': form})


@user_passes_test(is_admin)
@login_required
def user_update_view(request, pk):
    """Update user (admin only)"""
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _('User updated successfully!'))
            return redirect('accounts:user_list')
    else:
        form = UserUpdateForm(instance=user)
    
    return render(request, 'accounts/user_form.html', {'form': form, 'user': user})


@user_passes_test(is_admin)
@login_required
@require_POST
def user_delete_view(request, pk):
    """Delete user (admin only)"""
    user = User.objects.get(pk=pk)
    if request.user == user:
        messages.error(request, _('You cannot delete your own account!'))
    else:
        user.delete()
        messages.success(request, _('User deleted successfully!'))
    return redirect('accounts:user_list')


# API Views for AJAX
@csrf_exempt
def check_username_availability(request):
    """Check if username is available"""
    if request.method == 'GET':
        username = request.GET.get('username', '')
        if User.objects.filter(username=username).exists():
            return JsonResponse({'available': False})
        return JsonResponse({'available': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)
