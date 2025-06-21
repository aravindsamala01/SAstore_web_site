from django.contrib import admin
from.models import Product,Category
from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.

admin.site.register(Product)
admin.site.register(Category)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

# This is from order enter list.
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'status', 'created_at']
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email')

    def get_customer_name(self, obj):
        return obj.user.first_name  # or however you want to display it
    get_customer_name.short_description = 'Customer Name'

    def get_customer_email(self, obj):
        return obj.user.email
    get_customer_email.short_description = 'Customer Email'

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'available', 'created_at')
    list_filter = ('available', 'created_at')
    search_fields = ('name',)


