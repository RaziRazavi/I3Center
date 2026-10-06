from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from utility.function import send_sms, create_unique_otp_code
from accounts.forms import UserRegisterForm, OtpCodeForm, UserLoginForm
from accounts.models import OtpCode, User
from django.contrib import messages
from django.utils import timezone
import datetime
from django.contrib.auth import views as auth_views, authenticate, login, logout
from django.urls import reverse_lazy
import logging
logger = logging.getLogger(__name__)


class UserRegisterView(View):
    form_class = UserRegisterForm
    template_name = 'accounts/user_register.html'

    def get(self, request):  # shows empty form to user
        try:
            return render(request, self.template_name, {'form': self.form_class()})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in UserRegisterView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')

    def post(self, request):  # manages collected data from user
        try:
            form = self.form_class(request.POST)  # fills the form with collected data from user
            if form.is_valid():  # if given data is valid then...
                cd = form.cleaned_data
                random_code = create_unique_otp_code()  # creates random number for further operations
                if OtpCode.objects.filter(phone_number=cd.get('phone_number')).exists():  # checks if inserted number was there
                    OtpCode.objects.filter(phone_number=cd.get('phone_number')).delete()  # removes phone_number from database

                OtpCode.objects.create(phone_number=cd.get('phone_number'), code=random_code)
                # send_sms(phone_number=cd.get('phone_number'), code=random_code)  # sends sms using our send_sms utility
                messages.add_message(request, 200,
                f'send sms function is in line 32 of accounts.views and code is {random_code}', 'success')
                request.session['user_register_info'] = {
                    'phone_number': cd.get('phone_number'),
                    'email': cd.get('email'),
                    'first_name': cd.get('first_name'),
                    'last_name': cd.get('last_name'),
                    'state': cd.get('state'),
                    'city': cd.get('city'),
                    'address': cd.get('address'),
                    'zip_code': cd.get('zip_code'),
                    'password': cd.get('password1')
                }  # inserts collected data into session for next steps
                messages.add_message(request, 200, 'کد یکبار مصرف ارسال شد', 'success')
                return redirect('accounts:user_register_verify')  # redirects user to next step
            else:  # if data in form is not valid then ...
                messages.add_message(request, 200, 'اطلاعات را چک کنید', 'warning')
                return render(request, self.template_name, {'form': form})  # gives form again to user

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in UserRegisterView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class UserRegisterVerifyView(View):
    form_class = OtpCodeForm
    template_name = 'accounts/user_register_verify.html'

    def get(self, request):  # shows empty form to user
        try:
            return render(request, self.template_name, {'form': self.form_class()})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in UserRegisterVerifyView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')

    def post(self, request):  # manages collected data from user and session
        try:
            form = self.form_class(request.POST)  # fills the form with collected data from user
            if form.is_valid():  # if given data is valid then...
                otp_code = form.cleaned_data.get('OtpCode')
                user_register_info = request.session.get('user_register_info')  # gets related data from session within request
                otp_instance = OtpCode.objects.get(phone_number=user_register_info.get('phone_number'))
                if otp_instance.code != otp_code:  # if OTP Code doesn't match
                    messages.add_message(request, 200, 'کد یکبار مصرف اشتباه است', 'warning')
                    return redirect('accounts:user_register_verify')

                now = timezone.now()  # setups exact time and time of the moment
                opt_expire = otp_instance.created_at + datetime.timedelta(minutes=2)  # setups expiration for opt_instance
                if now > opt_expire:  # checks whether code is expired
                    messages.add_message(request, 200, 'کد یکبار مصرف منقضی شده است', 'warning')
                    del request.session['user_register_info']  # removes data from session
                    otp_instance.delete()  # deletes related OTP Code from database
                    return redirect('accounts:user_register')
                else:  # if otp_code doesn't expire
                    User.objects.create_user(
                        phone_number=user_register_info.get('phone_number'),
                        email=user_register_info.get('email'),
                        first_name=user_register_info.get('first_name'),
                        last_name=user_register_info.get('last_name'),
                        state=user_register_info.get('state'),
                        city=user_register_info.get('city'),
                        address=user_register_info.get('address'),
                        zip_code=user_register_info.get('zip_code'),
                        password=user_register_info.get('password')
                    )  # creates user using data from session
                    otp_instance.delete()  # deletes related OTP Code from database
                    del request.session['user_register_info']  # removes data from session
                    messages.add_message(request, 200, 'کاربر با موفقیت ساخته شد', 'success')
                    return redirect('products:home')
            else:  # return data to user for correction
                messages.add_message(request, 200, 'اطلاعات را چک کنید', 'warning')
                return render(request, self.template_name, {'form': form})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in UserRegisterVerifyView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class UserPasswordResetView(auth_views.PasswordResetView):  # uses Django generic views for simplicity
    template_name = 'accounts/user_password_reset_form.html'  # uses this template for processing view's logic
    success_url = reverse_lazy('accounts:user_password_reset_done')  # uses reverse_lazy because the url is not created yet
    email_template_name = 'accounts/user_password_reset_email.html'


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):  # uses Django generic views for simplicity
    template_name = 'accounts/user_password_reset_done.html'  # uses this template for processing view's logic


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):  # uses Django generic views for simplicity
    template_name = 'accounts/user_password_reset_confirm.html'  # uses this template for processing view's logic
    success_url = reverse_lazy('accounts:user_password_reset_complete')  # uses reverse_lazy because the url is not created yet


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):  # uses Django generic views for simplicity
    template_name = 'accounts/user_password_reset_complete.html'  # uses this template for processing view's logic


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/user_login.html'

    # this function helps us for dynamic logging, since we have 2-step logging method, we should implement this
    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')  # gets arguments after /?next=/ until & from GET environment(url) in request
        return super().setup(request, *args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.add_message(request, 200, 'وارد شدید', 'warning')
            return redirect('products:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):  # shows emtpy form to user
        try:
            return render(request, self.template_name, {'form': self.form_class()})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in UserLoginView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')

    def post(self, request):  # gets form from user to process
        try:
            form = self.form_class(request.POST)  # fills form with user's given information
            if form.is_valid():  # if data of form is valid then ...
                phone_number = form.cleaned_data.get('username')  # gets user_name field data as phone number from form
                password = form.cleaned_data.get('password')  # gets password field data from form
                # uses django built-in authenticate function to check whether we have user with given information
                user = authenticate(request, phone_number=phone_number, password=password)
                if user is not None:  # if so, then ...
                    random_code = create_unique_otp_code()  # creates random integer code for further processes
            # send_sms(phone_number, random_code)  # uses send_sms utility function to send phone number and code to user
                    messages.add_message(request, 200,
                f'send sms function is in line 139 of accounts.views and code is {random_code}', 'success')

                    # # if we have already same phone number in our database
                    if OtpCode.objects.filter(phone_number=phone_number).exists():
                        OtpCode.objects.filter(phone_number=phone_number).delete()  # deletes it

                    OtpCode.objects.create(phone_number=phone_number, code=random_code)  # inserts otp code to our database
                      # add user information to session section within request
                    request.session['user_information'] = {
                        'phone_number': phone_number,
                        'password': password,
                        'next_url': self.next,
                    }
                    messages.add_message(request, 200, 'کد یکبار مصرف با موفقیت ارسال شد', 'success')
                    return redirect('accounts:user_login_verify')  # redirects to next step
                else:  # if not, then ...
                    messages.add_message(request, 200, 'اطلاعات نامعتبر است', 'warning')
                    return redirect('accounts:user_login')  # redirects again to here

            else:  # if there's invalid data, then ...
                messages.add_message(request, 200, 'اطلاعات نامتعبر', 'warning')
                return render(request, self.template_name, {'form': form})  # gives form again to user to fill in

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in UserLoginView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class UserLoginVerifyView(View):
    form_class = OtpCodeForm
    template_name = 'accounts/user_login_verify.html'

    def get(self, request):  # shows form to user to fill in
        try:
            return render(request, self.template_name, {'form': self.form_class()})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in UserLoginVerifyView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')

    def post(self, request):  # gets information from user for next steps
        try:
            form = self.form_class(request.POST)  # fills form with user data
            if form.is_valid():  # if data of form is valid then ...
                user_information = request.session.get('user_information')  # gets information from session
                phone_number = user_information.get('phone_number')  # gets phone number from session
                password = user_information.get('password')  # gets password from session
                otp_instance = get_object_or_404(OtpCode, phone_number=phone_number)  # gets opt object from database
                user_code = form.cleaned_data.get('OtpCode')  # takes code from form
                now = timezone.now()  # creates now variable with help of datetime module
                otp_expires = otp_instance.created_at + datetime.timedelta(minutes=2)  # adds 2 minute expiration time

                if now > otp_expires:  # if otp_expires does expire, then ...
                    otp_instance.delete()  # removes opt object from our database
                    messages.add_message(request, 200, 'کد بکبار مصرف انقضا شده است', 'warning')
                    del request.session['user_information']  # removes related information from session
                    return redirect('accounts:user_login')  # redirects user to next phase

                if user_code != otp_instance.code:  # if user's given code is not same with opt code of database, then ...
                    messages.add_message(request, 200, 'کد یکبار مصرف نامعتبر است', 'warning')
                    return redirect('accounts:user_login_verify')  # redirects again to here

                # uses django built-in authenticate function to check whether we have user with given information
                user = authenticate(request, phone_number=phone_number, password=password)
                if user is not None:  # if so, then ...
                    cart_data = request.session.get('cart')  # gets cart data from session
                    login(request, user)  # logs in user
                    if cart_data is not None:  # inserts cart data again in session
                        request.session['cart'] = cart_data

                    messages.add_message(request, 200, 'وارد شدید', 'success')
                    otp_instance.delete()  # removes opt object from our database
                    next_url = user_information.get('next_url')  # takes next parameter in session
                    del request.session['user_information']  # removes related information from session
                    if next_url:  # if there's next parameter, then ...
                        return redirect(next_url)  # redirects user to next url

                    return redirect('products:home')

                else:  # if not, then ...
                    messages.add_message(request, 200, 'اطلاعات نامعتبر', 'warning')
                    return redirect('accounts:user_login')  # redirects user to last step

            else:  # if given information is not valid
                messages.add_message(request, 200, 'اطلاعات را چک کنید', 'warning')
                return render(request, self.template_name, {'form': form})  # gives form agin to user

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in UserLoginVerifyView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class UserLogoutView(View):  # logs out user
    def get(self, request):
        try:
            cart_data = request.session.get('cart')  # before logging out gets user's cart's info
            logout(request)
            if cart_data is not None:
                request.session['cart'] = cart_data  # then inserts it again into session

            messages.add_message(request, 200, 'خارج شدید', 'success')
            return redirect('products:home')  # redirects back to home page

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in UserLogoutView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


# uses Django generic views for simplicity and uses lazy loading, because next step has not been created yet
class UserPasswordChangeView(LoginRequiredMixin, auth_views.PasswordChangeView):
    template_name = 'accounts/user_password_change.html'
    success_url = reverse_lazy('accounts:user_password_change_done')


# uses Django generic views for simplicity
class UserPasswordChangeDoneView(LoginRequiredMixin, auth_views.PasswordChangeDoneView):
    template_name = 'accounts/user_password_change_done.html'