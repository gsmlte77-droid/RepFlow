"""
Accounts API serializers
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'telephone', 
                 'role', 'is_active', 'date_created', 'date_updated', 'avatar']
        read_only_fields = ['date_created', 'date_updated']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Simplified user serializer for lists"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'get_full_name', 'email', 'telephone', 
                 'get_role_display', 'is_active', 'date_created']


class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    remember_me = serializers.BooleanField(default=False, required=False)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError(
                        _('User account is disabled.')
                    )
                attrs['user'] = user
            else:
                raise serializers.ValidationError(
                    _('Unable to log in with provided credentials.')
                )
        else:
            raise serializers.ValidationError(
                _('Must include "username" and "password".')
            )
        
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    new_password1 = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    new_password2 = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    def validate(self, attrs):
        user = self.context.get('request').user
        
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError(
                {'old_password': _('Your old password was entered incorrectly. Please enter it again.')}
            )
        
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {'new_password2': _('The two password fields did not match.')}
            )
        
        # Validate password strength
        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(attrs['new_password1'], user)
        except ValidationError as e:
            raise serializers.ValidationError({'new_password1': list(e.messages)})
        
        return attrs


class CheckUsernameSerializer(serializers.Serializer):
    """Check username availability serializer"""
    
    username = serializers.CharField()
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(_('Username already exists.'))
        return value
