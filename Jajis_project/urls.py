from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app.admin import ecommerce_admin_site

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ecommerce/admin/', ecommerce_admin_site.urls),
    path('api/', include('app.urls')),
]


