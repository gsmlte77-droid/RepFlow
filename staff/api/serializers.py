"""
Staff API serializers
"""
from rest_framework import serializers
from accounts.api.serializers import UserSerializer
from ..models import StaffMember


class StaffMemberSerializer(serializers.ModelSerializer):
    """Staff member serializer"""
    
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = StaffMember
        fields = [
            'id', 'user', 'user_id', 'employee_id', 'telephone', 'address', 
            'city', 'postal_code', 'department', 'position', 'employment_status',
            'hire_date', 'termination_date', 'salary', 'commission_rate', 
            'skills', 'specialties', 'work_schedule', 'performance_rating', 
            'notes', 'is_active', 'date_created', 'date_updated'
        ]
        read_only_fields = ['date_created', 'date_updated']


class StaffMemberListSerializer(serializers.ModelSerializer):
    """Simplified staff member serializer for lists"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = StaffMember
        fields = [
            'id', 'user', 'employee_id', 'telephone', 'department', 
            'position', 'employment_status', 'hire_date', 'is_active',
            'performance_rating', 'date_created'
        ]


class StaffMemberSimpleSerializer(serializers.ModelSerializer):
    """Minimal staff member serializer for dropdowns"""
    
    class Meta:
        model = StaffMember
        fields = ['id', 'employee_id', 'position']
        extra_kwargs = {
            'employee_id': {'required': False},
            'position': {'required': False}
        }
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.get_full_name(),
            'employee_id': instance.employee_id,
            'position': instance.position,
            'department': instance.get_department_display()
        }
