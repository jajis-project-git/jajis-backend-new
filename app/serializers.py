from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .models import (
    BannerImage, Cosmetics, Saloon, FoodMenu, Courses,
    Product, ProductVariant, Category, Cart, CartItem,
    Wishlist, WishlistItem, Address, Order, OrderItem,
    PaymentTransaction, PasswordResetOTP,
)

# ======================================================
# COMMON IMAGE HELPER (DRY + SAFE)
# ======================================================

class AbsoluteImageMixin:
    def get_abs_url(self, request, image):
        if image:
            return request.build_absolute_uri(image.url) if request else image.url
        return None


# ======================================================
# BASIC MODELS
# ======================================================

class BannerImageSerializer(serializers.ModelSerializer, AbsoluteImageMixin):
    image = serializers.SerializerMethodField()

    class Meta:
        model = BannerImage
        fields = "__all__"

    def get_image(self, obj):
        return self.get_abs_url(self.context.get("request"), obj.image)


class SaloonSerializer(serializers.ModelSerializer, AbsoluteImageMixin):
    image = serializers.SerializerMethodField()
    image1 = serializers.SerializerMethodField()
    image2 = serializers.SerializerMethodField()
    image3 = serializers.SerializerMethodField()
    image4 = serializers.SerializerMethodField()
    image5 = serializers.SerializerMethodField()
    image6 = serializers.SerializerMethodField()

    class Meta:
        model = Saloon
        fields = "__all__"

    def get_image(self, obj): return self.get_abs_url(self.context.get("request"), obj.image)
    def get_image1(self, obj): return self.get_abs_url(self.context.get("request"), obj.image1)
    def get_image2(self, obj): return self.get_abs_url(self.context.get("request"), obj.image2)
    def get_image3(self, obj): return self.get_abs_url(self.context.get("request"), obj.image3)
    def get_image4(self, obj): return self.get_abs_url(self.context.get("request"), obj.image4)
    def get_image5(self, obj): return self.get_abs_url(self.context.get("request"), obj.image5)
    def get_image6(self, obj): return self.get_abs_url(self.context.get("request"), obj.image6)


class FoodMenuSerializer(serializers.ModelSerializer, AbsoluteImageMixin):
    image = serializers.SerializerMethodField()

    class Meta:
        model = FoodMenu
        fields = ["id", "title", "description", "image", "price"]

    def get_image(self, obj):
        return self.get_abs_url(self.context.get("request"), obj.image)


class CosmeticsSerializer(serializers.ModelSerializer, AbsoluteImageMixin):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Cosmetics
        fields = ["id", "title", "description", "image", "price"]

    def get_image(self, obj):
        return self.get_abs_url(self.context.get("request"), obj.image)


class CourseSerializer(serializers.ModelSerializer, AbsoluteImageMixin):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Courses
        fields = "__all__"

    def get_image(self, obj):
        return self.get_abs_url(self.context.get("request"), obj.image)


# ======================================================
# AUTH SERIALIZERS
# ======================================================

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"]
        )
        Token.objects.get_or_create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        data["user"] = user
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "date_joined"]
        read_only_fields = fields


# ======================================================
# CATEGORY / PRODUCT / VARIANT
# ======================================================

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductInCartSerializer(serializers.ModelSerializer, AbsoluteImageMixin):
    image1 = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "title", "brand", "image1"]

    def get_image1(self, obj):
        return self.get_abs_url(self.context.get("request"), obj.image1)


