from rest_framework import serializers
from .models import Order, OrderItem
from django.contrib.auth.models import User

class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    orderitems = serializers.SerializerMethodField(method_name="get_order_items", read_only=True)
    user_full_name = serializers.SerializerMethodField(method_name="get_user_full_name", read_only=True)  # لتسلسل اسم المستخدم

    class Meta:
        model = Order
        fields = [
            "id", "city", "zip_code", "street", "state", 
            "country", "phone_no", "total_amount", "payment_status", 
            "payment_mode", "status", "user", "createAT", "orderitems", "user_full_name"
        ]

    def get_order_items(self, obj):
        order_items = obj.orderitems.all()
        serializer = OrderItemsSerializer(order_items, many=True)
        return serializer.data

    def get_user_full_name(self, obj):
        if obj.user:
            full_name = f"{obj.user.first_name} {obj.user.last_name}"
            return full_name
        return "Unknown User"

