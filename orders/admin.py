from django.contrib import admin
from orders.models import Order, OrderItem, Coupon, CouponUsage


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'variant', 'product', 'price', 'quantity', 'order_item_total_price',
                    'created_at_jalali', 'updated_at_jalali')
    list_filter = ('product__name',)
    search_fields = ('variant__name',)
    readonly_fields = ('product','price')


class OrderItemAdminTabular(admin.TabularInline):  # allows to show order item table in order
    model = OrderItem
    extra = 1
    fields = ('variant', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone_number', 'email', 'first_name', 'last_name', 'state', 'city', 'address',
                    'zip_code', 'paid', 'coupon', 'base_price', 'discount', 'paid_price', 'order_current_total_price',
                    'order_current_final_price', 'created_at_jalali', 'updated_at_jalali')
    list_filter = ('paid',)
    search_fields = ('first_name', 'last_name', 'phone_number', 'email', 'coupon__code')
    inlines = [OrderItemAdminTabular]  # enables us to have order item table in here


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'available', 'max_uses', 'times_used', 'start_date', 'end_date', 'is_valid',
                    'created_at_jalali', 'updated_at_jalali')
    list_filter = ('available',)
    search_fields = ('code',)


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'order', 'created_at_jalali', 'updated_at_jalali')
    list_filter = ('coupon',)
    search_fields = ('order__phone_number', 'user__phone_number')
