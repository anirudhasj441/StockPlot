from django.contrib import admin
from .models import Stock, StockTrack, StockNews
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

admin.site.register(Stock, StockAdmin)
admin.site.register(StockTrack)
admin.site.register(StockNews)