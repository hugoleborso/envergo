from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from envergo.evaluations.forms import EvaluationFormMixin
from envergo.evaluations.models import Criterion, Evaluation, Request


class EvaluationAdminForm(EvaluationFormMixin, forms.ModelForm):
    pass


class CriterionAdminForm(forms.ModelForm):
    pass


class CriterionInline(admin.StackedInline):
    model = Criterion
    fields = ("order", "probability", "criterion", "description_md", "map", "legend_md")


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ["application_number", "created_at"]
    form = EvaluationAdminForm
    inlines = [CriterionInline]

    fieldsets = (
        (None, {"fields": ("application_number", "evaluation_file")}),
        (
            _("Project data"),
            {
                "fields": (
                    "commune",
                    "created_surface",
                    "existing_surface",
                )
            },
        ),
        (
            _("Evaluation report"),
            {"fields": ("global_probability",)},
        ),
        (
            _("Contact data"),
            {"fields": ("contact_md",)},
        ),
    )


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ["application_number", "created_at", "contact_email", "phone_number"]
    readonly_fields = ["created_at", "parcels"]
    fieldsets = (
        (_("Project localisation"), {"fields": ("address", "parcels")}),
        (
            _("Project data"),
            {
                "fields": (
                    "application_number",
                    "created_surface",
                    "existing_surface",
                )
            },
        ),
        (
            _("Contact info"),
            {
                "fields": (
                    "contact_email",
                    "phone_number",
                )
            },
        ),
        (_("Meta info"), {"fields": ("created_at",)}),
    )
