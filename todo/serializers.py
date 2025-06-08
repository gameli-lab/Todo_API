from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Task
from django.utils import timezone

class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)
    confirm_password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ['fullname', 'phone', 'email', 'password', 'confirm_password']
    extra_kwargs = {
        'fullname': {'required': True},
        'phone': {'required': True},
        'email': {'required': True, 'allow_blank': False},
    }

    def validate_empty_values(self, data):
        errors = {}
        if not data.get('email'):
            errors['email'] = ['This field may not be blank.']
        if not data.get('password'):
            errors['password'] = ['This field may not be blank.']
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return super().validate_empty_values(data)

    def validate_email(self, value):
        """Check if the email is already registered."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value
    
    def validate_phone(self, value):
        """Check if the phone number is already registered."""
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number is already registered.")
        return value
    
    def validate (self, data):
        """Check if password and confirm_password match."""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    
    def create(self, validated_data):
        user = User.objects.create_user(
                fullname = validated_data['fullname'],
                phone = validated_data['phone'],
                email = validated_data['email'],
                password = validated_data['password']
                )
        return user

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'status', 'created_at', 'updated_at', 'status_changed_at', 'user']
        read_only_fields = ['id', 'created_at', 'updated_at', 'status_changed_at', 'user']

    def validate_title(self, value):
        """Check if the title is not empty."""
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value
        
    def validate_due_date(self, value):
        """ Check if the due date is in the future."""
        try:
            if value < timezone.now().date():
                raise serializers.ValidationError("""Due date cannot be in the past.""")
        except TypeError:
            raise serializers.ValidationError("Due date must be a valid date.")
        return value

class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']

    def validate_status(self, value):
        """check if status is validated"""
        valid_statuses = [status[0] for status in Task.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"status must be one of: {', '.join(valid_statuses)}")
        return value