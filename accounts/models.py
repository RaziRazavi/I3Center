from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from accounts.manager import UserManager
from accounts.model_field_validation import otp_code_validation
from utility.inheritance import BaseModel


class User(AbstractBaseUser, BaseModel, PermissionsMixin):  # inherits from 3 different classes
    phone_number = models.CharField(unique=True, max_length=15, verbose_name='شماره تماس')
    email = models.EmailField(unique=True, max_length=255, verbose_name='ایمیل')
    first_name = models.CharField(max_length=100, verbose_name='اسم')
    last_name = models.CharField(max_length=100, verbose_name='فامیل')
    state = models.CharField(max_length=100, verbose_name='استان')
    city = models.CharField(max_length=100, verbose_name='شهر')
    address = models.TextField(verbose_name='آدرس')
    zip_code = models.CharField(max_length=15, verbose_name='کد پستی')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_staff = models.BooleanField(default=False, verbose_name='ادمین')
    is_superuser = models.BooleanField(default=False, verbose_name='سوپر ادمین')

    class Meta:  # configures metadata
        db_table = 'کاربر'  # human-readable singular name
        verbose_name_plural = 'کاربران'  # human-readable plural name
        ordering = ('phone_number',)  # sorts data in table based on phone_number

    objects = UserManager()   # because of hash password we use custom manager

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ('email', 'password', 'first_name', 'last_name', 'state', 'city', 'address', 'zip_code')

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.phone_number

    def has_perm(self, perm, obj=None):  # if user has permissions to access some to admin panel
        return True

    def has_module_perms(self, app_label):  # if user has permissions to access some modules
        return True

    @property
    def get_full_name(self):  # gets full name of user
        return f'{self.first_name} - {self.last_name}'


class OtpCode(BaseModel):  # holds one time
    phone_number = models.CharField(unique=True, max_length=15, verbose_name='شاره تماس')
    code = models.PositiveIntegerField(unique=True, validators=[otp_code_validation,], verbose_name='کد')

    class Meta:  # configures metadata
        db_table = 'کد یکبار مصرف'  # human-readable singular name
        verbose_name_plural = 'کدهای یکبار مصرف'  # human-readable plural name
        ordering = ('phone_number',)  # sorts data in table based on phone_number

    def __str__(self):  # gets human-readable string when the object is called or printed
        return f'{self.phone_number} - {self.code}'
