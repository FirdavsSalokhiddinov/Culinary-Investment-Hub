from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class InvestmentListing(models.Model):
    class BusinessType(models.TextChoices):
        RESTAURANT = 'restaurant', 'Restaurant'
        CAFE = 'cafe', 'Cafe'
        BAKERY = 'bakery', 'Bakery'
        CATERING = 'catering', 'Catering Service'
        GHOST_KITCHEN = 'ghost-kitchen', 'Ghost Kitchen'
        FOOD_TRUCK = 'food-truck', 'Food Truck'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='investment_listings',
    )
    restaurant_name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    business_type = models.CharField(max_length=20, choices=BusinessType.choices)
    location = models.CharField(max_length=120)
    funding_goal = models.DecimalField(max_digits=12, decimal_places=2)
    equity_offer = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Optional percentage of equity offered to investors.',
    )
    summary = models.CharField(max_length=220)
    story = models.TextField()
    use_of_funds = models.TextField()
    target_timeline = models.CharField(max_length=120)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.restaurant_name

    def get_absolute_url(self):
        return reverse('listing_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.restaurant_name) or 'culinary-venture'
            slug = base_slug
            counter = 2
            while InvestmentListing.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
