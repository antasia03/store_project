from django.urls import path
from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='base'),
    path('product/<int:pk>/', views.DetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('product/favorites/', views.FavoriteView.as_view(), name='product_favorite_list'),
    path('product/<int:pk>/cart_item/', views.add_to_cart, name='add_to_cart'),
    path('product/cart/', views.CartView.as_view(), name='cartitem_list'),
    path('product/<int:pk>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile_edit"),
    path('order/create/', views.OrderCreateView.as_view(), name='order_create'),
    path('order/success/<uuid:order_number>/', views.order_success, name='order_success'),
]