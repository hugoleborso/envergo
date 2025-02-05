import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from envergo.moulinette.tests.factories import MoulinetteConfigFactory

pytestmark = pytest.mark.django_db


HOME_TITLE = "Évaluez à quelles réglementations votre projet de construction est soumis"
RESULT_TITLE = "Réglementations environnementales : évaluation personnalisée"
FORM_ERROR = (
    "Nous n'avons pas pu traiter votre demande car le formulaire contient des erreurs."
)
UNAVAIL = "Le simulateur EnvErgo n'est pas encore déployé dans votre département."
ADMIN_MSG = "Le simulateur n'est pas activé dans ce département"


def test_moulinette_home(client):
    url = reverse("moulinette_home")
    res = client.get(url)

    assert res.status_code == 200
    assert HOME_TITLE in res.content.decode()
    assert RESULT_TITLE not in res.content.decode()
    assert FORM_ERROR not in res.content.decode()


def test_moulinette_home_with_params_redirects_to_results_page(client):
    url = reverse("moulinette_home")
    params = "created_surface=500&final_surface=500&lng=-1.54394&lat=47.21381"
    full_url = f"{url}?{params}"
    res = client.get(full_url)
    assert res.status_code == 302
    assert res.url.startswith("/simulateur/resultat/")


def test_moulinette_result_without_config(client):
    """When dept. contact info is not set, eval is unavailable."""

    url = reverse("moulinette_result")
    params = "created_surface=500&final_surface=500&lng=-1.54394&lat=47.21381"
    full_url = f"{url}?{params}"
    res = client.get(full_url)

    assert res.status_code == 200
    assertTemplateUsed(res, "moulinette/result_non_disponible.html")


def test_moulinette_result_without_config_admin_access(client, admin_user):
    """When dept. contact info is not set, eval is unavailable, even for admins."""
    client.force_login(admin_user)

    url = reverse("moulinette_result")
    params = "created_surface=500&final_surface=500&lng=-1.54394&lat=47.21381"
    full_url = f"{url}?{params}"
    res = client.get(full_url)

    assert res.status_code == 200
    assertTemplateUsed(res, "moulinette/result_non_disponible.html")


def test_moulinette_result_with_deactivated_config(client):
    MoulinetteConfigFactory(is_activated=False)

    url = reverse("moulinette_result")
    params = "created_surface=500&final_surface=500&lng=-1.54394&lat=47.21381"
    full_url = f"{url}?{params}"
    res = client.get(full_url)

    assert res.status_code == 200
    assertTemplateUsed(res, "moulinette/result_available_soon.html")


def test_moulinette_result_with_deactivated_config_admin_access(client, admin_user):
    MoulinetteConfigFactory(is_activated=False)
    client.force_login(admin_user)

    url = reverse("moulinette_result")
    params = "created_surface=500&final_surface=500&lng=-1.54394&lat=47.21381"
    full_url = f"{url}?{params}"
    res = client.get(full_url)

    assert res.status_code == 200
    assertTemplateUsed(res, "moulinette/result.html")
    assert ADMIN_MSG in res.content.decode()


def test_moulinette_result_with_activated_config(client):
    MoulinetteConfigFactory(is_activated=True)

    url = reverse("moulinette_result")
    params = "created_surface=500&final_surface=500&lng=-1.54394&lat=47.21381"
    full_url = f"{url}?{params}"
    res = client.get(full_url)

    assert res.status_code == 200
    assertTemplateUsed(res, "moulinette/result.html")


def test_moulinette_result_without_params_redirects_to_home(client):
    url = reverse("moulinette_result")
    res = client.get(url)

    assert res.status_code == 302


def test_moulinette_result_form_error(client):
    url = reverse("moulinette_result")
    params = "bad_param=true"
    full_url = f"{url}?{params}"
    res = client.get(full_url)

    assert res.status_code == 302
    assert res.url.endswith("/simulateur/")


def test_moulinette_home_form_error(client):
    url = reverse("moulinette_home")
    params = "bad_param=true"
    full_url = f"{url}?{params}"
    res = client.get(full_url)

    assert res.status_code == 200
    assert HOME_TITLE in res.content.decode()
    assert RESULT_TITLE not in res.content.decode()
    assert FORM_ERROR in res.content.decode()


def test_moulinette_utm_param(client):
    url = reverse("moulinette_home")
    params = "utm_campaign=test"
    full_url = f"{url}?{params}"
    res = client.get(full_url)

    assert res.status_code == 200
    assert HOME_TITLE in res.content.decode()
    assert RESULT_TITLE not in res.content.decode()
    assert FORM_ERROR not in res.content.decode()
