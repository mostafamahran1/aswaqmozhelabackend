from django.contrib import admin
# 🆕 إضافة CouponUsage للـ imports
from .models import Order, OrderItem, Coupon, DeliveryGovernorate, CouponUsage, SavedAddress

# 1️⃣ عرض حقول المنتجات كـ "سطور مدمجة" جوة الفاتورة الأساسية
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # لمنع ظهور سطور فارغة إضافية
    
    # جعل تفاصيل الفاتورة السابقة للقراءة فقط لحمايتها من التلاعب البشري بالخطأ
    readonly_fields = ['name', 'price', 'quantity', 'variant', 'color_name', 'color_code', 'size', 'primary_image']
    fields = ['name', 'price', 'quantity', 'variant', 'color_name', 'color_code', 'size', 'primary_image']
    can_delete = False  # منع حذف عنصر منفرد من الفاتورة من هنا مباشرة لحماية الحسابات


# 2️⃣ تخصيص شاشة إدارة الطلبات بالكامل
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # الحقول اللي هتظهر في الجدول الرئيسي بره
    list_display = ['id', 'get_customer_name', 'phone_no', 'state', 'total_amount', 'free_delivery', 'status', 'payment_status', 'createAT']
    
    # فلاتر جانبية سريعة للمتابعة اليومية
    list_filter = ['status', 'payment_status', 'payment_mode', 'free_delivery', 'state', 'createAT']
    
    # البحث الذكي (برقم الأوردر، اسم العميل، اليوزر نيم، أو رقم الموبايل)
    search_fields = ['id', 'user__username', 'user__first_name', 'user__last_name', 'phone_no', 'city']
    
    # حمايتها كـ Readonly عشان الموظف يغير "حالة الطلب" بس، وميلعبش في الحسابات والتواريخ
    readonly_fields = [
        'total_amount', 'discount_amount', 'createAT', 'coupon',
        'delivery_fee', 'standard_delivery_fee', 'free_delivery',
        'expected_delivery_start', 'expected_delivery_end',
    ]
    
    # دمج الفاتورة (الـ Inline) هنا
    inlines = [OrderItemInline]

    # تقسيم شاشة الأوردر من الداخل لـ مجموعات (Fieldsets) تفتح النفس في الشغل
    fieldsets = (
        ('👤 بيانات العميل والشحن', {
            'fields': ('user', 'phone_no', 'country', 'state', 'city', 'street', 'zip_code')
        }),
        ('💰 الحسابات والخصومات الفورية', {
            'fields': (
                'total_amount', 'standard_delivery_fee', 'delivery_fee',
                'free_delivery', 'expected_delivery_start', 'expected_delivery_end',
                'coupon', 'discount_amount',
                'payment_mode', 'payment_status',
            )
        }),
        ('📦 اللوجستيات وحالة الأوردر', {
            'fields': ('status', 'createAT')
        }),
    )

    # دالة ذكية لإظهار اسم العميل بالكامل في جدول الطلبات الرئيسي
    def get_customer_name(self, obj):
        if obj.user:
            full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
            return full_name if full_name else obj.user.username
        return "مستخدم مجهول"
    get_customer_name.short_description = 'اسم العميل'


# 3️⃣ تخصيص شاشة الكوبونات
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'discount_amount', 'min_order_amount', 'is_active', 'expiry_date']
    list_filter = ['is_active', 'expiry_date']
    search_fields = ['code']


# 4️⃣ تخصيص شاشة محافظات التوصيل
@admin.register(DeliveryGovernorate)
class DeliveryGovernorateAdmin(admin.ModelAdmin):
    list_display = ['name', 'delivery_fee']
    search_fields = ['name']


# 5️⃣ 🆕 تخصيص شاشة متابعة استخدام الكوبونات
@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['user', 'coupon', 'used_at']
    list_filter = ['used_at', 'coupon']
    search_fields = ['user__username', 'coupon__code']
    readonly_fields = ['user', 'coupon', 'used_at']


@admin.register(SavedAddress)
class SavedAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'label', 'phone_no', 'governorate', 'city', 'is_default']
    list_filter = ['is_default', 'governorate']
    search_fields = ['user__username', 'phone_no', 'street', 'city', 'label']