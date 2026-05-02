from django.contrib import admin
from .models import InvestmentListing


@admin.register(InvestmentListing)
class InvestmentListingAdmin(admin.ModelAdmin):
    list_display = ('restaurant_name', 'business_type', 'location', 'funding_goal', 'owner', 'created_at')
    list_filter = ('business_type', 'created_at')
    search_fields = ('restaurant_name', 'location', 'summary', 'owner__username')
    prepopulated_fields = {'slug': ('restaurant_name',)}
