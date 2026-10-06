from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from products.models import Variant
from orders.forms import CartForm, OrderForm, CouponForm
from orders.cart import Cart
from orders.models import Order, OrderItem, Coupon, CouponUsage
from django.conf import settings
from django.db import transaction
import requests
import json
import logging
logger = logging.getLogger(__name__)


class CartView(View):
    def get(self, request):  # shows cart data to user
        try:
            return render(request, 'orders/cart_view.html', {'cart': Cart(request)})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in CartView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page


class AddToCartView(View):
    def post(self, request, *args, **kwargs):  # manages collected data from user
        try:
            variant = get_object_or_404(Variant, id=kwargs.get('pk'))  # if there's variant
            if not variant.product.available or not variant.is_available:  # if variant or product isn't available
                messages.add_message(request, 200, 'محصول یا متفییر موجود نیست',
                                     'warning')
                return redirect(variant.product.get_absolute_url())  # redirects back to related product page

            cart = Cart(request)  # fills cart with data from request
            form = CartForm(request.POST)  # fills cartForm with data from request.post
            if form.is_valid():  # if form is valid...
                try:
                    cart.add(variant, form.cleaned_data.get('quantity'))  # uses add method from cart with cleaned quantity
                    messages.add_message(request, 200, 'به کارت اضافه شد', 'success')
                    return redirect('orders:cart_view')  # redirect to this url
                except ValueError as e:  # if it goes wrong with valueError...
                    messages.add_message(request, 200, f'{str(e)}', 'danger')
                    return redirect(variant.product.get_absolute_url())  # redirects back to related product page
            else:  # if data is invalid...
                messages.add_message(request, 200, 'اطلاعات نامعتبر است', 'danger')
                return redirect(variant.product.get_absolute_url())  # redirects back to related product page

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in AddToCartView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page


class UpdateCartQuantityView(View):
    def post(self, request, *args, **kwargs):  # manages collected data from user
        try:
            cart = Cart(request)  # fills cart with data from request
            variant = get_object_or_404(Variant, id=kwargs.get('pk'))  # gets exact variant
            _action = request.POST.get('action')  # gets value of action inside request.post
            try:
                if _action == 'add':  # if it's add ...
                    cart.add(variant, quantity=1)  # calls add method from cart with quantity 1
                    messages.add_message(request, 200, 'یکی به کارت اضافه شد', 'success')
                elif _action == 'remove':  # if it's remove ...
                    cart.remove_one(variant)  # calls remove one method from cart
                    messages.add_message(request, 200, 'یکی از کارت کم شد', 'success')
                elif _action == 'delete':  # if it's delete ...
                    cart.remove(variant)  # calls remove method from cart
                    messages.add_message(request, 200, f'آیتم{variant.name} از کارت حذف شد ',
                                         'success')
                else:  # or other stuff ...
                    messages.add_message(request, 200, 'اطلاعات نامعتبر است', 'danger')

                return redirect('orders:cart_view')  # redirects to this url
            except ValueError as e:  # whether it goes wrong with valueError...
                messages.add_message(request, 200, f'{str(e)}', 'danger')
                return redirect('orders:cart_view')  # redirects to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in UpdateCartQuantityView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page


