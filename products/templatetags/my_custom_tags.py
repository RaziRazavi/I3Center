from django import template


register = template.Library()


@register.filter(name='comment_like_checker')
def comment_like_checker(comment, user_id):
    if comment.likers.filter(id=user_id).exists():
        return '-fill'
    else:
        return ''


@register.filter(name='comment_dislike_checker')
def comment_dislike_checker(comment, user_id):
    if comment.dislikers.filter(id=user_id).exists():
        return '-fill'
    else:
        return ''


@register.filter(name='product_like_checker')
def product_like_checker(product, user_id):
    if product.likers.filter(id=user_id).exists():
        return '-fill'
    else:
        return ''


@register.filter(name='post_love_checker')
def post_love_checker(post, user_id):
    return '-fill 'if post.lovers.filter(id=user_id).exists() else ''


@register.filter(name='post_comment_love_checker')
def post_comment_love_checker(post_comment, user_id):
    return '-fill' if post_comment.lovers.filter(id=user_id).exists() else ''


@register.filter(name='post_comment_hate_checker')
def post_comment_hate_checker(post_comment, user_id):
    return '-fill' if post_comment.haters.filter(id=user_id).exists() else ''
