
from rest_framework import generics, permissions
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer, UserDetailsSerializer, ItemSerializer, CartItemSerializer, ChangePasswordSerializer,  EmailSerializer
from rest_framework.response import Response
from django.shortcuts import render
from django.http import HttpResponse
from .models import Item, UserData, CartItem, Cart
from rest_framework import status
import random
from django.utils import timezone
from datetime import timedelta
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail

# view for registering users


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserDetailsView(generics.RetrieveAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


def landingPageView(request):
    # Get the current date and time
    current_date = timezone.now()

    # Calculate the date one week ago from the current date
    one_week_ago = current_date - timedelta(days=7)

    # Query the database to get the count of items added in the last week
    items_added_last_week = Item.objects.filter(
        date_added__gte=one_week_ago).count()

    # Query the database to get the count of items with status 'sell'
    total_sell_items = Item.objects.filter(status='sale').count()

    # Query the database to get the count of active users (users with at least one item with status 'sell')
    active_users = UserData.objects.all().count()

    # Pass the counts as context data to the template
    context = {
        'items_added_last_week': items_added_last_week,
        'total_sell_items': total_sell_items,
        'active_users': active_users,
    }
    rendered_template = render(request, 'index.html', context)

    # Return the rendered template as a response with content type 'text/html'
    return HttpResponse(rendered_template, content_type='text/html')


class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)


class DeleteAllItemsView(APIView):
    def delete(self, request, *args, **kwargs):
        try:
            # Perform bulk deletion of all items in the Item model
            deleted_count, _ = Item.objects.all().delete()
            return Response({"message": f"{deleted_count} items deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Error occurred while deleting items.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class PopulateDBView(APIView):
    def post(self, request):
        # Empty the database before repopulating
        Item.objects.all().delete()
        UserData.objects.filter(username__startswith='testuser').delete()

        # Generate and save 6 users
        for i in range(1, 7):
            username = f'testuser{i}'
            email = f'testuser{i}@shop.aa'
            password = f'pass{i}'
            user = UserData.objects.create_user(
                username=username, email=email, password=password)

            # For the first 3 users (sellers), generate and save 10 items each
            if i <= 3:
                for j in range(1, 11):
                    title = f'Item {j}'
                    description = f'This is item {j} owned by {username}.'
                    price = random.randint(10, 100)
                    isAvailable = True
                    status = 'sale'
                    Item.objects.create(
                        title=title, description=description, status=status, price=price, isAvailable=isAvailable, seller_id=user.id, user_id=user)

        return Response({'message': 'Database populated         .'}, 200)


class ItemListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    # This allows access without authentication.
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        status = self.request.query_params.get('status', 'sale')
        isAvailable = True
        return Item.objects.filter(status=status, isAvailable=isAvailable).order_by('-id')

     # Set up pagination to send only 10 items per request.
    pagination_class = LimitOffsetPagination
    default_limit = 10
    max_limit = 10


class SellItemsList(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        isAvailable = True
        # Filter items based on the current logged-in user and status "sell"
        return Item.objects.filter(user_id=self.request.user.id, status='sale', isAvailable=isAvailable)


class AddToCartView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        item_id = request.data.get('item_id')
        user_id = request.data.get('user_id')
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, item=item, user_id=user_id)
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemsListView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CartItem.objects.filter(user_id=user.id)


class RemoveFromCartView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        item_id = kwargs.get('item_id')

        try:
            cart_item = CartItem.objects.get(item_id=item_id, user_id=user.id)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Cart item removed successfully'}, status=status.HTTP_204_NO_CONTENT)


class RemoveAllCartItemsView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user

        try:
            cart_items = CartItem.objects.filter(user_id=user.id)
            cart_items.delete()
        except CartItem.DoesNotExist:
            return Response({'message': 'No cart items found'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'All cart items removed successfully'}, status=status.HTTP_204_NO_CONTENT)


class ItemsByBuyerView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        status = 'purchased'
        return Item.objects.filter(buyer_id=user.id, status=status)


class ItemsSellerView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        status = 'purchased'
        return Item.objects.filter(seller_id=user.id, status=status)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not user.check_password(old_password):
                return Response({'error': 'Incorrect old password'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)

            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserDataById(generics.RetrieveAPIView):
    queryset = UserData.objects.all()
    serializer_class = UserDetailsSerializer
    
class SendEmailView(APIView):
    serializer_class = EmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        subject = 'webshop-invoice'
        message = serializer.validated_data['message']
        from_email = 'admin@webshop.com'
        recipient_list =[serializer.validated_data['email_to']]

        send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'Email sent successfully'})