class OrderFormView(LoginRequiredMixin, View):
    form_class = OrderForm
    template_name = 'orders/order_form.html'

    def dispatch(self, request, *args, **kwargs):  # examine some conditions before further process  # checks before going in, if there is cart...
        cart_data = Cart(request)
        if not cart_data:
            return redirect('orders:cart_view')  # if not, redirects back
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):  # shows form class with instance of request.user to user
        try:
            return render(request, self.template_name, {'form': self.form_class(instance=request.user)})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in OrderFormView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page

    def post(self, request, *args, **kwargs):  # # manages collected data from user
        try:
            form = self.form_class(request.POST, instance=request.user)  # fills form class with one of these data
            if form.is_valid():  # if for is valid
                cd = form.cleaned_data  # gets cleaned data from form
                with transaction.atomic():  # database doesn't write if anything goes wrong inside this block
                    order = Order.objects.create(
                        user=request.user,
                        phone_number=cd.get('phone_number'),
                        email=cd.get('email'),
                        first_name=cd.get('first_name'),
                        last_name=cd.get('last_name'),
                        state=cd.get('state'),
                        city=cd.get('city'),
                        address=cd.get('address'),
                        zip_code=cd.get('zip_code'),
                    )  # creates new order object inside its table and puts in order variable
                    cart_data = Cart(request)  # fills cart with request data
                    for item in cart_data:  # applies some things to items inside cart
                        variant = Variant.objects.filter(id=item.get('variant_id')).first()  # gets right variant
                        if variant is None:  # if variant is None
                            messages.add_message(request, 200, 'متغیر موجود نیست', 'danger')
                            return redirect('orders:cart_view')  # redirects to this url

                        if not variant.is_available:  # if variant isn't available
                            messages.add_message(request, 200, f'{variant.name} موجود نیست ',
                                                 'warning')
                            return redirect('orders:cart_view')  # redirects to this url

                        if item.get('quantity') > variant.stock:  # if quantity is bigger than variant stock ...
                            messages.add_message(request, 200, f'فقط {variant.stock} باقی مانده است ',
                                                 'warning')
                            return redirect('orders:cart_view')  # redirects to this url

                        OrderItem.objects.create(
                            order=order,
                            variant=variant,
                            quantity=item.get('quantity'),
                        )  # creates new orderItem object inside its table
                    order.base_price = order.order_current_total_price  # fills base price field with this
                    order.save()  # saves it

                del request.session['cart']  # removes cart from session
                messages.add_message(request, 200, 'سفارش ثبت شد', 'success')
                return redirect('orders:order_view')  # redirects to this url
            else:
                messages.add_message(request, 200, 'اطلاعات نامعتبر است', 'warning')
                return render(request, self.template_name, {'form': self.form_class(instance=request.user)})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in OrderFormView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page


class OrderView(LoginRequiredMixin, View):
    template_name = 'orders/order_view.html'

    def get(self, request, *args, **kwargs):  # sends orders to related template
        try:
            return render(request, self.template_name,
                          {'orders': Order.objects.filter(user=request.user).prefetch_related('order_items')})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in OrderView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page

    def post(self, request, *args, **kwargs):  # manages collected data from user
        try:
            _order = request.POST.get('order')  # gets value of order inside request.post
            if not _order:  # if not ...
                messages.add_message(request, 200, 'اطلاعات نامعتبر است', 'warning')
                return redirect('orders:order_view')  # redirects to this url
            order = get_object_or_404(Order, id=_order, user=request.user)
            if order.paid:  # if its paid ...
                messages.add_message(request, 200, 'نمی توان سفارش پرداخت شده را حذف کرد', 'warning')
            else:  # if not ...
                messages.add_message(request, 200, f'Order {order.id} has been deleted', 'success')
                order.delete()  # deletes order from database
            return redirect('orders:order_view')  # redirects to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in OrderView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page


class OrderModifyView(LoginRequiredMixin, View):
    form_class = OrderForm
    template_name = 'orders/order_modify.html'

    def setup(self, request, *args, **kwargs):  # gets order from database
        self.order = get_object_or_404(Order.objects.prefetch_related('order_items'), id=kwargs.get('id'),
                                       user=request.user)
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):  # examine some conditions before further process
        if self.order.paid:  # if its paid ...
            return redirect('orders:order_view')  # redirects to this url
        if self.order.order_items.count() == 0:  # if orderItems's count is zero
            return redirect('orders:order_view')  # redirects to this url
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):  # sends form and order to related template
        try:
            return render(request, self.template_name,
                          {'form': self.form_class(instance=self.order), 'order': self.order})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in OrderModifyView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page

    def post(self, request, *args, **kwargs):  # manages collected data from user
        try:
            form = self.form_class(request.POST, instance=self.order)  # fills form with one of these data
            if form.is_valid():  # if form is valid
                cd = form.cleaned_data  # gets cleaned data from form
                self.order.phone_number = cd.get('phone_number')
                self.order.email = cd.get('email')
                self.order.first_name = cd.get('first_name')
                self.order.last_name = cd.get('last_name')
                self.order.state = cd.get('state')
                self.order.city = cd.get('city')
                self.order.address = cd.get('address')
                self.order.zip_code = cd.get('zip_code')
                if not self.order.paid:
                    self.order.base_price = self.order.order_current_total_price

                self.order.save()  # saves and updates order with given data
                messages.add_message(request, 200, 'سفارش ثبت شد', 'success')
                return redirect('orders:order_view') # redirects to this url
            else:  # if it's not valid, sends back to user
                messages.add_message(request, 200, 'اطلاعات نامعتبر است', 'danger')
                return render(request, self.template_name,
                              {'form': self.form_class(instance=self.order), 'order': self.order})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in OrderModifyView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page


