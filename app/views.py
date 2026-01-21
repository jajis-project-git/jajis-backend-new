# views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import BannerImage,Saloon,FoodMenu,Courses,Cart,CartItem,Category,Product,ProductVariant,Wishlist,WishlistItem,PasswordResetOTP
from .serializers import BannerImageSerializer,SaloonSerializer,FoodMenuSerializer,CourseSerializer,CartItemSerializer,CartSerializer

from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    ProductListSerializer,
    CategorySerializer,
    ProductDetailSerializer,
    WishlistSerializer,
    AddressSerializer,
    OrderItemSerializer,
    OrderListSerializer,
    OrderSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UserProfileSerializer,
)
from .models import Category, Product, ProductVariant,WishlistItem,Wishlist,Order,OrderItem,PaymentTransaction,Address

from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction
from django.conf import settings
import razorpay
from django.shortcuts import get_object_or_404
from .email import send_password_reset_otp_email
from django.utils import timezone
from datetime import timedelta
import random
import string
from django.contrib.auth.models import User




class home(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        latest_image = BannerImage.objects.order_by('-uploaded_at').first()
        serializer = (
            BannerImageSerializer(latest_image, context={'request': request})
            if latest_image else None
        )

        return Response({
            "page": "Home",
            "content": "This is the Home page.",
            "video": serializer.data if serializer else None
        })


# --------------------------------------------------
# SALONS
# --------------------------------------------------

class salons_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        salon = Saloon.objects.all()
        serializer = SaloonSerializer(salon, many=True, context={'request': request})

        return Response({
            "page": "Salons page",
            "data": serializer.data
        })


class salons_detail_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        salon = get_object_or_404(Saloon, id=id)
        serializer = SaloonSerializer(salon, context={'request': request})

        return Response({
            "page": "Salon Detail",
            "data": serializer.data
        })


# --------------------------------------------------
# FOOD
# --------------------------------------------------

class Food_menu_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        food_items = FoodMenu.objects.all()
        serializer = FoodMenuSerializer(food_items, many=True, context={'request': request})

        return Response({
            "page": "Food Menu",
            "data": serializer.data
        })


class food_court_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        food_items = FoodMenu.objects.all()
        serializer = FoodMenuSerializer(food_items, many=True, context={'request': request})

        return Response({
            "page": "Food Menu",
            "data": serializer.data
        })


# --------------------------------------------------
# STATIC PAGES
# --------------------------------------------------

class cosmetics_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "page": "Cosmetics",
            "content": "This is the Cosmetics page."
        })


class event_hall_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "page": "Event Hall",
            "content": "This is the Event Hall page."
        })


class designing_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "page": "Designing & Stitching",
            "content": "This is the Designing & Stitching page."
        })


class franchise_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "page": "Franchise",
            "content": "This is the Franchise page."
        })


class about_us_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "page": "About Us",
            "content": "This is the About Us page."
        })


class contact_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "page": "Contact",
            "content": "This is the Contact page."
        })


class Buy_productes_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "page": "Buy Products",
            "content": "This is the Buy Products page."
        })


# --------------------------------------------------
# ACADEMY
# --------------------------------------------------

class academy_view(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        courses = Courses.objects.all()
        course_serializer = CourseSerializer(
            courses, many=True, context={"request": request}
        )

        return Response({
            "page": "course",
            "data": course_serializer.data
        })



# --------------------------ecommerse----------------------------







class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user)
            return Response({
                "message": "Signup successful",
                "token": token.key
            }, status=201)
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message":"Login successful",
                "token": token.key
            })
        return Response(serializer.errors, status=400)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()   # Delete token
        return Response({"message": "Logged out"}, status=200)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"message": "If the email exists, an OTP has been sent."}, status=200)
            
            # Generate OTP
            otp = ''.join(random.choices(string.digits, k=6))
            expires_at = timezone.now() + timedelta(minutes=10)
            
            # Save OTP
            PasswordResetOTP.objects.create(email=email, otp=otp, expires_at=expires_at)
            
            # Send email
            try:
                send_password_reset_otp_email(user, otp)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Email sending failed for {email}: {str(e)}")
                # Don't expose email error to user, but log it for debugging
            
            return Response({"message": "OTP sent to your email."}, status=200)
        return Response(serializer.errors, status=400)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            
            try:
                otp_obj = PasswordResetOTP.objects.get(email=email, otp=otp)
            except PasswordResetOTP.DoesNotExist:
                return Response({"message": "Invalid OTP."}, status=400)
            
            if otp_obj.is_expired():
                otp_obj.delete()
                return Response({"message": "OTP has expired."}, status=400)
            
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                otp_obj.delete()
                return Response({"message": "Password reset successful."}, status=200)
            except User.DoesNotExist:
                return Response({"message": "User not found."}, status=400)
        return Response(serializer.errors, status=400)




