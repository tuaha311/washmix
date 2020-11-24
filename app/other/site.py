from functools import update_wrapper

from django import forms
from django.contrib.admin import AdminSite
from django.urls import path
from django.views.generic.base import TemplateResponse

from other.media import Media


# metaclass definition copied from django.contrib.admin.options.BaseModelAdmin
class WashmixAdminSite(AdminSite, metaclass=forms.MediaDefiningClass):
    """
    Custom Admin site with few changes:
        - Custom site branding
        - Added new /pos/ route
        - Added new Media class with .js and .css definitions
    """

    site_header = "Washmix"
    site_title = "washmix.com"
    index_title = "Washmix Admin Panel"

    Media = Media

    def get_urls(self):
        """
        Here we are adding a new route /pos/ to the parent routes.
        """

        urls = super().get_urls()

        # start of copied part from django.contrib.admin.sites.AdminSite#get_urls
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        # end of copied part

        custom_urls = [
            path("pos/", wrap(self.pos), name="pos"),
        ]

        return urls + custom_urls

    def pos(self, request, extra_context=None):
        """
        Method that implement route /pos/. Strange pattern that used
        in AdminSite class. For consistence, we implemented a new view in same style.
        """

        # start of copied part from django.contrib.admin.sites.AdminSite views
        request.current_app = self.name

        context = {
            **self.each_context(request),
            "title": self.index_title,
            # injected by metaclass
            "media": self.media,
            **(extra_context or {}),
        }
        # end of copied part

        return TemplateResponse(request, "pos/index.html", context)

    def _build_app_dict(self, request, label=None):
        app_dict = super()._build_app_dict(request, label)

        return app_dict
