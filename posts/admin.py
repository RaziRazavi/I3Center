from django.contrib import admin
from posts.models import Post, PostCategory, PostSeen, PostComment


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'created_at_jalali', 'updated_at_jalali')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'author', 'comments_count', 'views_count', 'likes_count',
                    'created_at_jalali', 'updated_at_jalali')
    search_fields = ('name',)
    list_filter = ('category__name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PostSeen)
class PostSeenAdmin(admin.ModelAdmin):
    list_display = ('post', 'ip_address', 'created_at_jalali', 'updated_at_jalali')
    search_fields = ('post__name',)


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_reply', 'total_lovers', 'total_haters', 'created_at_jalali',
                    'updated_at_jalali')
    search_fields = ('post__name',)
