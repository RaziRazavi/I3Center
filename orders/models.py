from django.utils import timezone
from utility.inheritance import BaseModel
from django.db import models
from django_jalali.db import models as jmodels
from products.model_field_validation import discount_validation, price_validation
from django.urls import reverse


class Order(BaseModel):
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='orders',
                             verbose_name='کاربر')
    phone_number = models.CharField(max_length=15, verbose_name='شماره تماس')
    email = models.EmailField(max_length=255, verbose_name='ایمیل')
    first_name = models.CharField(max_length=255, verbose_name='اسم')
    last_name = models.CharField(max_length=255, verbose_name='فامیل')
    state = models.CharField(max_length=255, verbose_name='استان')
    city = models.CharField(max_length=255, verbose_name='شهر')
    address = models.TextField(verbose_name='آدرس')
    zip_code = models.CharField(max_length=15, verbose_name='کد پستی')
    paid = models.BooleanField(default=False, verbose_name='پرداخت شده')
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True, related_name='orders',
                               verbose_name='کد تخفیف')
    base_price = models.PositiveIntegerField(null=True, blank=True, validators=[price_validation,], verbose_name='قیمت اولیه')
    discount = models.PositiveSmallIntegerField(default=0, validators=[discount_validation,], verbose_name='تخفیف')
    paid_price = models.PositiveIntegerField(null=True, blank=True, validators=[price_validation,], verbose_name='قیمت پرداخت')

    class Meta:  # configures metadata
        db_table = 'سفارش'  # human-readable singular name
        verbose_name_plural = 'سفارش ها'  # human-readable plural name
        ordering = ('-id',)  # sorts data in table based on id

    def __str__(self):  # gets human-readable string when the object is called or printed
        return str(self.phone_number)

    @property
    def order_current_total_price(self):  # calculates current total price of order
        return sum(item.order_item_total_price for item in self.order_items.all())

    @property
    def order_current_final_price(self):  # calculates current final price of order
        return self.order_current_total_price * (100 - self.discount) // 100

    def get_absolute_url(self):  # gets url of related view
        return reverse('orders:order_details', kwargs={'id':self.id})

    @property
    def is_paid(self):  # checks if order is paid and responds base on that
        return 'بله' if self.paid else 'خیر'


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name='سفارش')
    variant = models.ForeignKey('products.Variant', on_delete=models.SET_NULL, null=True, related_name='order_items',
                                verbose_name='متغیر')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, related_name='order_items',
                                verbose_name='محصول')
    price = models.PositiveIntegerField(null=True, blank=True, validators=[price_validation], verbose_name='قیمت')
    quantity = models.PositiveIntegerField(default=0, verbose_name='تعداد')

    class Meta:  # configures metadata
        db_table = 'آیتم سفارش'  # human-readable singular name
        verbose_name_plural = 'آیتم های سفارش'  # human-readable plural name
        ordering = ('-id',) # sorts data in table based on id

    def __str__(self):  # gets human-readable string when the object is called or printed
        return str(self.id)

    def save(self, *args, **kwargs):  # overrides save method
        if self.variant and not self.product:  # writes product field base on variant field if it is empty
            self.product = self.variant.product
        if self.variant and not self.price:  # if price field is empty, writes it base on variant field
            self.price = self.variant.final_price
        super().save(*args, **kwargs)

    @property
    def order_item_total_price(self):  # calculates orderItem's total price
        return self.price * self.quantity


class Coupon(BaseModel):
    code = models.CharField(max_length=255, unique=True, verbose_name='کد')
    discount = models.PositiveSmallIntegerField(default=0, validators=[discount_validation,], verbose_name='تخفیف')
    available = models.BooleanField(default=False, verbose_name='موجود')
    max_uses = models.PositiveIntegerField(default=0, verbose_name='حداکثر استفاده')
    times_used = models.PositiveIntegerField(default=0, verbose_name='تعداد استفاده')
    start_date = jmodels.jDateTimeField(verbose_name='تاریخ شروع')
    end_date = jmodels.jDateTimeField(verbose_name='تاریخ پایان')

    class Meta:  # configures metadata
        db_table = 'کد تخفیف'  # human-readable singular name
        verbose_name_plural = 'کدهای تخفیف'  # human-readable plural name
        ordering = ('code',)  # sorts data in table based on code

    def __str__(self):  # gets human-readable string when the object is called or printed
        return str(self.code)

    @property
    def is_valid(self):  # examines if coupon is valid base on some fields
        if not self.available:
            return False
        if self.discount == 0:
            return False
        if self.times_used >= self.max_uses:
            return False
        if not self.start_date.togregorian() <= timezone.now() <= self.end_date.togregorian():
            return False
        return True

    def is_valid_for(self, user):  # checks if coupon is valid for user
        if not self.is_valid:
            return False
        if self.coupon_usages.filter(user=user).exists():
            return False
        return True


class CouponUsage(BaseModel):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='coupon_usages', verbose_name='کد تخفیف')
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='coupon_usages',
                             verbose_name='کاربر')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name='coupon_usages',
                              verbose_name='سفارش')

    class Meta:  # configures metadata
        db_table = 'استفاده کد تخفیف'  # human-readable singular name
        verbose_name_plural = 'استفاده های کد نخفیف'  # human-readable plural name
        ordering = ('coupon',)  # sorts data in table based on coupon
        unique_together = (('coupon', 'user'),)  # this combination should be unique in database level

    def __str__(self):  # gets human-readable string when the object is called or printed
        return f'{self.coupon.code} used by {self.user.phone_number}'