class UpdateQuantityView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):  # gets order from database
        self.item = get_object_or_404(OrderItem.objects.select_related('order'), id=kwargs.get('id'),
                                      order__user=request.user)
        self.order = get_object_or_404(Order, id=self.item.order.id)
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):  # examine some conditions before further process
        if self.order.paid:  # if it's paid ...
            return redirect('orders:order_view') # redirects to this url
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):  # manages collected data from user
        try:
            _action = request.POST.get('action')  # gets value of action from request.post
            if _action == 'add':  # if it's add ...
                if not self.item.variant.is_available:  # if variant isn't available
                    messages.add_message(request, 200, f'{self.item.variant.name} موجود نیست ',
                                         'warning')
                    return redirect('orders:order_modify', id=self.item.order.id)  # redirects to this url
                if self.item.quantity + 1 > self.item.variant.stock:  # if quantity is bigger than variant stock
                    messages.add_message(request, 200, f'فقط {self.item.variant.stock} باقی مانده است ',
                                         'warning')
                    return redirect('orders:order_modify', id=self.item.order.id)  # redirects to this url
                self.item.quantity += 1  # adds one to quantity
                self.item.save()  # saves it
                messages.add_message(request, 200, 'یکی به سفارش اضافه شد', 'success')
            elif _action == 'remove':  # if it's remove ...
                self.item.quantity -= 1  # subtracts one from quantity
                if self.item.quantity == 0:  # if quantity is zero
                    self.item.delete()  # deletes it
                    if self.order.order_items.count() == 0:  # if count of orderItems is zero ...
                        self.order.delete()  # deletes it
                        messages.add_message(request, 200, 'سفارش حذف شد', 'success')
                        return redirect('orders:order_view')  # redirects to this url
                    messages.add_message(request, 200, f'{self.item.variant.name} حذف شد ',
                                         'warning')
                else:  # if not ...
                    self.item.save()  # saves it
                    messages.add_message(request, 200, 'یکی از سفارش شما حذف شد',
                                         'success')
            elif _action == 'delete':  # if it's delete
                self.item.delete()  # deletes it
                if self.order.order_items.count() == 0:  # if count of orderItems is zero
                    self.order.delete()  # deletes it
                    messages.add_message(request, 200, 'سفارش حذف شد', 'success')
                    return redirect('orders:order_view')  # redirects to this url
                messages.add_message(request, 200, f'{self.item.variant.name} حذف شد ', 'success')
            else:  # if it's something else ....
                messages.add_message(request, 200, 'اطلاعات نامعتبر است', 'danger')

            return redirect('orders:order_modify', id=self.item.order.id)  # redirects to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in UpdateQuantityView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page


