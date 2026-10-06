from products.models import Variant


CART_SESSION_KEY = 'cart'


class Cart:
    def __init__(self, request):  # initializes the cart inside session, if there's no cart, function creates it
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not cart:
            self.session[CART_SESSION_KEY] = {}
            cart = self.session[CART_SESSION_KEY]

        self.cart = cart


    def __iter__(self):  # makes cart iterable
        variants_ids = self.cart.keys()  # gets cart keys
        variants = Variant.objects.filter(id__in=variants_ids)  # gets all variants which have id from variant_ids
        cart = self.cart.copy()  # makes copy of cart
        for variant in variants:  # inserts below data inside cart/cart.id
            cart[str(variant.id)]['variant'] = variant.name
            cart[str(variant.id)]['variant_id'] = variant.id
            cart[str(variant.id)]['color'] = variant.color.name
            cart[str(variant.id)]['size'] = variant.size.name
            cart[str(variant.id)]['stock'] = variant.stock
            cart[str(variant.id)]['price'] = variant.final_price
            cart[str(variant.id)]['product_url'] = variant.product.get_absolute_url()
            cart[str(variant.id)]['product_name'] = variant.product.name
            cart[str(variant.id)]['product_picture'] = variant.product.get_image_src()

        for value in cart.values():  # gets values of price and quantity and calculate total price inside its value
            value['total_price'] = int(value['price']) * int(value['quantity'])
            yield value


    def __len__(self):  # answers if cart exists inside session
        return len(self.cart)


    def save(self):  # helps to save data inside cart when we have deep inside changes
        self.session.modified = True


    def add(self, variant, quantity):  # adds quantity to related variable inside cart
        if quantity == 0:  # validates quantity
            raise ValueError('تعداد نمی تواند صفر باشد')
        if quantity < 0:  # validates quantity
            raise ValueError('تعداد نمی تواند کمتر از صفر باشد')

        variant_id = str(variant.id)
        if variant_id not in self.cart:  # checks whether variant.id exists in cart, creates one in case we don't have it
            self.cart[variant_id] = {
                'variant': variant.name,
                'price': str(variant.final_price),
                'quantity': 0,
            }

        current_quantity = self.cart.get(variant_id).get('quantity')  # gets quantity of related variant
        new_quantity = current_quantity + quantity  # accumulates quantity
        if new_quantity > variant.stock:  # checks new quantity doesn't exceed variant stock
            raise ValueError(f'تعداد نمی تواند بیش تر از {variant.stock} (تعداد متغیر)')

        self.cart[variant_id]['quantity'] = new_quantity  # sets new quantity as quantity for related variant
        self.save()  # saves it


    def remove(self, variant):  # deletes related variant from cart
        variant_id = str(variant.id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()
        else:
            raise ValueError(f'{variant.name} در کارت نیست')  # raises a valueError just in case there's not variant inside


    def remove_one(self, variant):  # removes one quantity from related variant in cart
        variant_id = str(variant.id)
        if variant_id not in self.cart: # checks if variant.id exists in cart, raises an error in case there's none
            raise ValueError(f'{variant.name} موجود نمی باشد ')

        if self.cart[variant_id]['quantity'] <= 0:  # checks whether quantity of variant.id exists in cart
            raise ValueError('تعداد نمی تواند کمتر از صفر باشد')  # raises an error when it is less than zero

        self.cart[variant_id]['quantity'] -= 1  # subtracts one from variant
        if self.cart[variant_id]['quantity'] == 0:  # if quantity is zero, deletes it
            del self.cart[variant_id]

        self.save()  # saves cart


    def get_total_price(self):  # calculates total price of all items within cart
        return sum(int(value['price']) * int(value['quantity']) for value in self.cart.values())

    def get_total_quantity(self):  # calculates total quantities of all items in cart
        return sum(int(value['quantity']) for value in self.cart.values())