"""
Staff API views
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Count
from accounts.models import User
from .serializers import (
    StaffMemberSerializer, StaffMemberListSerializer, 
    StaffMemberSimpleSerializer
)
from ..models import StaffMember


class StaffMemberViewSet(viewsets.ModelViewSet):
    """Staff member CRUD operations"""
    
    queryset = StaffMember.objects.select_related('user').all()
    serializer_class = StaffMemberSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StaffMemberListSerializer
        return StaffMemberSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAdminUser()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department=department)
        
        # Filter by employment status
        employment_status = self.request.query_params.get('employment_status')
        if employment_status:
            queryset = queryset.filter(employment_status=employment_status)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(position__icontains=search)
            )
        
        return queryset.order_by('-date_created')
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active staff members"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def technicians(self, request):
        """Get only technicians"""
        queryset = self.get_queryset().filter(
            is_active=True,
            department=StaffMember.Department.TECHNICAL
        )
        serializer = StaffMemberSimpleSerializer(queryset, many=True)
        return Response(serializer.data)


class StaffByDepartmentView(APIView):
    """Get staff members by department"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, department):
        staff_members = StaffMember.objects.filter(
            department=department,
            is_active=True
        ).select_related('user').order_by('user__first_name')
        
        serializer = StaffMemberSimpleSerializer(staff_members, many=True)
        return Response(serializer.data)


class StaffStatsView(APIView):
    """Get staff statistics"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        stats = {
            'total': StaffMember.objects.count(),
            'active': StaffMember.objects.filter(is_active=True).count(),
            'by_department': list(
                StaffMember.objects.values('department').annotate(
                    count=Count('id')
                ).order_by('department')
            ),
            'by_status': list(
                StaffMember.objects.values('employment_status').annotate(
                    count=Count('id')
                ).order_by('employment_status')
            ),
            'by_performance': list(
                StaffMember.objects.exclude(performance_rating__isnull=True).values(
                    'performance_rating'
                ).annotate(count=Count('id')).order_by('performance_rating')
            ),
        }
        
        return Response(stats)
