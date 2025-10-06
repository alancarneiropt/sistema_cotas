"""
URLs da API para a app raffles.
"""
from django.urls import path
from . import views
from . import views_admin

app_name = "raffles_api"

urlpatterns = [
    path("products/active/", views.api_products_active, name="products_active"),
    path("products/<int:product_id>/quotas/", views.api_product_quotas, name="product_quotas"),
    path("stats/", views_admin.admin_stats_api, name="admin_stats"),
]
