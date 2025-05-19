from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, fullname, phone, email, password=None):
        if not email:
            raise ValueError("Users must have an email")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, fullname, phone, email, password=None):
        user = self.create_user(fullname, phone, email, password = password)
        user.is_admin = True
        user.save(using = self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    fullname = models.CharField(max_length = 20)
    phone = models.CharField(max_length = 20)
    email = models.EmailField(unique = True)
    is_active = models.BooleanField(default = True)
    is_admin = models.BooleanField(default = False)

    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj = None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class TodoItems(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    completed = models.BooleanField(default = False)

    def __str__(self):
        return self.title


