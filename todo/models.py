from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

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


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default = 'pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_changed_at = models.DateTimeField(null=True, blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name= 'tasks')


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_task = Task.objects.get(pk=self.pk)
            if old_task.status != self.status:
                self.status_changed_at = timezone.now()
            else:
                self.status_changed_at = timezone.now()

            super().save(*args, **kwargs)