class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


# -----------------------------------



from django.db.models import Min, Q

class ProductListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        category_name = request.GET.get("category")
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        search = request.GET.get("search")

        products = Product.objects.all()

        # 🔹 Category filter
        if category_name and category_name.lower() != "all":
            products = products.filter(category__name__iexact=category_name)

        if search:
            products = products.filter(title__icontains=search)

        products = products.annotate(
            lowest_price=Min("variants__price")
        )

        if min_price:
            products = products.filter(lowest_price__gte=min_price)

        if max_price:
            products = products.filter(lowest_price__lte=max_price)

        products = products.distinct().order_by("-created_at")

        serializer = ProductListSerializer(
            products,
            many=True,
            context={"request": request}
        )

        categories = Category.objects.all()
        category_serializer = CategorySerializer(categories, many=True)

        return Response(
            {
                "products": serializer.data,
                "categories": category_serializer.data,
            },
            status=status.HTTP_200_OK,
        )





class ProductDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductDetailSerializer(product, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        



class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        variant_id = request.data.get("variant_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response({"error": "Variant not found"}, status=404)

        if variant.stock < quantity:
            return Response({"error": "Not enough stock"}, status=400)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not item_created:
            if cart_item.quantity + quantity > variant.stock:
                return Response({"error": "Stock limit reached"}, status=400)

            cart_item.quantity += quantity
            cart_item.save()

        return Response({"message": "Added to cart successfully"}, status=200)



class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")
        quantity = int(request.data.get("quantity"))

        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)

        if quantity < 1:
            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=200)

        if quantity > cart_item.variant.stock:
            return Response({"error": "Stock limit exceeded"}, status=400)

        cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Quantity updated successfully"}, status=200)




# class CartDetailView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         serializer = CartSerializer(cart)
#         return Response(serializer.data)

class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

        

class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")

        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
            return Response({"message": "Item removed"}, status=200)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)





def get_user_wishlist(user):
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    return wishlist

class WishlistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist = get_user_wishlist(request.user)
        serializer = WishlistSerializer(wishlist, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddToWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        variant_id = request.data.get("variant_id")
        if not variant_id:
            return Response({"error": "variant_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response({"error": "Variant not found"}, status=status.HTTP_404_NOT_FOUND)

        wishlist = get_user_wishlist(request.user)

        item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, variant=variant)
        if not created:
            return Response({"message": "Already in wishlist"}, status=status.HTTP_200_OK)

        return Response({"message": "Added to wishlist"}, status=status.HTTP_201_CREATED)


class RemoveFromWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        variant_id = request.data.get("variant_id")
        if not variant_id:
            return Response({"error": "variant_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = WishlistItem.objects.get(wishlist__user=request.user, variant__id=variant_id)
            item.delete()
            return Response({"message": "Removed from wishlist"}, status=status.HTTP_200_OK)
        except WishlistItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)


class ToggleWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        variant_id = request.data.get("variant_id")
        if not variant_id:
            return Response({"error": "variant_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response({"error": "Variant not found"}, status=status.HTTP_404_NOT_FOUND)

        wishlist = get_user_wishlist(request.user)

        exists = WishlistItem.objects.filter(wishlist=wishlist, variant=variant).first()
        if exists:
            exists.delete()
            return Response({"toggled": False, "message": "Removed from wishlist"}, status=status.HTTP_200_OK)

        WishlistItem.objects.create(wishlist=wishlist, variant=variant)
        return Response({"toggled": True, "message": "Added to wishlist"}, status=status.HTTP_201_CREATED)


# ---------------- Address -----------------

class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(user=request.user).order_by("-is_default", "-created_at")
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if serializer.validated_data.get("is_default"):
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

        address = serializer.save(user=request.user)
        return Response(AddressSerializer(address).data, status=status.HTTP_201_CREATED)


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Address, pk=pk, user=user)

    def get(self, request, pk):
        address = self.get_object(pk, request.user)
        return Response(AddressSerializer(address).data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        address = self.get_object(pk, request.user)
        serializer = AddressSerializer(address, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if serializer.validated_data.get("is_default"):
            Address.objects.filter(user=request.user, is_default=True).exclude(pk=pk).update(is_default=False)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        address = self.get_object(pk, request.user)
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if serializer.validated_data.get("is_default"):
            Address.objects.filter(user=request.user, is_default=True).exclude(pk=pk).update(is_default=False)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        address = self.get_object(pk, request.user)
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreatePaymentOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        shipping_address_id = request.data.get("shipping_address_id")
        billing_address_id = request.data.get("billing_address_id")

        # Validate addresses
        try:
            shipping_address = Address.objects.get(id=shipping_address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"error": "Invalid shipping address"}, status=400)

        if billing_address_id:
            try:
                billing_address = Address.objects.get(id=billing_address_id, user=request.user)
            except Address.DoesNotExist:
                return Response({"error": "Invalid billing address"}, status=400)
        else:
            billing_address = shipping_address  # fallback

        # Get cart
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related("variant", "variant__product")

        if not items:
            return Response({"error": "Cart is empty"}, status=400)

        total_amount = sum(item.total_price for item in items)
        razorpay_amount = int(total_amount * 100)

        # Create Razorpay order
        try:
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            razorpay_order = client.order.create({
                "amount": razorpay_amount,
                "currency": "INR",
                "payment_capture": 1,
            })
        except Exception as exc:  # pragma: no cover - network error handling
            return Response({"error": f"Failed to create payment order: {exc}"}, status=400)

        # Save transaction temporarily (clear any previous pending ones)
        PaymentTransaction.objects.filter(user=request.user, status="created").delete()
        PaymentTransaction.objects.create(
            user=request.user,
            amount=total_amount,
            razorpay_order_id=razorpay_order["id"],
            status="created",
            shipping_address_id=shipping_address.id,
            billing_address_id=billing_address.id,
        )

        return Response({
            "order_id": razorpay_order["id"],
            "amount": total_amount,
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID,
        }, status=200)




from app.email import send_order_success_email


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response({"error": "Missing payment information"}, status=400)

        try:
            tx = PaymentTransaction.objects.get(
                razorpay_order_id=razorpay_order_id,
                user=request.user,
            )
        except PaymentTransaction.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=404)

        if tx.status != "created":
            return Response({"error": "Transaction already processed"}, status=400)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Signature verify
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            })
        except:
            tx.status = "failed"
            tx.save()
            return Response({"error": "Payment verification failed"}, status=400)

        # Fetch addresses with user guard
        try:
            shipping_address = Address.objects.get(id=tx.shipping_address_id, user=request.user)
            billing_address = Address.objects.get(id=tx.billing_address_id, user=request.user)
        except Address.DoesNotExist:
            tx.status = "failed"
            tx.save(update_fields=["status"])
            return Response({"error": "Saved address not found"}, status=400)

        # Create final Order
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            total_amount=tx.amount,
            status="confirmed",
            payment_method="razorpay",
            payment_status="paid",
            transaction_id=razorpay_payment_id,
        )

        # Convert cart items into OrderItems
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related("variant", "variant__product")

        for item in items:
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                quantity=item.quantity,
                unit_price=item.variant.price,
                total_price=item.total_price,
            )
            item.variant.stock = max(0, item.variant.stock - item.quantity)
            item.variant.save(update_fields=["stock"])

        # Clear cart
        items.delete()

        # Update payment transaction
        tx.order = order
        tx.razorpay_payment_id = razorpay_payment_id
        tx.razorpay_signature = razorpay_signature
        tx.status = "success"
        tx.save()

        # Send confirmation email to user and owner
        order_items = OrderItem.objects.filter(order=order)
        try:
            send_order_success_email(request.user, order, order_items)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Order confirmation email failed for {request.user.email}: {str(e)}")
            # Email failure shouldn't block order completion

        return Response({
            "message": "Payment verified successfully",
            "order_id": order.id
        }, status=200)


# ---------------- Orders -----------------

class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderListSerializer(orders, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        serializer = OrderSerializer(order, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)



