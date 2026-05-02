from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import InvestmentListing


class MarketplaceBaseTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='owner',
            password='testpass123',
        )
        self.other_user = get_user_model().objects.create_user(
            username='guest',
            password='testpass123',
        )
        self.listing = InvestmentListing.objects.create(
            owner=self.user,
            restaurant_name='Saffron Table',
            business_type=InvestmentListing.BusinessType.RESTAURANT,
            location='Chicago, IL',
            funding_goal='120000.00',
            equity_offer='12.50',
            summary='A neighborhood restaurant blending South Asian and Midwestern comfort food.',
            story='We are expanding from pop-ups into our first permanent space.',
            use_of_funds='Build-out, equipment, and launch staffing.',
            target_timeline='Launch within 8 months',
        )


class InvestmentListingModelTests(MarketplaceBaseTestCase):
    def test_slug_is_auto_generated(self):
        self.assertEqual(self.listing.slug, 'saffron-table')

    def test_slug_is_unique_for_duplicate_names(self):
        duplicate = InvestmentListing.objects.create(
            owner=self.user,
            restaurant_name='Saffron Table',
            business_type=InvestmentListing.BusinessType.CAFE,
            location='Houston, TX',
            funding_goal='95000.00',
            summary='Second concept with the same name.',
            story='New district expansion.',
            use_of_funds='Equipment and staffing.',
            target_timeline='Open in 6 months',
        )
        self.assertEqual(duplicate.slug, 'saffron-table-2')

    def test_get_absolute_url_uses_slug(self):
        self.assertEqual(
            self.listing.get_absolute_url(),
            reverse('listing_detail', kwargs={'slug': self.listing.slug}),
        )


class MarketplaceAccessTests(MarketplaceBaseTestCase):
    def test_homepage_is_public(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Saffron Table')

    def test_detail_page_is_public(self):
        response = self.client.get(reverse('listing_detail', kwargs={'slug': self.listing.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Saffron Table')

    def test_home_search_filters_results(self):
        InvestmentListing.objects.create(
            owner=self.user,
            restaurant_name='Bistro Ember',
            business_type=InvestmentListing.BusinessType.BAKERY,
            location='Seattle, WA',
            funding_goal='50000.00',
            summary='Craft bakery with seasonal menus.',
            story='Built traction through pop-ups.',
            use_of_funds='Lease and kitchen setup.',
            target_timeline='Launch in 4 months',
        )
        response = self.client.get(reverse('home'), {'q': 'Chicago'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Saffron Table')
        self.assertNotContains(response, 'Bistro Ember')
        self.assertEqual(response.context['search_count'], 1)

    def test_create_requires_login(self):
        response = self.client.get(reverse('listing_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
        self.assertIn('next=', response.url)

    def test_authenticated_user_can_create_listing(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(
            reverse('listing_create'),
            {
                'restaurant_name': 'Market Flame',
                'business_type': InvestmentListing.BusinessType.CAFE,
                'location': 'Austin, TX',
                'funding_goal': '85000.00',
                'equity_offer': '10.00',
                'summary': 'A cafe and bakery with all-day savory pastry service.',
                'story': 'We have proven demand from farmers market pop-ups.',
                'use_of_funds': 'Leasehold improvements and espresso equipment.',
                'target_timeline': 'Open in 5 months',
                'website': 'https://example.com',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(InvestmentListing.objects.filter(restaurant_name='Market Flame').exists())
        created = InvestmentListing.objects.get(restaurant_name='Market Flame')
        self.assertEqual(created.owner, self.user)

    def test_only_owner_can_edit(self):
        self.client.login(username='guest', password='testpass123')
        response = self.client.get(reverse('listing_update', kwargs={'slug': self.listing.slug}))
        self.assertEqual(response.status_code, 403)

    def test_only_owner_can_delete(self):
        self.client.login(username='guest', password='testpass123')
        response = self.client.post(reverse('listing_delete', kwargs={'slug': self.listing.slug}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(InvestmentListing.objects.filter(pk=self.listing.pk).exists())

    def test_owner_can_update_listing(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(
            reverse('listing_update', kwargs={'slug': self.listing.slug}),
            {
                'restaurant_name': 'Saffron Table Updated',
                'business_type': self.listing.business_type,
                'location': self.listing.location,
                'funding_goal': '140000.00',
                'equity_offer': '15.00',
                'summary': 'Updated summary for expansion.',
                'story': self.listing.story,
                'use_of_funds': self.listing.use_of_funds,
                'target_timeline': self.listing.target_timeline,
                'website': '',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.restaurant_name, 'Saffron Table Updated')
        self.assertEqual(str(self.listing.funding_goal), '140000.00')

    def test_owner_can_delete_listing(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(
            reverse('listing_delete', kwargs={'slug': self.listing.slug}),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(InvestmentListing.objects.filter(pk=self.listing.pk).exists())


class AuthenticationFlowTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'newfounder',
                'email': 'newfounder@example.com',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(get_user_model().objects.filter(username='newfounder').exists())
        self.assertIn('_auth_user_id', self.client.session)
