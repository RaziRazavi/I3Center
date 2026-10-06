from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from posts.models import Post, PostCategory, PostSeen, PostComment
from posts.forms import PostCommentForm, PostSearchForm
from utility.function import get_client_ip_address
from posts.filters import PostFilters
import logging
logger = logging.getLogger(__name__)


class CategoryView(View):
    template_name = 'posts/category_view.html'

    def get(self, request, *args, **kwargs):  # shows post category ...
        try:
            return render(request, self.template_name, {'categories': PostCategory.objects.all()})

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in CategoryView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class PostView(View):
    template_name = 'posts/post_view.html'
    form_class = PostSearchForm

    def get(self, request, pk=None, slug=None):  # does search, filter, pagination and shows them
        try:
            if pk is not None:  # gets posts and optimizes query
                posts = Post.objects.filter(category_id=pk).select_related('category')
            else:  # gets posts and optimizes query
                posts = Post.objects.all().select_related('category')

            # search operations
            search = request.GET.get('search')  # gets value of search from request.get
            form = self.form_class(request.GET) if search else self.form_class()  # fills form with given data if there's...
            if search and form.is_valid():  # if form is valid and there's value for search
                cd = form.cleaned_data.get('search')  # gets search value from cleaned data
                posts = posts.filter(Q(category__name__icontains=cd) | Q(name__icontains=cd)
                                            | Q(description__icontains=cd))  # gets posts based on given data

            # filter operations
            filters = PostFilters(request.GET, posts)  # sends data to postFilter
            posts = filters.qs  # puts result into posts

            # paginator operations
            paginating = Paginator(posts, 6)  # parses posts into each 6 parts
            page = request.GET.get('page')  # gets value of page from request.get
            posts = paginating.get_page(page)  # makes each page number which is given from last step have 6 posts

            # saving filters across page links
            query_params = request.GET.copy() # makes copy of request.get
            query_params.pop('page', None)  # deletes page from it. if not, deletes None
            context = {
                'posts': posts,
                'form': form,
                'query_params': query_params.urlencode(),  # encodes and sends to template
                'filters': filters,
            }
            return render(request, self.template_name, context)

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in PostView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class PostDetailsView(View):
    template_name = 'posts/post_details.html'
    form_class = PostCommentForm

    # gets post from database and optimizes query with select_related & prefetch related
    def setup(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
            Post.objects.select_related('author', 'category').prefetch_related('comments'),
            pk=kwargs.get('post_pk'))
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):  # (category_pk=None, category_slug=None, post_pk=None, post_slug=None)
        try:
            ip = get_client_ip_address(request) # summons this function
            if not PostSeen.objects.filter(ip_address__exact=ip, post=self.post_obj).exists():  # if not such an object
                PostSeen.objects.create(ip_address=ip, post=self.post_obj)  # creates one
                self.post_obj.views_count += 1
                self.post_obj.save()  # saves and updates post with new data
            context = {
                'post': self.post_obj,
                'comments': self.post_obj.comments.filter(is_reply=False),
                'replies': self.post_obj.comments.filter(is_reply=True),
                'form': self.form_class(),
            }
            return render(request, self.template_name, context)  # sends data to related template

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in PostDetailsView.get')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')

    @method_decorator(login_required)  # login is required here
    def post(self, request, *args, **kwargs): # manages collected data from user and operates on them
        try:
            form = self.form_class(request.POST)  # fills form class with data from request.post
            if form.is_valid():  # if form is valid ...
                comment = form.save(commit=False)
                comment.post = self.post_obj
                comment.author = request.user
                comment_father = request.POST.get('parent_id')  # gets value of parent id from request.post
                if comment_father:  # if there's such a thing ....
                    comment.parent = get_object_or_404(PostComment, id=comment_father)  # fills parent field with this
                    comment.is_reply = True  # sets is reply field to true

                comment.save()  # saves postComment
                self.post_obj.comments_count += 1
                self.post_obj.save() # saves and updates post with new info
                messages.add_message(request, 200, 'کامنت اضافه شد', 'success')
                return redirect(self.post_obj.get_absolute_url())  # redirects to this url
            else:  # if form isn't valid ...
                messages.add_message(request, 200, 'اطلاعات نامعتبر است', 'warning')
                context = {
                    'post': self.post_obj,
                    'comments': self.post_obj.comments.filter(is_reply=False),
                    'replies': self.post_obj.comments.filter(is_reply=True),
                    'form': self.form_class(request.POST),
                }
                return render(request, self.template_name, context)  # shows back to user

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in PostDetailsView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class PostLoveView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):  # operates base on collected data from user
        try:
            post = get_object_or_404(Post.objects.prefetch_related('lovers'), id=kwargs.get('pk')) # gets post & optimizes query
            if post.lovers.filter(id=request.user.id).exists():  # if there's such a user...
                post.lovers.remove(request.user)  # removes it from there
                if post.likes_count >= 1:  # if number of likes count field is bigger than 1 ...
                    post.likes_count -= 1  # deducts one
                else:  # otherwise
                    post.likes_count = 0  # sets zero
            else:  # if there's no such a user ...
                post.lovers.add(request.user)  # adds user to among lovers
                post.likes_count += 1  # adds one
            post.save()  # saves and updates post
            return redirect(post.get_absolute_url())  # redirect to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in PostLoveView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class PostCommentLoveView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):  # handles data comes from user
        try:
            comment = get_object_or_404(PostComment.objects.prefetch_related('lovers', 'haters'), id=kwargs.get('pk'))
            if comment.haters.filter(id=request.user.id).exists():  # if there's such a user among haters...
                comment.haters.remove(request.user)  # removes it

            if comment.lovers.filter(id=request.user.id).exists():  # if there's such a user among lovers...
                comment.lovers.remove(request.user)  # removes it
            else:  # otherwise ....
                comment.lovers.add(request.user)  # adds user to them

            return redirect(comment.post.get_absolute_url())  # redirects to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in PostCommentLoveView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')


class PostCommentHateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):  # manages collected data from user
        try:
            comment = get_object_or_404(PostComment.objects.prefetch_related('lovers', 'haters'), id=kwargs.get('pk'))
            if comment.lovers.filter(id=request.user.id).exists(): # if there's such a user among lovers...
                comment.lovers.remove(request.user)  # removes it

            if comment.haters.filter(id=request.user.id).exists(): # if there's such a user among haters...
                comment.haters.remove(request.user)  # removes it
            else:  # otherwise ....
                comment.haters.add(request.user)  # adds user to them

            return redirect(comment.post.get_absolute_url())  # redirect to this url

        except Exception:  # if an unexpected error is occurred, saves it to log file and redirects user to home page
            logger.exception('unexpected error in PostCommentHateView.post')
            messages.add_message(request, 200, 'مشکلی پیش آمده است', 'danger')
            return redirect('products:home')
