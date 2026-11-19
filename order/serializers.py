from rest_framework import serializers
from .delivery_window import window_for_order
from .models import Order, OrderItem
from django.contrib.auth.models import User

class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    createAT = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    orderitems = serializers.SerializerMethodField(method_name="get_order_items", read_only=True)
    user_full_name = serializers.SerializerMethodField(method_name="get_user_full_name", read_only=True)  # لتسلسل اسم المستخدم
    app_feedback = serializers.SerializerMethodField()
    expected_delivery_start = serializers.SerializerMethodField()
    expected_delivery_end = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "city", "zip_code", "street", "state", 
            "country", "phone_no", "total_amount", "payment_status", 
            "payment_mode", "status", "user", "createAT", "orderitems", "user_full_name",
            "delivery_fee", "standard_delivery_fee", "free_delivery",
            "discount_amount", "app_feedback",
            "expected_delivery_start", "expected_delivery_end",
        ]

    def get_expected_delivery_start(self, obj):
        start, _ = window_for_order(obj)
        return start.isoformat()

    def get_expected_delivery_end(self, obj):
        _, end = window_for_order(obj)
        return end.isoformat()

    def get_app_feedback(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return None
        if not (user.is_staff or user.is_superuser or obj.user_id == user.id):
            return None
        feedbacks = list(obj.appfeedback_set.all())
        if not feedbacks:
            return None
        feedback = max(feedbacks, key=lambda item: item.created_at)
        return {
            'rating': feedback.rating,
            'suggestion': feedback.suggestion,
        }

    def get_order_items(self, obj):
        order_items = obj.orderitems.all()
        serializer = OrderItemsSerializer(order_items, many=True)
        return serializer.data

    def get_user_full_name(self, obj):
        if obj.user:
            full_name = f"{obj.user.first_name} {obj.user.last_name}"
            return full_name
        return "Unknown User"