class OrderDetailView(LoginRequiredMixin, View):
    form_class = CouponForm
    template_name = 'orders/order_details.html'

    def setup(self, request, *args, **kwargs):  # gets order from database
        self.order = get_object_or_404(Order.objects.prefetch_related('order_items'), id=kwargs.get('id'),
                                       user=request.user)
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):  # sends form and order to related template
        try:
            return render(request, self.template_name, {'order': self.order, 'form': self.form_class()})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in OrderDetailView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page

    def post(self, request, *args, **kwargs):  # manages collected data from user
        try:
            if self.order.paid:  # if it's paid
                messages.add_message(request, 200, 'سفارش قبلا پرداخت شده است', 'warning')
                return redirect(self.order.get_absolute_url())

            form = self.form_class(request.POST)  # fills form with data from request.post
            if not form.is_valid():  # if form isn't valid ...
                messages.add_message(request, 200, 'اطلاعات نامعتبر است', 'warning')
                return render(request, self.template_name, {'form': form, 'order': self.order})  # sends back to user

            code = form.cleaned_data.get('code')  # gets code from cleaned data
            if not code:  # if it's not ...
                self.order.coupon = None
                self.order.paid_price = self.order.base_price = self.order.order_current_total_price
                self.order.save()  # saves and updates order with given data
                messages.add_message(request, 200, 'سفارش ثبت شد', 'success')
                return redirect('orders:order_pay', id=self.order.id)  # redirects to this url

            coupon_instance = Coupon.objects.filter(code__exact=code).first()  # gets coupon instance
            if coupon_instance is None:  # if there's not ...
                messages.add_message(request, 200, 'کد تخفیف وجود ندارد', 'warning')
                return render(request, self.template_name, {'form': form, 'order': self.order})  # sends data back

            if not coupon_instance.is_valid_for(request.user):  # if coupon isn't valid for user ...
                messages.add_message(request, 200, 'کد تخفیف معتبر نیست یا استفاده شده است', 'warning')
                return render(request, self.template_name, {'form': form, 'order': self.order})  # sends data back

            self.order.coupon = coupon_instance
            self.order.discount = coupon_instance.discount
            self.order.base_price = self.order.order_current_total_price
            self.order.paid_price = self.order.order_current_final_price
            self.order.save()  # saves and updates order with given data
            messages.add_message(request, 200, 'کد تخفیف اعمال و سفارش ثبت شد', 'success')
            return redirect('orders:order_pay', id=self.order.id)  # redirects to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in OrderDetailView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page


class OrderPayView(LoginRequiredMixin, View):
    template_name = 'orders/order_pay.html'

    def setup(self, request, *args, **kwargs):  # gets order from database
        self.order = get_object_or_404(Order, id=kwargs.get('id'), user=request.user)
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):  # examine some conditions before further process
        if self.order.paid_price is None:  # if order hasn't paid price field ...
            messages.add_message(request, 200, 'سفارش قیمت ندارد', 'warning')
            return redirect(self.order.get_absolute_url())  # redirects to this url
        if self.order.paid:  # if order is paid ...
            messages.add_message(request, 200, 'سفارش قبلا ثبت شده است', 'warning')
            return redirect(self.order.get_absolute_url())  # redirects to this url
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):  # shows order
        try:
            return render(request, self.template_name, {'order': self.order})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in OrderPayView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page


class PaymentRequestView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):  # gets order from database
        self.order = get_object_or_404(Order, id=kwargs.get('id'), user=request.user)
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):  # examine some conditions before further process
        if self.order.paid_price is None:  # if order hasn't paid price field ...
            messages.add_message(request, 200, 'سفارش قیمت ندارد', 'warning')
            return redirect(self.order.get_absolute_url())  # redirects to this url
        if self.order.paid: # if order is paid ...
            messages.add_message(request, 200, 'سفارش قبلا پرداخت شده است', 'warning')
            return redirect(self.order.get_absolute_url())  # redirects to this url
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):  # sends payment request to service provider
        try:
            data = json.dumps({
                "MerchantID": settings.MERCHANT,
                "Amount": int(self.order.paid_price) * 10,  # it is based on Rials
                "Description": f"receptor: {self.order.first_name} {self.order.last_name}, price: {self.order.base_price}",
                "Phone": self.order.phone_number,
                "CallbackURL": request.build_absolute_uri(reverse('orders:zp_verify')),
            })  # gets data in json format
            # set content length by data
            headers = {'content-type': 'application/json', 'content-length': str(len(data))}

            try:
                response = requests.post(settings.ZP_API_REQUEST, data=data, headers=headers, timeout=10) # sends data
            except requests.exceptions.Timeout:  # if it gets this error ...
                messages.add_message(request, 200, 'درگاه با مشکل مواجه شده است، دوباره امتحان کنید',
                                     'warning')
                return redirect(self.order.get_absolute_url()) # redirects to this url
            except requests.exceptions.ConnectionError:  # if it gets this error ...
                messages.add_message(request, 200, 'مشکل اتصال', 'warning')
                return redirect(self.order.get_absolute_url())  # redirects to this url

            if response.status_code != 200:  # if it isn't successful ...
                messages.add_message(request, 200, 'درگاه با مشکل مواجه شده است، دوباره امتحان کنید',
                                     'warning')
                return redirect(self.order.get_absolute_url())  # redirects to this url

            result = response.json()  # parses data to json format
            if result['Status'] == 100:  # if status is 100 ...
                request.session['order'] = self.order.id  # insert order into session
                return redirect(settings.ZP_API_STARTPAY + str(result['Authority']))  # redirects to this url

            messages.add_message(request, 200,
                                 f"درخواست پرداخت ناموفق - کد : {result['Status']}", 'warning')
            return redirect(self.order.get_absolute_url())  # redirects to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in PaymentRequestView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page


