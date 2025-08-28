from django.contrib.sitemaps import Sitemap
from .models import Publication, Club, Challenge, Page

class PublicationSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Publication.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # or obj.created_at

class ClubSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Club.objects.all()

class ChallengeSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Challenge.objects.all()

class PageSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.5

    def items(self):
        return Page.objects.all()
