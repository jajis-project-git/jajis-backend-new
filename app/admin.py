from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin

from .models import (
    BannerImage, Saloon, FoodMenu, Cosmetics, Courses,
    Category, Product, ProductVariant,
    Cart, CartItem, Wishlist, WishlistItem,
    Address, Order, OrderItem, PaymentTransaction, Eventhall, FranchiseEnquiry
)


# =============================================================
# Helpers
# =============================================================


def _thumb(img_field, size=56):
    if not img_field:
        return "-"
    return format_html(
        '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:8px;border:1px solid #e5e7eb;" />',
        img_field.url, size, size
    )


def _format_address(addr):
    if not addr:
        return "-"
    parts = [
        addr.label or None,
        addr.line1,
        addr.line2 or None,
        f"{addr.city}{', ' + addr.state if addr.state else ''} - {addr.postal_code}",
        addr.country,
        f"Phone: {addr.phone}" if addr.phone else None,
    ]
    text = "\n".join([p for p in parts if p])
    return format_html('<pre style="white-space:pre-wrap;margin:0">{}</pre>', text)


# =============================================================
# Basic Admin
# =============================================================

@admin.register(BannerImage)
class BannerImageAdmin(admin.ModelAdmin):
    list_display = ("id", "preview", "uploaded_at")
    readonly_fields = ("preview", "uploaded_at")
    search_fields = ("id",)
    ordering = ("-uploaded_at",)

    def preview(self, obj):
        return _thumb(obj.image, size=64)
    preview.short_description = "Image"


@admin.register(Saloon)
class SaloonAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "location", "preview")
    search_fields = ("name", "location")
    readonly_fields = ("preview",)

    def preview(self, obj):
        return _thumb(obj.image, size=64)
    preview.short_description = "Image"


@admin.register(FoodMenu)
class FoodMenuAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "preview")
    search_fields = ("title", "description")
    readonly_fields = ("preview",)

    def preview(self, obj):
        return _thumb(obj.image, size=56)
    preview.short_description = "Image"


@admin.register(Cosmetics)
class CosmeticsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "preview")
    search_fields = ("title", "description")
    readonly_fields = ("preview",)

    def preview(self, obj):
        return _thumb(obj.image, size=56)
    preview.short_description = "Image"


@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "duration", "preview")
    search_fields = ("course", "description", "duration")
    readonly_fields = ("preview",)

    def preview(self, obj):
        return _thumb(obj.image, size=56)
    preview.short_description = "Image"


# =============================================================
# E-commerce Admin Site
# =============================================================

class EcommerceAdminSite(admin.AdminSite):
    site_header = "Jaji's — E‑Commerce Admin"
    site_title = "Jaji's E‑Commerce Admin"
    index_title = "E‑Commerce Dashboard"


ecommerce_admin_site = EcommerceAdminSite(name="ecommerce_admin")
ecommerce_admin_site.register(User, UserAdmin)
ecommerce_admin_site.register(Group, GroupAdmin)


# ---------------- Product and Variant ----------------

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ("quantity_label", "mrp", "price", "stock", "sku")
    show_change_link = True
    can_delete = True  # explicitly allow deletion


