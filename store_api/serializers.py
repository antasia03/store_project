from rest_framework import serializers
from store.models import Product, ProductImage, Category, Favorite, CartItem, Order, OrderItem, Size, Profile

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'product', 'image')

class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Favorite
        fields = ('id', 'product', 'user')

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'description', 'category', 'article', 'images')

class ProductCreationSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    images = serializers.ListField(
        child= serializers.FileField(max_length=100000, allow_empty_file=False),
        required=True,
    )
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'category','images']


    def create(self, validated_data):
        category = validated_data.pop('category', [])
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data, category=category)
        for image in images_data:
            ProductImage.objects.create(product=product, image=image)

        return product

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ('id', 'name')


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)
    size = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all(), required=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'size']

    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data['product']
        size = validated_data['size']

        existing_item = CartItem.objects.filter(user=user, product=product, size=size).first()

        if existing_item:
            raise serializers.ValidationError("Этот товар с выбранным размером уже в корзине.")

        return CartItem.objects.create(**validated_data)

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)
    size = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all(), required=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'size']

class OrderSerializer(serializers.ModelSerializer):
    receiver_details = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), required=True)
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'receiver_details', 'created_at', 'total_price', 'order_number', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)


        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'name', 'surname', 'birthday', 'address', 'phone_number']
        read_only_fields = ['user']