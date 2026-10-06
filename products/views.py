from django.db.models import Q
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product, Comment, Category, ProductSeen
from django.contrib import messages
from products.forms import CommentForm, SearchForm, ContactUsForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from orders.forms import CartForm
from utility.function import get_client_ip_address
from products.filters import ProductsFilter
from django.core.paginator import Paginator
from posts.models import Post
import logging
logger = logging.getLogger(__name__)


class HomeView(View):
    template_name = 'products/home.html'

    def get(self, request):  # sends data to related template
        try:
            products = Product.objects.filter(available=True)
            discounts = products.filter(has_discount=True).order_by('-discount')[:10]
            visits = products.order_by('-views_count')[:10]
            favorites = products.order_by('-favorites_count')[:10]
            news = products.order_by('-created_at')[:10]
            sales = products.order_by('-sales_count')[:10]
            articles = Post.objects.all().order_by('-views_count')[:5]
            context = {
                'products': products,
                'discounts': discounts,
                'visits': visits,
                'favorites':favorites,
                'news': news,
                'sales': sales,
                'articles': articles,
            }
            return render(request, self.template_name, context)

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to server error page
            logger.exception('unexpected error in HomeView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return render(request, '500.html', status=500)

class ProductView(View):
    template_name = 'products/product_view.html'
    form_class = SearchForm

    def get(self, request, pk=None, slug=None):  # # does search, filter, pagination and shows them
        try:
            if pk is not None: # gets products and optimizes query
                products = Product.objects.filter(category_id=pk).select_related('category') # this aims for category
                if not products:  # this aims for sub category
                    products = Product.objects.filter(category__parent_id=pk).select_related('category')
            else:  # gets products and optimizes query
                products = Product.objects.all().select_related('category') # this aims for all products

            # search operations
            search = request.GET.get('search')  # gets value of search from request.get
            form = self.form_class(request.GET) if search else self.form_class() # fills form with given data if there's...
            if search and form.is_valid(): # if form is valid and there's value for search
                search = form.cleaned_data.get('search') # gets search value from cleaned data
                products = products.filter(Q(name__icontains=search) | Q(description__icontains=search)
                    | Q(brand__name__icontains=search) | Q(category__name__icontains=search)
                    | Q(material__name__icontains=search) | Q(category__parent__name__icontains=search))

            # filter operations
            filters = ProductsFilter(request.GET, queryset=products) # sends data to productFilter
            products = filters.qs # puts result into posts

            # paginator operations
            paginating = Paginator(products, 10) # parses products into each 10 parts
            page = request.GET.get('page') # gets value of page from request.get
            products = paginating.get_page(page) # makes each page number which is given from last step have 10 products

            # saving filters across page links
            query_params = request.GET.copy()  # makes copy of request.get
            query_params.pop('page', None)  # deletes page from it. if not, deletes None
            context = {
                'products': products,
                'filters': filters,
                'query_params': query_params.urlencode(),  # encodes and sends to template
                'search_form': form,
            }
            return render(request, self.template_name, context)

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in ProductView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class ProductDetailsView(View):
    template_name = 'products/product_details.html'
    form_class = CommentForm
    form_class2 = CartForm

    # gets data from database and optimizes database query with selec_related(forward-foreignkey) & prefetch_related(reverse)
    def setup(self, request, *args, **kwargs):
        self.product = get_object_or_404(
            Product.objects.select_related('brand', 'material', 'category').prefetch_related('comments', 'variants'),
            id=kwargs.get('pk'))
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            images = [ item for item in self.product.extra_images.all()]
            images.append(self.product) # gets and creates image variable for images
            ip = get_client_ip_address(request) # summons this function
            if not ProductSeen.objects.filter(ip_address__exact=ip, product=self.product).exists(): # if not such an object
                ProductSeen.objects.create(ip_address=ip, product=self.product) # creates one
                self.product.views_count += 1
                self.product.save()  # saves and updates post with new data
            context = {
                'images': images,
                'product': self.product,
                'variants': self.product.variants.filter(available=True),
                'comments': self.product.comments.filter(is_reply=False),
                'replies': self.product.comments.filter(is_reply=True),
                'form': self.form_class(),
                'cart_form': self.form_class2(),
            }
            return render(request, self.template_name, context)

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in ProductDetailsView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')

    @method_decorator(login_required)  # login is required here
    def post(self, request, *args, **kwargs):  # manages collected data from user and operates on them
        try:
            images = [item for item in self.product.extra_images.all()]
            images.append(self.product) # gets images and creates variable for that
            form = self.form_class(request.POST) # fills form with data from request.post
            if form.is_valid():  # if form is valid ...
                comment = form.save(commit=False)
                comment.product = self.product
                comment.user = request.user
                comment_father = request.POST.get('parent_id') # gets value of parent id from request.post
                if comment_father:
                    comment.parent = get_object_or_404(Comment, id=comment_father)  # fills parent field with this
                    comment.is_reply = True  # sets is reply field to true

                comment.save()  # saves comment
                messages.add_message(request, 200, 'کامنت اضافه شد', 'success')
                return redirect(self.product.get_absolute_url())  # redirects to this url
            else:  # if form isn't valid ...
                messages.add_message(request, 200, 'اطلاعات نامعتبر است', 'warning')
                context = {
                    'images': images,
                    'product': self.product,
                    'variants': self.product.variants.filter(available=True),
                    'comments': self.product.comments.filter(is_reply=False),
                    'replies': self.product.comments.filter(is_reply=True),
                    'form': self.form_class(request.POST),
                    'cart_form': self.form_class2(),
                }
                return render(request, self.template_name, context) # shows back to user

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in ProductDetailsView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class ProductLikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):   # operates base on collected data from user
        try:
            product = get_object_or_404(Product.objects.prefetch_related('likers'), id=kwargs.get('pk')) # gets & optimizes query
            if product.likers.filter(id=request.user.id).exists(): # if there's such a user...
                product.likers.remove(request.user) # removes it from there
                if product.favorites_count >= 1: # if number of favorite count field is bigger than 1 ...
                    product.favorites_count -= 1  # deducts one
                else:  # otherwise
                    product.favorites_count = 0 # sets zero
            else:  # if there's no such a user ...
                product.likers.add(request.user)  # adds user to among likers
                product.favorites_count += 1  # adds one
            product.save()  # saves and updates post
            return redirect(product.get_absolute_url())  # redirect to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in ProductLikeView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class CommentLikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs): # handles data comes from user
        try:
            comment = get_object_or_404(Comment.objects.prefetch_related('likers', 'dislikers'), id=kwargs.get('pk'))
            if comment.dislikers.filter(id=request.user.id).exists(): # if there's such a user among dislikers...
                comment.dislikers.remove(request.user) # removes it

            if comment.likers.filter(id=request.user.id).exists(): # if there's such a user among liker...
                comment.likers.remove(request.user) # removes it
            else: # otherwise ...
                comment.likers.add(request.user) # adds user to them

            return redirect(comment.product.get_absolute_url())  # redirects to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in CommentLikeView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class CommentDislikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):  # manages collected data from user
        try:
            comment = get_object_or_404(Comment.objects.prefetch_related('likers', 'dislikers'), id=kwargs.get('pk'))
            if comment.likers.filter(id=request.user.id).exists():  # if there's such a user among likers...
                comment.likers.remove(request.user)  # removes it

            if comment.dislikers.filter(id=request.user.id).exists(): # if there's such a user among dislikers...
                comment.dislikers.remove(request.user) # removes it
            else: # otherwise ..
                comment.dislikers.add(request.user)  # adds user to them

            return redirect(comment.product.get_absolute_url()) # redirects to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in CommentDislikeView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class CategoryView(View):
    template_name = 'products/category_view.html'

    def get(self, request, pk=None, slug=None):  # shows product category ...
        try:
            if pk: # if url has pk in it ...
                children = Category.objects.filter(parent_id=pk) # gets possible children
                if children.exists(): # if does have it ...
                    context = {
                        'categories': children,
                    }
                else: # if it doesn't have ...
                    return redirect('products:view_from_category', pk=pk, slug=slug) # redirects to this url
            else: # if it doesn't have pk in url ...
                context = {
                    'categories': Category.objects.filter(is_parent=True),
                }

            return render (request, self.template_name, context) # sends data to related template

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in CategoryView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class FAQView(View):
    template_name = 'products/faq.html'

    def get(self, request, *args, **kwargs): # shows related template
        try:
            return render(request, self.template_name)

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in FAQView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class AboutUsView(View):
    template_name = 'products/about_us.html'

    def get(self, request, *args, **kwargs): # shows related template
        try:
            return render(request, self.template_name)

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in AboutUsView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class ContactUsView(View):
    template_name = 'products/contact_us.html'
    form_class = ContactUsForm

    def get(self, request, *args, **kwargs): #  shows related template and sends form class to it
        try:
            return render(request, self.template_name, {'form': self.form_class()})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in ContactUsView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')

    def post(self, request, *args, **kwargs):  # processes collected data from user
        try:
            form = self.form_class(request.POST) # fills form class with data from request.post
            if not form.is_valid():  # if data in form isn't valid
                messages.add_message(request, 200, 'اطلاعات نامعتبر است', 'warning')
                return render(request, self.template_name, {'form': form}) # sends back to user

            form.save() # saves it in contactUs table
            messages.add_message(request, 200, 'پیام ارسال شد', 'success')
            return redirect('products:home')  # redirects to home page

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in ContactUsView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')