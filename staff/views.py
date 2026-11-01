"""
Staff views for FixSoftRepair
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.http import JsonResponse

from accounts.models import User
from .models import StaffMember
from .forms import StaffMemberForm, StaffSearchForm


def is_admin_or_manager(user):
    """Check if user is admin or has management privileges"""
    return user.is_authenticated and (user.is_admin() or user.role == User.Role.ADMIN)


@login_required
def staff_list_view(request):
    """List all staff members"""
    form = StaffSearchForm(request.GET or None)
    
    staff_members = StaffMember.objects.select_related('user').all()
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        department = form.cleaned_data.get('department')
        employment_status = form.cleaned_data.get('employment_status')
        is_active = form.cleaned_data.get('is_active')
        
        if search:
            staff_members = staff_members.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(position__icontains=search)
            )
        
        if department:
            staff_members = staff_members.filter(department=department)
        
        if employment_status:
            staff_members = staff_members.filter(employment_status=employment_status)
        
        if is_active is not None:
            staff_members = staff_members.filter(is_active=is_active)
    
    staff_members = staff_members.order_by('-date_created')
    
    return render(request, 'staff/staff_list.html', {
        'staff_members': staff_members,
        'form': form
    })


@login_required
@user_passes_test(is_admin_or_manager)
def staff_create_view(request):
    """Create new staff member"""
    if request.method == 'POST':
        form = StaffMemberForm(request.POST)
        if form.is_valid():
            staff_member = form.save()
            messages.success(request, _('Staff member created successfully!'))
            return redirect('staff:staff_list')
    else:
        form = StaffMemberForm()
    
    return render(request, 'staff/staff_form.html', {'form': form})


@login_required
@user_passes_test(is_admin_or_manager)
def staff_update_view(request, pk):
    """Update staff member"""
    staff_member = get_object_or_404(StaffMember, pk=pk)
    
    if request.method == 'POST':
        form = StaffMemberForm(request.POST, instance=staff_member)
        if form.is_valid():
            form.save()
            messages.success(request, _('Staff member updated successfully!'))
            return redirect('staff:staff_list')
    else:
        form = StaffMemberForm(instance=staff_member)
    
    return render(request, 'staff/staff_form.html', {
        'form': form,
        'staff_member': staff_member
    })


@login_required
@user_passes_test(is_admin_or_manager)
@user_passes_test(is_admin_or_manager)
def staff_delete_view(request, pk):
    """Delete staff member"""
    staff_member = get_object_or_404(StaffMember, pk=pk)
    
    if request.method == 'POST':
        # Don't actually delete, just deactivate
        staff_member.is_active = False
        staff_member.save()
        messages.success(request, _('Staff member deactivated successfully!'))
        return redirect('staff:staff_list')
    
    return render(request, 'staff/staff_confirm_delete.html', {'staff_member': staff_member})


@login_required
def staff_profile_view(request, pk):
    """View staff member profile"""
    staff_member = get_object_or_404(StaffMember, pk=pk)
    
    # Check if user can view this profile
    if not request.user.is_admin() and request.user != staff_member.user:
        messages.error(request, _('You do not have permission to view this profile.'))
        return redirect('staff:staff_list')
    
    return render(request, 'staff/staff_profile.html', {'staff_member': staff_member})


# AJAX Views
@login_required
def get_staff_by_department(request, department):
    """Get staff members by department (AJAX)"""
    staff_members = StaffMember.objects.filter(
        department=department,
        is_active=True
    ).select_related('user').order_by('user__first_name')
    
    data = [{
        'id': sm.id,
        'name': sm.get_full_name(),
        'employee_id': sm.employee_id,
        'position': sm.position
    } for sm in staff_members]
    
    return JsonResponse(data, safe=False)


@login_required
def get_staff_stats(request):
    """Get staff statistics (AJAX)"""
    from django.db.models import Count
    
    stats = {
        'total': StaffMember.objects.count(),
        'active': StaffMember.objects.filter(is_active=True).count(),
        'by_department': list(StaffMember.objects.values('department').annotate(count=Count('id')).order_by('department')),
        'by_status': list(StaffMember.objects.values('employment_status').annotate(count=Count('id')).order_by('employment_status')),
    }
    
    return JsonResponse(stats)
