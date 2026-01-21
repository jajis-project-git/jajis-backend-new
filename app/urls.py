from django.urls import path
from . import views

urlpatterns = [
    path('', views.home.as_view()),
    path('salons/', views.salons_view.as_view()),
    path('salons/<int:id>/', views.salons_detail_view.as_view()),
    path('cosmetics/', views.cosmetics_view.as_view()),
    path('event-hall/', views.event_hall_view.as_view()),
    path('food-court/', views.food_court_view.as_view()),
    path('designing-stitching/', views.designing_view.as_view()),
    path('academy/', views.academy_view.as_view()),
    path('franchise/', views.franchise_view.as_view()),
    path('about-us/', views.about_us_view.as_view()),
    path('contact/', views.contact_view.as_view()),


    # ecom-----------------

    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset_password"),
    path("profile/", views.UserProfileView.as_view(), name="user-profile"),


    path("products/", views.ProductListAPIView.as_view(), name="product-list"),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product-detail'),


    path('cart/add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', views.CartDetailView.as_view(), name='cart_detail'),
    path('cart/update/', views.UpdateCartQuantityView.as_view(), name='update_cart_quantity'),
    path('cart/remove/', views.RemoveCartItemView.as_view(), name='remove_cart_item'),


    # ---------------- Wishlist -----------------


    path('wishlist/', views.WishlistDetailView.as_view(), name='wishlist_detail'),
    path('wishlist/add/', views.AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('wishlist/remove/', views.RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    path('wishlist/toggle/', views.ToggleWishlistView.as_view(), name='toggle_wishlist'),
 

    # Address
    path('addresses/', views.AddressListCreateView.as_view(), name='addresses'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address_detail'),


    # Payment / Order Creation + Verification
    path("payment/create/", views.CreatePaymentOrderView.as_view(), name="create_payment"),
    path("payment/verify/", views.VerifyPaymentView.as_view(), name="verify_payment"),

    # Orders
    path("orders/", views.OrderListView.as_view(), name="orders"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),


    

]
