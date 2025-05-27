from django.contrib import admin
from . import models

admin.site.site_title = 'Интернет-магазин одежды'
admin.site.site_header = 'Интернет-магазин одежды'
admin.site.index_title = 'Администрирование'

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 1
    fields = ('image',)

@admin.register(models.Product)
class ProductAdminView(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'price', 'category', 'article',)
    list_filter = ('price', 'category')
    search_fields = ('name', 'article')
    inlines = [ProductImageInline]
    ordering = ('-id',)

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'address', 'birthday', 'phone_number')
    search_fields = ('name', 'surname', 'user__username')

class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 1
    fields = ('product', 'size', 'get_price')
    readonly_fields = ('get_price',)

    @admin.display(description="Цена за единицу")
    def get_price(self, obj):
        price = obj.product.price
        return price

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('receiver_details', 'created_at', 'total_price', 'order_number')
    inlines = [OrderItemInline]
    search_fields = ('order_number', 'receiver_details__name', 'receiver_details__surname')
    ordering = ('-created_at',)
    list_filter = ('created_at',)