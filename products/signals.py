from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Variant, PriceChange, Product
from orders.models import Order, OrderItem
from django.utils import timezone
from django.db import transaction


def price_change(instance, **kwargs):  # this function inserts new data in PriceChange model
    new = None
    if kwargs.get('created'):  # if there's created inside kwargs...
        new = PriceChange.objects.create(variant=instance, price=instance.final_price)  # creates record inside priceChange table
    else: # if not ...
        last_price = PriceChange.objects.filter(variant=instance).order_by('-created_at').first() # gets related last price
        if last_price is None or instance.final_price != last_price.price: # if there's no last price or last price doesn't match
            if PriceChange.objects.filter(variant=instance, created_at__date=timezone.localdate()).exists(): # new price per day
                PriceChange.objects.filter(variant=instance, created_at__date=timezone.localdate()).delete()

            new = PriceChange.objects.create(variant=instance, price=instance.final_price) # creates new record in priceChange

    if new is not None: # if new has value...
        orders = Order.objects.filter(order_items__variant=instance, paid=False)  # get related orders
        if orders is not None: # if there are orders ...
            with transaction.atomic():  # holds database until whole block renders successfully
                for order in orders:  # does some tasks ...
                    order_item = OrderItem.objects.get(order=order, variant=instance)  # gets related orderItem...
                    order_item.price = instance.final_price
                    order_item.save() # modifies and saves orderItem
                    order.base_price = order.order_current_total_price
                    order.save()  # modifies and saves order


@receiver(post_save, sender=Variant)  # after Variant model saves something this function operates
def variant_price_change_signal(sender, instance, **kwargs):
    price_change(instance=instance, **kwargs)


@receiver(post_save, sender=Product)  # after Product model saves something this function operates
def product_price_change_signal(sender, instance, **kwargs):
    variants = Variant.objects.filter(product=instance)  # gets all variants of that product
    for variant in variants:  # for every variant...
        price_change(instance=variant, **kwargs)  # does this
