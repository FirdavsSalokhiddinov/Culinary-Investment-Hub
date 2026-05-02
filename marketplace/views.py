from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import InvestmentListingForm, SignUpForm
from .models import InvestmentListing


class HomeView(ListView):
    model = InvestmentListing
    template_name = 'marketplace/home.html'
    context_object_name = 'listings'

    def get_queryset(self):
        queryset = InvestmentListing.objects.select_related('owner')
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(restaurant_name__icontains=query)
                | Q(location__icontains=query)
                | Q(summary__icontains=query)
                | Q(use_of_funds__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listings = list(context['listings'])
        aggregate = InvestmentListing.objects.aggregate(total_requested=Sum('funding_goal'))
        total_count = InvestmentListing.objects.count()
        context['featured_listing'] = listings[0] if listings else None
        context['search_term'] = self.request.GET.get('q', '').strip()
        context['search_count'] = len(listings)
        context['stats'] = {
            'listing_count': total_count,
            'capital_requested': aggregate['total_requested'] or 0,
            'investor_access': 'Open',
        }
        return context


class ListingDetailView(DetailView):
    model = InvestmentListing
    template_name = 'marketplace/listing_detail.html'
    context_object_name = 'listing'


class OwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.get_object().owner == self.request.user


class ListingCreateView(LoginRequiredMixin, CreateView):
    model = InvestmentListing
    form_class = InvestmentListingForm
    template_name = 'marketplace/listing_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Your investment opportunity is now live.')
        return super().form_valid(form)


class ListingUpdateView(OwnerRequiredMixin, UpdateView):
    model = InvestmentListing
    form_class = InvestmentListingForm
    template_name = 'marketplace/listing_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Your opportunity has been updated.')
        return super().form_valid(form)


class ListingDeleteView(OwnerRequiredMixin, DeleteView):
    model = InvestmentListing
    template_name = 'marketplace/listing_confirm_delete.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'The opportunity has been removed.')
        return super().form_valid(form)


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Welcome to Culinary Investment Hub.')
        return response
