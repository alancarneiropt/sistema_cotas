"""
URLs para a app raffles.
"""
from django.urls import path
from . import views
from . import views_admin
from . import views_admin_products
from . import views_auth

app_name = "raffles"

urlpatterns = [
    # URLs de autenticação
    path("login/", views_auth.custom_login, name="custom_login"),
    path("logout/", views_auth.custom_logout, name="custom_logout"),
    path("profile/", views_auth.profile, name="profile"),
    
    # URLs administrativas (devem vir antes das públicas para evitar conflitos)
    path("dashboard/", views_admin.admin_dashboard, name="admin_dashboard"),
    path("dashboard/<int:product_id>/", views_admin.admin_dashboard, name="admin_dashboard_product"),
    path("produtos/", views_admin.admin_products, name="admin_products"),
    path("produto/criar/", views_admin_products.admin_product_create, name="admin_product_create"),
    path("produto/<int:product_id>/", views_admin.admin_product_detail, name="admin_product_detail"),
    path("produto/<int:product_id>/editar/", views_admin_products.admin_product_edit, name="admin_product_edit"),
    path("produto/<int:product_id>/deletar/", views_admin_products.admin_product_delete, name="admin_product_delete"),
    path("produto/<int:product_id>/criar-cotas/", views_admin_products.admin_product_create_quotas, name="admin_product_create_quotas"),
    path("produto/<int:product_id>/toggle-status/", views_admin_products.admin_product_toggle_status, name="admin_product_toggle_status"),
    path("admin-pedidos/", views_admin.admin_orders, name="admin_orders"),
    path("admin-pedido/<int:order_id>/", views_admin.admin_order_detail, name="admin_order_detail"),
    path("admin-pedidos/historico/", views.admin_order_history, name="admin_order_history"),
    path("admin-pedido/<int:order_id>/detalhes/", views.admin_order_detail_full, name="admin_order_detail_full"),
    path("logs/", views_admin.admin_logs, name="admin_logs"),
    
    # URLs públicas
    path("", views.home, name="home"),
    path("sucesso/", views.order_success, name="order_success"),
    path("comprovante/<int:order_id>/", views.upload_receipt, name="upload_receipt"),
    path("pedido/<int:order_id>/", views.order_status, name="order_status"),
    path("pedido/<int:order_id>/detalhes/", views.order_detail_full, name="order_detail_full"),
    path("produto/<int:product_id>/", views.product_detail, name="product_detail"),
    path("vencedores/", views.winners_list, name="winners_list"),
    path("historico/", views.order_history, name="order_history"),
    
    # Ações administrativas
    path("acoes/confirmar-pedido/<int:order_id>/", views_admin.confirm_order_action, name="confirm_order"),
    path("acoes/cancelar-pedido/<int:order_id>/", views_admin.cancel_order_action, name="cancel_order"),
    path("acoes/confirmar-com-comprovante/<int:order_id>/", views_admin.confirm_order_with_receipt, name="confirm_order_with_receipt"),
    path("acoes/confirmar-sem-comprovante/<int:order_id>/", views_admin.confirm_order_without_receipt, name="confirm_order_without_receipt"),
    path("acoes/sortear-produto/<int:product_id>/", views_admin.draw_product_action, name="draw_product"),
    path("acoes/criar-cotas/<int:product_id>/", views_admin.create_quotas_action, name="create_quotas"),
    path("acoes/liberar-reservas/", views_admin.release_reservations_action, name="release_reservations"),
]
