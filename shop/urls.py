"""
URL configuration for shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin
from .views import RegisterView, UserDetailsView, ChangePasswordView, ItemsByBuyerView, GetUserDataById, SendEmailView,ItemsSellerView,RemoveAllCartItemsView,RemoveFromCartView,CartItemsListView, AddToCartView,ItemListCreateView,DeleteAllItemsView, ItemRetrieveUpdateDestroyView, PopulateDBView, ItemListView, SellItemsList
from . import views
from rest_framework_simplejwt.views import (    
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/index', views.landingPageView, name='index'),
    path('api/signup/', RegisterView.as_view(), name="sign_up"),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/details/', UserDetailsView.as_view(), name='user-details'),
    path('api/items/', ItemListCreateView.as_view(), name='item-list-create'),
    path('api/items/delete-all/', DeleteAllItemsView.as_view(),name='delete-all-items'),
    path('api/items/<int:pk>/', ItemRetrieveUpdateDestroyView.as_view(), name='item-retrieve-update-destroy'),
    path('api/populate_db/', PopulateDBView.as_view(), name='populate-db'),
    path('api/items/public/', ItemListView.as_view(), name='item-list'),
    path('api/items/myitems/', SellItemsList.as_view(), name='my-item'),
    path('api/add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('api/cart-items/', CartItemsListView.as_view(), name='cart-items-list'),
    path('api/remove-from-cart/<int:item_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('api/remove-all-cart-items/', RemoveAllCartItemsView.as_view(), name='remove-all-cart-items'),
    path('api/my-bought-items/', ItemsByBuyerView.as_view(), name='items-by-buyer'),
    path('api/my-sold-items/', ItemsSellerView.as_view(), name='items-by-seller'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/user/<int:pk>/', GetUserDataById.as_view(), name='user-data'),
    path('api/send-email/', SendEmailView.as_view(), name='send-email'),
]
