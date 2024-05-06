from rest_framework import serializers
from .models import UserData, Item, CartItem


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserData
        fields = ["id", "email", "username", "password"]

    def create(self, validated_data):
        user = UserData.objects.create(email=validated_data['email'],
                                       username=validated_data['username']
                                       )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ('id', 'email', 'username')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    cart_id = serializers.IntegerField(source='cart.id')
    item_id = serializers.IntegerField(source='item.id')
    title = serializers.CharField(source='item.title')
    description = serializers.CharField(source='item.description')
    isPriceChange = serializers.CharField(source='item.isPriceChange')
    isAvailable = serializers.CharField(source='item.isAvailable')
    buyer_id =serializers.CharField(source='item.buyer_id')
    seller_id = serializers.CharField(source='item.seller_id')

    price = serializers.DecimalField(
        source='item.price', max_digits=10, decimal_places=2)

    class Meta:
        model = CartItem
        fields = ['cart_id', 'item_id', 'title',
                  'description', 'price', 'isPriceChange', 'isAvailable', 'user_id', 'buyer_id', 'seller_id']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class EmailSerializer(serializers.Serializer):
    message = serializers.CharField()
    email_to = serializers.CharField()
