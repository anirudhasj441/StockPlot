from django.contrib import admin
from .models import Stock, StockTrack, StockNews, VisitedStock
# Register your models here.

class StockAdmin(admin.ModelAdmin):
    list_display = [
        "symbol",
        "full_name"
    ]
    search_fields = [
        "symbol",
        "full_name"
    ]

class StockNewsAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "stock_symbol",
        "title"
    ]
    list_filter = [
        "stock"
    ]
    def stock_symbol(self, obj):
        return obj.stock.symbol

admin.site.register(Stock, StockAdmin)
admin.site.register(StockTrack)
admin.site.register(StockNews, StockNewsAdmin)
admin.site.register(VisitedStock)