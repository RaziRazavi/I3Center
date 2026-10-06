from django.contrib import admin
from products.models import (Product, Brand, Material, Category, Comment, PriceChange, Size, Color, Variant, ExtraImage,
                             ProductSeen, ContactUs)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'description', 'logo', 'created_at_jalali', 'updated_at_jalali')
    search_fields = ('name',)
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # slug field will be written automatically based on name field
    ordering = ('name',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'slug', 'created_at_jalali', 'updated_at_jalali')
    search_fields = ('name',)
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # slug field will be written automatically based on name field
    ordering = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'image', 'parent', 'is_parent', 'created_at_jalali', 'updated_at_jalali')
    list_filter = ('is_parent',)
    search_fields = ('name',)
    readonly_fields = ('id',)
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # slug field will be written automatically based on name field
    ordering = ('name',)
    raw_id_fields = ('parent',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'parent', 'is_reply', 'body', 'created_at_jalali')
    list_filter = ('product', 'user')
    ordering = ('created_at',)
    list_editable = ('is_reply',)


@admin.register(PriceChange)
class PriceChangeAdmin(admin.ModelAdmin):
    list_display = ('product', 'variant', 'price', 'created_at_jalali')
    ordering = ('variant',)
    list_filter = ('product',)
    search_fields = ('variant__name',)
    readonly_fields = ('product',)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'hex_code', 'extra_price', 'created_at_jalali', 'updated_at_jalali')
    list_filter = ('name',)
    ordering = ('name',)
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # slug field will be written automatically based on name field


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'extra_price', 'created_at_jalali', 'updated_at_jalali')
    list_filter = ('name',)
    ordering = ('name',)
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # slug field will be written automatically based on name field


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product', 'color', 'size', 'unit_price', 'discount', 'variant_price',
                    'final_price',  'stock', 'sales_count','available', 'created_at_jalali', 'updated_at_jalali')
    list_filter = ('product', 'color', 'size')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('name','slug')


class VariantAdminTabular(admin.TabularInline):  # allows to show Variant table inside Product table
    model = Variant
    extra = 1
    min_num = 1  # forces have at least on variant for each product
    validate_min = True  # validates the rule
    fields = ('color', 'size', 'unit_price', 'discount', 'stock', 'available')


@admin.register(ExtraImage)
class ExtraImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'title', 'alt', 'created_at_jalali', 'updated_at_jalali')
    list_filter = ('product',)
    search_fields = ('title', 'alt')


class ExtraImageAdminTabular(admin.TabularInline):
    model = ExtraImage
    extra = 1


@admin.register(ProductSeen)
class ProductSeenAdmin(admin.ModelAdmin):
    list_display = ('product', 'ip_address', 'created_at_jalali', 'updated_at_jalali')
    search_fields = ('product__name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'brand', 'material', 'category', 'image', 'start_price', 'discount', 'has_discount',
                    'base_price', 'total_stocks', 'views_count', 'favorites_count', 'sales_count', 'available',
                    'created_at_jalali', 'updated_at_jalali')
    list_filter = ('available', 'material', 'brand', 'category')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # slug field will be written automatically based on name field
    ordering = ('name',)
    readonly_fields = ('has_discount',)
    list_editable = ('available','start_price')
    inlines = [VariantAdminTabular, ExtraImageAdminTabular]  # enables us to have these tables inside Product table


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'subject', 'done', 'created_at_jalali', 'updated_at_jalali')
    search_fields = ('name', 'phone_number', 'email')
    ordering = ('-created_at',)
    list_editable = ('done',)
