from django.urls import path

from .views import (
    HomeView,
    ListingCreateView,
    ListingDeleteView,
    ListingDetailView,
    ListingUpdateView,
    SignUpView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('opportunities/new/', ListingCreateView.as_view(), name='listing_create'),
    path('opportunities/<slug:slug>/', ListingDetailView.as_view(), name='listing_detail'),
    path('opportunities/<slug:slug>/edit/', ListingUpdateView.as_view(), name='listing_update'),
    path('opportunities/<slug:slug>/delete/', ListingDeleteView.as_view(), name='listing_delete'),
]
