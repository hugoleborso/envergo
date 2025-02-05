from django import forms
from django.conf import settings
from django.contrib.postgres.forms import SimpleArrayField
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

from envergo.evaluations.models import USER_TYPES, Request
from envergo.evaluations.validators import application_number_validator


class EvaluationFormMixin(forms.Form):
    """Common code for all evaluation forms."""

    # We don't set `maxlength` to 15 because we want to allow copy-pasting
    # values with spaces
    application_number = forms.CharField(
        label=_("Application number"),
        help_text="15 caractères commençant par « PA », « PC », « DP » ou « CU »",
        max_length=64,
    )

    def clean_application_number(self):
        dirty_number = self.cleaned_data.get("application_number")
        if dirty_number == "":
            return ""

        clean_number = dirty_number.replace(" ", "").strip().upper()
        application_number_validator(clean_number)
        return clean_number


class EvaluationSearchForm(forms.Form):
    """Search for a single evaluation."""

    reference = forms.CharField(
        label=_("EnvErgo reference"),
        help_text=_("The value you received when you requested an evaluation."),
        max_length=64,
    )


class WizardAddressForm(EvaluationFormMixin, forms.ModelForm):
    address = forms.CharField(
        label=_("What is the project's address?"),
        help_text=_("Type in a few characters to see suggestions"),
    )
    no_address = forms.BooleanField(
        label=_("This project is not linked to an address"),
        required=False,
    )
    application_number = forms.CharField(
        label=_("Application number"),
        help_text=_("If an application number was already submitted."),
        max_length=64,
    )

    class Meta:
        fields = ["application_number", "address", "project_description"]
        model = Request

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["application_number"].required = False
        self.fields["application_number"].widget.attrs["placeholder"] = _(
            "15 caractères commençant par « PA », « PC », « DP » ou « CU »"
        )
        self.fields["project_description"].widget.attrs["rows"] = 3

    def clean(self):
        data = super().clean()
        no_address = data.get("no_address", False)
        if no_address:
            self.fields["address"].required = False
            if "address" in self._errors:
                del self._errors["address"]

        return data


class WizardContactForm(forms.ModelForm):

    user_type = forms.ChoiceField(
        label="Vous êtes :",
        required=True,
        choices=USER_TYPES,
        initial=USER_TYPES.instructor,
        widget=forms.RadioSelect,
    )
    contact_email = forms.EmailField(
        label=_("Urbanism department email"), help_text=_("Project instructor…")
    )
    project_sponsor_emails = SimpleArrayField(
        forms.EmailField(),
        label=_("Project sponsor email address(es)"),
        help_text=_("Petitioner, project manager…"),
        error_messages={"item_invalid": _("The %(nth)s address is invalid:")},
    )
    project_sponsor_phone_number = PhoneNumberField(
        label=_("Project sponsor phone number"), region="FR"
    )
    send_eval_to_sponsor = forms.BooleanField(
        label=_("Send evaluation to project sponsor"),
        initial=True,
        required=False,
        help_text=_(
            "If you uncheck this box, you will be the only recipient of the evaluation."
        ),
    )

    class Meta:
        model = Request
        fields = [
            "user_type",
            "contact_email",
            "project_sponsor_emails",
            "send_eval_to_sponsor",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project_sponsor_emails"].widget.attrs["placeholder"] = _(
            "Provide one or several addresses separated by commas « , »"
        )

    def clean_project_sponsor_phone_number(self):
        phone = self.cleaned_data["project_sponsor_phone_number"]
        return str(phone)

    def clean(self):
        """Custom form field validation.

        Some contact fields are removed depending on the user type.
        """
        data = super().clean()
        user_type = data.get("user_type", None)
        if user_type == USER_TYPES.petitioner:
            self.fields["contact_email"].required = False
            if "contact_email" in self._errors:
                del self._errors["contact_email"]
            if "contact_email" in data:
                del data["contact_email"]

        return data


class WizardFilesForm(forms.ModelForm):
    additional_files = forms.FileField(
        label=_("Additional files you might deem useful for the evaluation"),
        required=False,
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
        help_text=f"""
            Formats autorisés : images (png, jpg), pdf, zip. <br>
            Maximum {settings.MAX_EVALREQ_FILES} fichiers. <br>
            Maximum 20 Mo par fichier. <br>
        """,
    )

    class Meta:
        model = Request
        fields = ["additional_files"]


class RequestForm(WizardAddressForm, WizardContactForm):
    class Meta:
        model = Request
        fields = [
            "address",
            "application_number",
            "project_description",
            "user_type",
            "contact_email",
            "project_sponsor_emails",
            "project_sponsor_phone_number",
            "send_eval_to_sponsor",
        ]


class EvaluationShareForm(forms.Form):
    emails = SimpleArrayField(
        forms.EmailField(),
        label=_("Select your recipient(s) email address(es)"),
        help_text=_("Separate several addresses with a comma « , »"),
        error_messages={"item_invalid": _("The %(nth)s address is invalid:")},
    )
