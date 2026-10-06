from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from accounts.models import User
from products.model_field_validation import price_validation, discount_validation
from django.core.exceptions import ValidationError
from utility.inheritance import BaseModel
from ckeditor_uploader.fields import RichTextUploadingField

class Brand(BaseModel):
    name = models.CharField(max_length=100, verbose_name='اسم')
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, blank=True, null=True,
                            verbose_name='اسلاگ')  # farsi is also ok
    description = models.TextField(verbose_name='توضیح')
    logo = models.ImageField(upload_to='brands', blank=True, null=True, verbose_name='لوگو')

    class Meta:  # configures metadata
        db_table = 'برند'  # human-readable singular name
        verbose_name_plural = 'برند ها'  # human-readable plural name
        ordering = ('name',)  # sorts data in table based on name

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.name

    def save(self, *args, **kwargs):  # automatics writing slug field based on name field
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_image_src(self):  # return url of related image if there is
        if self.logo:
            return self.logo.url
        else:
            return ''


class Material(BaseModel):
    name = models.CharField(max_length=100, verbose_name='اسم')
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, blank=True, null=True,
                            verbose_name='اسلاگ')  # farsi is also ok

    class Meta:  # configures metadata
        db_table = 'جنس'  # human-readable singular name
        verbose_name_plural = 'جنس ها'  # human-readable plural name
        ordering = ('name',)  # sorts data in table based on name

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.name

    def save(self, *args, **kwargs):  # automatics writing slug field based on name field
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(BaseModel):
    name = models.CharField(max_length=100, verbose_name='اسم')
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, blank=True, null=True,
                            verbose_name='اسلاگ') # farsi is also ok
    image = models.ImageField(upload_to='categories', blank=True, null=True, verbose_name='تصویر')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categories', blank=True, null=True,
                               verbose_name='پدر')
    is_parent = models.BooleanField(default=False, verbose_name='داشتن پدر')

    class Meta:  # configures metadata
        db_table = 'دسته بندی محصول'  # human-readable singular name
        verbose_name_plural = 'دسته بندی های محصول'  # human-readable plural name
        ordering = ('name',)  # sorts data in table based on name

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.name

    def save(self, *args, **kwargs):  # automatics writing slug field based on name field
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_image_src(self):  # return url of related image if there is
        if self.image:
            return self.image.url
        else:
            return ''

    def get_absolute_url(self):  # gets url of related view
        return reverse('products:category_sub', kwargs={'pk': self.pk, 'slug': self.slug})

    def has_child(self):  # checks whether it has child....
        return True if self.sub_categories.exists() else False