@admin.register(Category, site=ecommerce_admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Product, site=ecommerce_admin_site)
class ProductAdmin(admin.ModelAdmin):
    inlines = (ProductVariantInline,)

    list_display = (
        "id", "preview", "title", "category", "brand",
        "variants_count", "total_stock", "created_at", "updated_at"
    )
    list_filter = ("category", "brand", "created_at")
    search_fields = ("title", "description", "brand")
    autocomplete_fields = ("category",)
    readonly_fields = ("preview", "created_at", "updated_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25
    list_max_show_all = 100
    show_full_result_count = False

    fieldsets = (
        ("Product", {"fields": ("title", "category", "brand", "description")}),
        ("Images", {"fields": ("preview", "image1", "image2", "image3", "image4")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def preview(self, obj):
        return _thumb(obj.image1, size=64)
    preview.short_description = "Image"

    def variants_count(self, obj):
        return obj.variants.count()
    variants_count.short_description = "Variants"

    def total_stock(self, obj):
        return sum(v.stock for v in obj.variants.all())
    total_stock.short_description = "Total stock"

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(ProductVariant, site=ecommerce_admin_site)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "id", "product_image", "product_title", "product",
        "quantity_label", "mrp", "price", "stock", "sku"
    )
    list_filter = ("product__category", "product__brand")
    search_fields = ("sku", "product__title", "quantity_label")
    ordering = ("product__title", "quantity_label")

    def product_image(self, obj):
        return _thumb(getattr(obj.product, "image1", None), size=44)
    product_image.short_description = "Image"

    def product_title(self, obj):
        return getattr(obj.product, "title", "-")
    product_title.short_description = "Product"


# ---------------- Address ----------------

@admin.register(Address, site=ecommerce_admin_site)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "label", "city", "state", "postal_code", "country", "phone", "is_default", "created_at")
    list_filter = ("is_default", "country", "state", "city")
    search_fields = ("user__username", "user__email", "label", "line1", "city", "postal_code", "phone")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    actions = ("make_default",)

    @admin.action(description="Set selected address as default (per user)")
    def make_default(self, request, queryset):
        for addr in queryset.select_related("user"):
            Address.objects.filter(user=addr.user, is_default=True).exclude(pk=addr.pk).update(is_default=False)
            addr.is_default = True
            addr.save(update_fields=["is_default"])


# ---------------- Order ----------------

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("variant",)
    fields = ("product_image", "product_title", "variant", "quantity", "unit_price", "total_price")
    readonly_fields = ("product_image", "product_title", "variant", "quantity", "unit_price", "total_price")
    can_delete = True

    def product_image(self, obj):
        return _thumb(getattr(obj.variant.product, "image1", None), size=44)
    product_image.short_description = "Image"

    def product_title(self, obj):
        return getattr(obj.variant.product, "title", "-")
    product_title.short_description = "Product"


class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    fields = ("status", "amount", "razorpay_order_id", "razorpay_payment_id", "created_at")
    readonly_fields = ("status", "amount", "razorpay_order_id", "razorpay_payment_id", "created_at")
    can_delete = True


@admin.register(Order, site=ecommerce_admin_site)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemInline, PaymentTransactionInline)

    list_display = (
        "id", "user", "status", "payment_status",
        "total_amount", "created_at",
        "razorpay_payment_id", "razorpay_order_id",
        "shipping_address_short"
    )
    list_filter = ("status", "payment_status", "payment_method", "created_at")
    search_fields = (
        "id", "user__username", "user__email", "transaction_id",
        "paymenttransaction__razorpay_order_id", "paymenttransaction__razorpay_payment_id",
        "items__variant__product__title", "items__variant__sku"
    )
    autocomplete_fields = ("user", "shipping_address")
    readonly_fields = ("created_at", "updated_at", "shipping_address_full")
    ordering = ("-created_at",)
    list_per_page = 25
    list_max_show_all = 100
    show_full_result_count = False

    fieldsets = (
        ("Order", {"fields": ("user", "status", "total_amount", "shipping_cost", "created_at", "updated_at")}),
        ("Payment", {"fields": ("payment_method", "payment_status", "transaction_id")}),
        ("Shipping", {"fields": ("shipping_address_full",)}),
    )

    def shipping_address_full(self, obj):
        return _format_address(obj.shipping_address)
    shipping_address_full.short_description = "Shipping address (full)"

    def shipping_address_short(self, obj):
        a = obj.shipping_address
        return f"{a.city} - {a.postal_code}" if a else "-"
    shipping_address_short.short_description = "Shipping"

    def razorpay_payment_id(self, obj):
        tx = PaymentTransaction.objects.filter(order=obj).order_by("-created_at").first()
        if tx and tx.razorpay_payment_id:
            return tx.razorpay_payment_id
        return obj.transaction_id or "-"
    razorpay_payment_id.short_description = "RZP Payment ID"

    def razorpay_order_id(self, obj):
        tx = PaymentTransaction.objects.filter(order=obj).order_by("-created_at").first()
        return tx.razorpay_order_id if tx else "-"
    razorpay_order_id.short_description = "RZP Order ID"





# ---------------- Payment Transactions (for auditing missed orders) ----------------

class OrphanedTransactionFilter(admin.SimpleListFilter):
    title = "Order linked"
    parameter_name = "has_order"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Has Order"),
            ("no", "⚠ Missing Order (Orphaned)"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(order__isnull=False)
        if self.value() == "no":
            return queryset.filter(order__isnull=True)


@admin.register(PaymentTransaction, site=ecommerce_admin_site)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "status", "amount",
        "razorpay_order_id", "razorpay_payment_id",
        "order_link", "created_at",
    )
    list_filter = ("status", OrphanedTransactionFilter, "created_at")
    search_fields = (
        "razorpay_order_id", "razorpay_payment_id",
        "user__username", "user__email",
    )
    autocomplete_fields = ("user", "order")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 25
    actions = ["recreate_missing_orders"]

    def order_link(self, obj):
        if obj.order:
            return format_html(
                '<a href="../order/{}/change/">Order #{}</a>',
                obj.order.id,
                obj.order.id,
            )
        return format_html(
            '<span style="color:red;font-weight:bold">\u26a0 NO ORDER</span>'
        )
    order_link.short_description = "Order"

    def recreate_missing_orders(self, request, queryset):
        recovered = 0
        already_linked = 0
        for tx in queryset:
            if tx.order_id:
                already_linked += 1
                continue
            if tx.status not in ("success", "created"):
                continue

            # Fallback shipping & billing address
            shipping_address = None
            if tx.shipping_address_id:
                shipping_address = Address.objects.filter(id=tx.shipping_address_id, user=tx.user).first()
            if not shipping_address:
                shipping_address = Address.objects.filter(user=tx.user).order_by("-is_default", "-id").first()

            billing_address = None
            if tx.billing_address_id:
                billing_address = Address.objects.filter(id=tx.billing_address_id, user=tx.user).first()
            if not billing_address:
                billing_address = shipping_address

            # Check if order with this transaction_id already exists
            order = None
            if tx.razorpay_payment_id:
                order = Order.objects.filter(transaction_id=tx.razorpay_payment_id).first()

            if not order:
                order = Order.objects.create(
                    user=tx.user,
                    shipping_address=shipping_address,
                    billing_address=billing_address,
                    total_amount=tx.amount,
                    status="confirmed",
                    payment_method="razorpay",
                    payment_status="paid" if tx.status == "success" else "unpaid",
                    transaction_id=tx.razorpay_payment_id or tx.razorpay_order_id,
                )
                cart = Cart.objects.filter(user=tx.user).first()
                if cart and cart.items.exists():
                    for item in cart.items.select_related("variant"):
                        OrderItem.objects.create(
                            order=order,
                            variant=item.variant,
                            quantity=item.quantity,
                            unit_price=item.variant.price,
                            total_price=item.total_price,
                        )

            tx.order = order
            if tx.status != "success" and tx.razorpay_payment_id:
                tx.status = "success"
            tx.save(update_fields=["order", "status"])
            recovered += 1

        self.message_user(
            request,
            f"Successfully recovered {recovered} order(s). ({already_linked} were already linked)"
        )
    recreate_missing_orders.short_description = "⚡ Recreate Missing Order(s) for selected transactions"


# Also register on default admin site so all orders and ecommerce models are accessible on both /admin/ and /ecommerce/admin/
for _model, _admin_cls in [
    (Category, CategoryAdmin),
    (Product, ProductAdmin),
    (ProductVariant, ProductVariantAdmin),
    (Address, AddressAdmin),
    (Order, OrderAdmin),
    (PaymentTransaction, PaymentTransactionAdmin),
]:
    if not admin.site.is_registered(_model):
        admin.site.register(_model, _admin_cls)


@admin.register(Eventhall)
class EventhallAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "email", "event_type", "category", "event_date", "created_at")
    list_filter = ("event_type", "category", "event_date")
    search_fields = ("name", "phone", "email")
    date_hierarchy = "event_date"
    ordering = ("-created_at",)


@admin.register(FranchiseEnquiry)
class FranchiseEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "id", "full_name", "mobile_number", "email",
        "preferred_city", "investment_budget", "plan_to_start", "created_at"
    )
    list_filter = ("preferred_city", "investment_budget", "plan_to_start", "applicant_type", "state")
    search_fields = ("full_name", "mobile_number", "email", "preferred_city", "preferred_area")
    ordering = ("-created_at",)



