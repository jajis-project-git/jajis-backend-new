from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone


class BannerImage(models.Model):
    
    image = models.ImageField(upload_to="banner_image/",null=True,blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"


class Saloon(models.Model):

    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='saloon_images/')
    image1=models.ImageField(upload_to='saloon_images/',blank=True,null=True)
    image2=models.ImageField(upload_to='saloon_images/',blank=True,null=True)
    image3=models.ImageField(upload_to='saloon_images/',blank=True,null=True)
    image4=models.ImageField(upload_to='saloon_images/',blank=True,null=True)
    image5=models.ImageField(upload_to='saloon_images/',blank=True,null=True)
    image6=models.ImageField(upload_to='saloon_images/',blank=True,null=True)
    google_map_url=models.CharField(max_length=1000,null=True,blank=True)
    location = models.CharField(max_length=300)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Saloon"
        verbose_name_plural = "Saloon"
    

class FoodMenu(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='food_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Food Menu"
        verbose_name_plural = "Food Menu"

    
class Cosmetics(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='cosmetics_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Cosmetic"
        verbose_name_plural = "Cosmetics"


class Courses(models.Model):

    image=models.ImageField(upload_to='courses/')
    course=models.CharField(max_length=100)
    duration=models.CharField(max_length=100)
    description=models.TextField()

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"



# -------------e-commerse--------------------------
class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    title = models.CharField(max_length=255)
    description = models.TextField()
    brand = models.CharField(max_length=100, blank=True, null=True,default="jajis")

    image1 = models.ImageField(upload_to='product_images/')
    image2 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image4 = models.ImageField(upload_to='product_images/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)

    quantity_label = models.CharField(max_length=50)

    mrp = models.DecimalField(max_digits=10, decimal_places=2)      
    price = models.DecimalField(max_digits=10, decimal_places=2)    

    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.product.title} - {self.quantity_label}"
    




class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'variant')

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.variant.price





class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"



class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="wishlist_items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('wishlist', 'variant')

    def __str__(self):
        return f"{self.variant.product.title} - {self.variant.quantity_label}"



class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=100, null=True, blank=True)  
    line1 = models.CharField(max_length=255) 
    line2 = models.CharField(max_length=255, null=True, blank=True) 
    city = models.CharField(max_length=100)  
    state = models.CharField(max_length=100, null=True, blank=True) 
    postal_code = models.CharField(max_length=20)  
    country = models.CharField(max_length=100, default="India")
    phone = models.CharField(max_length=30, null=True, blank=True) 
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.label or self.line1}"



class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name="+")
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name="+")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    payment_method = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=50, default="unpaid")

    transaction_id = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Order {self.order.id} - {self.variant}"


class PaymentTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=200)
    razorpay_payment_id = models.CharField(max_length=200, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default="created")

    shipping_address_id = models.IntegerField(null=True, blank=True)
    billing_address_id = models.IntegerField(null=True, blank=True)

    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    class Meta:
        verbose_name = "Password Reset OTP"
        verbose_name_plural = "Password Reset OTPs"