class Product(BaseModel):
    name = models.CharField(max_length=255, verbose_name='اسم')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True,
                            verbose_name='اسلاک')  # farsi is also ok
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products',
                              verbose_name='برند')  # connects via foreignkey
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='products',
                                 verbose_name='جنس')  # connects via foreignkey
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products',
                                 verbose_name='دسته بندی محصول')  # connects via foreignkey
    description = RichTextUploadingField(verbose_name='توضیح')
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, null=True, verbose_name='تصویر')
    start_price = models.PositiveIntegerField(validators=[price_validation, ],
                                              verbose_name='قیمت اولیه')  # uses extra validator
    discount = models.PositiveSmallIntegerField(default=0, validators=[discount_validation, ],
                                                verbose_name='تخفیف')  # uses extra validator
    has_discount = models.BooleanField(default=False, verbose_name='داشتن تخفیف')
    likers = models.ManyToManyField(User, related_name='product_likers', blank=True, verbose_name='لایک کننده ها')
    views_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    favorites_count = models.PositiveIntegerField(default=0, verbose_name='تعداد لایک ها')
    sales_count = models.PositiveIntegerField(default=0, verbose_name='تعداد فروش')
    available = models.BooleanField(default=True, verbose_name='موجود')

    class Meta:  # configures metadata
        db_table = 'محصول'  # human-readable singular name
        verbose_name_plural = 'محصول ها'  # human-readable plural name
        ordering = ('name',)  # sorts data in table based on name

    def save(self, *args, **kwargs):  # automates writing slug field based on name field
        if not self.slug:
            self.slug = slugify(self.name)

        self.has_discount = True if self.discount > 0 else False  # sets true if discount is bigger than zero
        super().save(*args, **kwargs)

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.name

    def get_absolute_url(self):  # returns url of related view
        return reverse('products:details', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_image_src(self):  # return url of related image if there is
        if self.image:
            return self.image.url
        else:
            return ''

    def get_like_url(self):  # returns url of related view
        return reverse('products:product_like', kwargs={'pk': self.pk})

    @property
    def base_price(self):  # calculates price
        if self.discount and self.discount > 0:
            return self.start_price * (100 - self.discount) // 100
        else:
            return self.start_price

    @property
    def total_stocks(self):  # gets total stock
        total = 0
        variants = self.variants.all()
        for variant in variants:
            total += variant.stock
        return total


class Color(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name='رنگ')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True, verbose_name='اسلاگ')
    hex_code = models.CharField(max_length=100, unique=True, verbose_name='کد هگز رنگ')
    extra_price = models.PositiveIntegerField(default=0, verbose_name='قیمت اضافه')

    class Meta:  # configures metadata
        db_table = 'رنگ'  # human-readable singular name
        verbose_name_plural = 'رنگ ها'  # human-readable plural name
        ordering = ('name',)  # sorts data in table based on name

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.name

    def save(self, *args, **kwargs):  # overrides save method
        if not self.slug:  # auto generates slug field
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Size(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name='اسم')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True, verbose_name='اسلاگ')
    extra_price = models.PositiveIntegerField(default=0, verbose_name='قیمت اضافه')

    class Meta:  # configures metadata
        db_table = 'سایز'  # human-readable singular name
        verbose_name_plural = 'سایز ها'  # human-readable plural name
        ordering = ('name',)  # sorts data in table based on name

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.name

    def save(self, *args, **kwargs):  # overrides save method
        if not self.slug:  # auto generates slug field
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Variant(BaseModel):
    name = models.CharField(max_length=255, blank=True, verbose_name='اسم')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True, verbose_name='اسلاگ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name='محصول')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='variants', verbose_name='رنگ')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='variants', verbose_name='سایز')
    unit_price = models.PositiveIntegerField(default=0, verbose_name='قیمت هر واحد')
    discount = models.PositiveSmallIntegerField(default=0, validators=[discount_validation,],
                                                verbose_name='تخفیف')  # uses extra validator
    stock = models.PositiveIntegerField(default=0, verbose_name='موجودی')
    sales_count = models.PositiveIntegerField(default=0, verbose_name='تعداد فروش')
    available = models.BooleanField(default=True, verbose_name='موجود')

    class Meta:  # configures metadata
        db_table = 'متغیر'  # human-readable singular name
        verbose_name_plural = 'متغیر ها'  # human-readable plural name
        ordering = ('name',)  # sorts data in table based on name
        unique_together = [('product', 'color', 'size')]  # enforce law of having unique combination

    def save(self, *args, **kwargs):  # overrides save method
        if not self.name:  # auto generates name field
            self.name = f"{self.color.name} - {self.size.name}"
        if not self.slug:  # # auto generates slug field
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):  # enforces law of not deleting last variant of a product
        if self.product.variants.count() == 1:
            raise ValidationError('آخرین متغیر حذف نمیشود ')
        super().delete(*args, **kwargs)

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.name

    @property
    def variant_price(self):  # calculates variant price
        if self.discount > 0 :
            return (self.unit_price + self.color.extra_price + self.size.extra_price) * (100 - self.discount) // 100
        else:
            return self.unit_price + self.color.extra_price + self.size.extra_price

    @property
    def final_price(self):  # calculates variant final price
        base_price = self.product.base_price
        extra_price = self.unit_price + self.color.extra_price + self.size.extra_price
        if self.discount > 0 :
            return (base_price + extra_price) * (100 - self.discount) // 100
        else:
            return base_price + extra_price

    @property
    def is_available(self):  # checks if variant is available
        if not self.product.available:
            return False
        if not self.available:
            return False
        if self.stock == 0:
            return False
        return True


