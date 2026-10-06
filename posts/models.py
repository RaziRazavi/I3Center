from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.urls import reverse
from utility.inheritance import BaseModel
from django.utils.text import slugify


class PostCategory(BaseModel):
    name = models.CharField(max_length=255, verbose_name='اسم')
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, allow_unicode=True, verbose_name='اسلاگ')
    image = models.ImageField(upload_to='posts/category', blank=True, null=True, verbose_name='تصویر')
    description = models.CharField(max_length=255, verbose_name='توضیح')

    class Meta:  # configures metadata
        db_table = 'دسته بندی مقاله'  # human-readable singular name
        verbose_name_plural = 'دسته بندی های مقاله'  # human-readable plural name
        ordering = ('name',)  # sorts data in table based on name

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.name

    def save(self, *args, **kwargs):  # automatics writing slug field based on name field
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_image_src(self):  # return url of related image if there is
        return self.image.url if self.image else ''

    def get_absolute_url(self):  # returns url of related view
        return reverse('posts:view_from_category', kwargs={'pk': self.pk, 'slug': self.slug})


class Post(BaseModel):
    author = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, related_name='post_authors',
                               blank=True, null=True, verbose_name='نویسنده')
    category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, blank=True, null=True, related_name='posts',
                                 verbose_name='دسته بندی مقاله')
    name = models.CharField(max_length=255, verbose_name='اسم')
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, allow_unicode=True, verbose_name='اسلاگ')
    image = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True, null=True, verbose_name='تصویر')
    text = RichTextUploadingField(verbose_name='متن')
    description = models.CharField(max_length=255, verbose_name='توضیح')
    comments_count = models.PositiveIntegerField(default=0, verbose_name='تعداد کامنت')
    views_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    likes_count = models.PositiveIntegerField(default=0, verbose_name='تعداد لایک')
    lovers = models.ManyToManyField('accounts.User', related_name='post_lovers', verbose_name='لایک کننده ها')

    class Meta:  # configures metadata
        db_table = 'مقاله'  # human-readable singular name
        verbose_name_plural = 'مقاله ها'  # human-readable plural name
        ordering = ('name',) # sorts data in table based on name

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.name

    def save(self, *args, **kwargs):  # overrides save method ...
        if not self.slug:  # if slug field is empty, fills it base on name field
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_image_src(self):  # returns url of related image if there is
        return self.image.url if self.image else ''

    def get_absolute_url(self):  # returns url of related view
        return reverse('posts:details', kwargs={'category_pk':self.category.pk,
                'category_slug':self.category.slug, 'post_pk':self.pk, 'post_slug':self.slug})

    def get_love_url(self):  # return url of related view
        return reverse('posts:post_love', kwargs={'pk':self.pk})


class PostComment(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='مقاله')
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='post_comments',
                               verbose_name='نویسنده')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies',
                               verbose_name='پدر')
    is_reply = models.BooleanField(default=False, verbose_name='جواب کامنت')
    body = models.TextField(verbose_name='متن')
    lovers = models.ManyToManyField('accounts.User', related_name='post_comment_lovers', verbose_name='لایک کننده ها')
    haters = models.ManyToManyField('accounts.User', related_name='post_comment_haters', verbose_name='هیت دهنده ها')

    class Meta:
        db_table = 'کامنت مقاله'  # human-readable singular name
        verbose_name_plural = 'کامنت های مقاله'  # human-readable plural name
        ordering = ('post',)  # sorts data in table based on name

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.author.get_full_name

    def total_lovers(self):  # counts the amounts of field
        return self.lovers.count()

    def total_haters(self):  # counts the amounts of field
        return self.haters.count()

    def get_love_url(self):  # return url of related view
        return reverse('posts:comment_love', kwargs={'pk':self.pk})

    def get_hate_url(self): # return url of related view
        return reverse('posts:comment_hate', kwargs={'pk':self.pk})


class PostSeen(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_seen', verbose_name='مقاله')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='آیپی آدرس')

    class Meta:  # configures metadata
        db_table = 'بازدید مقاله'  # human-readable singular name
        verbose_name_plural = 'بازدید های مقاله'  # human-readable plural name
        ordering = ('post',)  # sorts data in table based on name

    def __str__(self):  # gets human-readable string when the object is called or printed
        return self.post.name
