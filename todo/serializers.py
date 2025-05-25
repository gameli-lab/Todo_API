from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ['fullname', 'phone', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
                fullname = validated_data['fullname'],
                phone = validated_data['phone'],
                email = validated_data['email'],
                password = validated_data['password']
                )
        return user
