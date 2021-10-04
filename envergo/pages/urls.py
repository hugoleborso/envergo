from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from envergo.evaluations.views import RequestEvaluation

urlpatterns = [
    path("", RequestEvaluation.as_view(), name="home"),
    path(
        _("legal-mentions/"),
        TemplateView.as_view(template_name="pages/legal_mentions.html"),
        name="legal_mentions",
    ),
    path(
        _("accessibility/"),
        TemplateView.as_view(template_name="pages/accessibility.html"),
        name="accessibility",
    ),
    path(
        _("contact-us/"),
        TemplateView.as_view(template_name="pages/contact_us.html"),
        name="contact_us",
    ),
    path(
        _("water-law/"),
        TemplateView.as_view(template_name="pages/water_law.html"),
        name="water_law",
    ),
    path(
        _("map/"),
        TemplateView.as_view(template_name="pages/map.html"),
        name="map",
    ),
]