class ProductVariantSerializer(serializers.ModelSerializer):
    product = ProductInCartSerializer(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ["id", "quantity_label", "mrp", "price", "stock", "sku", "product"]


class ProductListSerializer(serializers.ModelSerializer, AbsoluteImageMixin):
    category = CategorySerializer(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    image1 = serializers.SerializerMethodField()
    image2 = serializers.SerializerMethodField()
    image3 = serializers.SerializerMethodField()
    image4 = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "title", "brand",
            "image1", "image2", "image3", "image4",
            "category", "category_name", "variants",
        ]

    def get_image1(self, obj): return self.get_abs_url(self.context.get("request"), obj.image1)
    def get_image2(self, obj): return self.get_abs_url(self.context.get("request"), obj.image2)
    def get_image3(self, obj): return self.get_abs_url(self.context.get("request"), obj.image3)
    def get_image4(self, obj): return self.get_abs_url(self.context.get("request"), obj.image4)


class ProductDetailSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ["description"]


# ======================================================
# CART
# ======================================================

class CartItemSerializer(serializers.ModelSerializer, AbsoluteImageMixin):
    variant = ProductVariantSerializer(read_only=True)
    total_price = serializers.FloatField(read_only=True)
    product_title = serializers.CharField(source="variant.product.title", read_only=True)
    product_brand = serializers.CharField(source="variant.product.brand", read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id", "variant",
            "product_title", "product_brand",
            "product_image", "quantity", "total_price",
        ]

    def get_product_image(self, obj):
        return self.get_abs_url(self.context.get("request"), obj.variant.product.image1)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "cart_total"]

    def get_cart_total(self, obj):
        return sum(item.total_price for item in obj.items.all())


# ======================================================
# WISHLIST
# ======================================================

class WishlistItemSerializer(serializers.ModelSerializer, AbsoluteImageMixin):
    variant = ProductVariantSerializer(read_only=True)
    product_title = serializers.CharField(source="variant.product.title", read_only=True)
    product_brand = serializers.CharField(source="variant.product.brand", read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = ["id", "variant", "product_title", "product_brand", "product_image"]

    def get_product_image(self, obj):
        return self.get_abs_url(self.context.get("request"), obj.variant.product.image1)


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True, source="wishlist_items")

    class Meta:
        model = Wishlist
        fields = ["id", "items"]


# ======================================================
# ADDRESS / ORDER
# ======================================================

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'label', 'line1', 'line2', 'city', 'state', 'postal_code', 'country', 'phone', 'is_default']
        read_only_fields = ['id']
        extra_kwargs = {
            'label': {'allow_null': True, 'allow_blank': True, 'required': False},
            'line1': {'required': True},
            'line2': {'allow_null': True, 'allow_blank': True, 'required': False},
            'city': {'required': True},
            'state': {'allow_null': True, 'allow_blank': True, 'required': False},
            'postal_code': {'required': True},
            'country': {'required': False},
            'phone': {'allow_null': True, 'allow_blank': True, 'required': False},
            'is_default': {'required': False},
        }

        

class OrderItemSerializer(serializers.ModelSerializer, AbsoluteImageMixin):
    variant = ProductVariantSerializer(read_only=True)
    product_title = serializers.CharField(source="variant.product.title", read_only=True)
    product_brand = serializers.CharField(source="variant.product.brand", read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id", "variant", "product_title",
            "product_brand", "product_image",
            "quantity", "unit_price", "total_price",
        ]

    def get_product_image(self, obj):
        return self.get_abs_url(self.context.get("request"), obj.variant.product.image1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    razorpay_order_id = serializers.SerializerMethodField()
    razorpay_payment_id = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]

    def _tx(self, obj):
        return PaymentTransaction.objects.filter(order=obj).order_by("-created_at").first()

    def get_razorpay_order_id(self, obj):
        tx = self._tx(obj)
        return tx.razorpay_order_id if tx else None

    def get_razorpay_payment_id(self, obj):
        tx = self._tx(obj)
        return tx.razorpay_payment_id if tx else None


class OrderListSerializer(OrderSerializer):
    first_product_image = serializers.SerializerMethodField()
    first_product_title = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()

    class Meta(OrderSerializer.Meta):
        fields = [
            "id", "total_amount", "status", "payment_status",
            "payment_method", "transaction_id",
            "razorpay_order_id", "razorpay_payment_id",
            "created_at", "updated_at",
            "first_product_image", "first_product_title",
            "items_count", "items",
            "shipping_address", "billing_address",
        ]

    def get_first_product_image(self, obj):
        first_item = obj.items.first()
        if first_item:
            return self.context.get("request").build_absolute_uri(first_item.variant.product.image1.url)
        return None

    def get_first_product_title(self, obj):
        first_item = obj.items.first()
        return first_item.variant.product.title if first_item else None

    def get_items_count(self, obj):
        return obj.items.count()
