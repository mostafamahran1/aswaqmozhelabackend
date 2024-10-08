from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    orderitems = serializers.SerializerMethodField(method_name="get_order_items", read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "city", "zip_code", "street", "state", "country", "phone_no", "total_amount", "payment_status", "payment_mode", "status", "user", "createAT", "orderitems"]

    def get_order_items(self, obj):
        order_items = obj.orderitems.all()
        serializer = OrderItemsSerializer(order_items, many=True)
        return serializer.data
