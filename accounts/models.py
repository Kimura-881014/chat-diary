from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, user_id, email, password, **extra_fields):
        if not email:
            email = ""
        else:
            email = self.normalize_email(email)
        # username = self.model.normalize_username(username)
        user = self.model(user_id=user_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user
    def create_user(self, user_id,email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(user_id, email,password, **extra_fields)

    def create_superuser(self, user_id, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('is_staff=Trueである必要があります。')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser=Trueである必要があります。')
        return self._create_user(user_id, email, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()


    user_id = models.CharField(_("user_id"),max_length=30,unique=True)
    username = models.CharField(_("username"), max_length=50, validators=[username_validator], blank=True)
    email = models.EmailField(_("email_address"), blank=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    is_active = models.BooleanField(_("active"), default=True)
    is_manager = models.CharField(_("manager_number"),max_length=100,blank=True)
    chat_type = models.CharField(_("chattype"),max_length=100,default="[1,2]")
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()
    USERNAME_FIELD = "user_id" # ログインのときに必要なfield
    EMAIL_FIELD = ["email"] # email形式にしたいところ
    REQUIRED_FIELDS = ["email"] # createsuperuserで求めるfiled

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