class PaymentVerifyView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):  # shows result of payment service provider
        try:
            authority = request.GET.get('Authority')  # gets this parameter from request.get
            status = request.GET.get('Status')  # gets this parameter from request.get
            order = get_object_or_404(Order, id=request.session.get('order'), user=request.user)  # gets order
            del request.session['order']  # deletes order from session
            if status != 'OK':  # if status isn't ok ...
                messages.add_message(request, 200, 'پرداخت کنسل شد', 'warning')
                return redirect(order.get_absolute_url()) # redirects to this url

            if order.paid:  # if order is paid ....
                messages.add_message(request, 200, 'درخواست پرداخت قبلا پرداخت شده است', 'warning')
                return redirect(order.get_absolute_url()) # redirects to this url

            data = json.dumps({
                "MerchantID": settings.MERCHANT,
                "Amount": int(order.paid_price) * 10,  # it is based on Rials
                "Authority": authority,
            })  # gets data in json format
            # set content length by data
            headers = {'content-type': 'application/json', 'content-length': str(len(data))}
            response = requests.post(settings.ZP_API_VERIFY, data=data, headers=headers, timeout=10) # sends data
            if response.status_code != 200:  #  if response status isn't 200
                messages.add_message(request, 200, 'درگاه با مشکل مواجه شده است، دوباره امتحان کنید', 'warning')
                return redirect(order.get_absolute_url())  # redirects to this url

            result = response.json()  # parses data as json and converts into python
            if result['Status'] == 100:  # if status is 100 ...
                with transaction.atomic():  # holds database until this block is successfully completed
                    order.paid = True  # sets order to paid
                    order.save()  # saves it

                    if order.coupon:  # if there's coupon ...
                        if order.coupon.is_valid_for(order.user):  # if coupon is valid for user ...
                            CouponUsage.objects.create(order=order, user=order.user, coupon=order.coupon)
                            order.coupon.times_used += 1
                            order.coupon.save() # saves and updates coupon with given data + creates order usage
                        else:  # if not, records happened error in log directory
                            logger.warning(f'Order {order.id} paid with already-invalid coupon {order.coupon.code}')

                    for item in order.order_items.all():  # does some tasks for orderItems ...
                        variant = item.variant  # gets variant
                        if variant is None: # if there's no variant, records happened error in log directory
                            logger.warning('some variant was deleted after order had been placed')
                            continue  # if variant was deleted after order had been placed

                        if variant.stock >= item.quantity:  # if variant stock is bigger than quantity of orderItem ...
                            variant.product.sales_count += item.quantity
                            variant.product.save()  # saves and updates product with new info
                            variant.sales_count += item.quantity
                            variant.stock -= item.quantity
                            if variant.stock == 0:
                                variant.available = False

                            variant.save()  # saves and updates product with new info
                        else:  # if variant stock is less than quantity, records happened error in log directory
                            logger.warning(
                                f'Order {item.order.id} sold variant {variant.name} but now there is not enough quantity')

                messages.add_message(request, 200,
                                     f"پرداخت موفق, ref ID : {result['RefID']}", 'success')
            else:  # if status isn't 100 ...
                messages.add_message(request, 200,
                                     f"درخواست پرداخت احراز نشد - کد : {result['Status']} ", 'warning')
            return redirect(order.get_absolute_url()) # redirects to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in PaymentVerifyView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')  # redirects to home page