class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments',
                             verbose_name='کاربر')  # connects via foreignkey
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments',
                                verbose_name='محصول')  # connects via foreignkey
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', blank=True, null=True,
                               verbose_name='پدر')
    is_reply = models.BooleanField(default=False, verbose_name='جواب')
    body = models.TextField(verbose_name='متن')
    likers = models.ManyToManyField(User, related_name='comment_likers', blank=True, verbose_name='لایک کننده ها')
    dislikers = models.ManyToManyField(User, related_name='comment_dislikers', blank=True, verbose_name='هیت دهنده ها')

    class Meta:  # configures metadata
        db_table = 'کامنت محصول'  # human-readable singular name
        verbose_name_plural = 'کامنت های محصول'  # human-readable plural name
        ordering = ('product',)  # sorts data in table based on product

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.user.phone_number

    def like_count(self):  # counts the amounts of field
        return self.likers.count()

    def dislike_count(self):  # counts the amounts of field
        return self.dislikers.count()

    def get_like_url(self):  # returns url of related view
        return reverse('products:comment_like', kwargs={'pk': self.pk})

    def get_dislike_url(self):  # returns url of related view
        return reverse('products:comment_dislike', kwargs={'pk': self.pk})


class PriceChange(BaseModel):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='price_changes', blank=True, null=True,
                                verbose_name='متغیر')  # connects via foreign key to variant table
    product = models.CharField(max_length=255, blank=True, null=True, verbose_name='محصول')
    price = models.PositiveIntegerField(verbose_name='قیمت')

    class Meta:  # configures metadata
        db_table = 'تغییر قیمت'  # human-readable singular name
        verbose_name_plural = 'تغییر های قیمت'  # human-readable plural name
        ordering = ('created_at',)  # sorts data in table based on created time

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.variant.name

    def save(self, *args, **kwargs):
        if not self.product:  # auto generates product field
            self.product = self.variant.product
        super().save(*args, **kwargs)


class ExtraImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='extra_images', verbose_name='محصول')
    image = models.ImageField(upload_to='product_extra_images/%Y/%m/%d/', verbose_name='تصویر')
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='عنوان')
    alt = models.CharField(max_length=255, blank=True, null=True, verbose_name='متن جایگرین')

    class Meta:  # configures metadata
        db_table = 'تصویر اضافه'  # human-readable singular name
        verbose_name_plural = 'تصویر های اضافه'  # human-readable plural name
        ordering = ('product',) # sorts data in table based on product

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.product.name

    @property
    def get_image_src(self):  # gets url of related image
        return self.image.url


class ProductSeen(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_seen', verbose_name='محصول')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='آیپی آدرس')

    class Meta:  # configures metadata
        db_table = 'بازدید محصول'  # human-readable singular name
        verbose_name_plural = 'بازدید های محصول'  # human-readable plural name
        ordering = ('product',)   # sorts data in table based on product

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.product.name


class ContactUs(BaseModel):
    name = models.CharField(max_length=255, verbose_name='اسم')
    phone_number = models.CharField(max_length=11, verbose_name='شماره تماس')
    email = models.EmailField(max_length=255, verbose_name='ایمیل')
    subject = models.CharField(max_length=255, verbose_name='عنوان')
    message = models.TextField(verbose_name='پیام')
    done = models.BooleanField(default=False, verbose_name='بررسی شد')

    class Meta:  # configures metadata
        db_table = 'ارتباط با ما'  # human-readable singular name
        verbose_name_plural = 'ارتباط با ما'  # human-readable plural name
        ordering = ('-created_at',)  # sorts data in table based on created time

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.name