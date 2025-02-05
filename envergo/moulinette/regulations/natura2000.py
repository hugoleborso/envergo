from functools import cached_property

from django import forms
from django.contrib.gis.measure import Distance as D
from django.utils.translation import gettext_lazy as _

from envergo.evaluations.models import RESULTS
from envergo.moulinette.regulations import (
    Map,
    MapPolygon,
    MoulinetteCriterion,
    MoulinetteRegulation,
)

BLUE = "blue"
LIGHTBLUE = "lightblue"


class ZoneHumide44(MoulinetteCriterion):
    slug = "zone_humide_44"
    choice_label = "Natura 2000 > 44 - Zone humide"
    title = "Impact sur zone humide Natura 2000"
    subtitle = "Seuil réglementaire : 100 m²"
    header = "« Liste locale 2 » Natura 2000 en Loire-Atlantique (13° de l'art. 1 de l'<a href='/static/pdfs/arrete_08042014.pdf' target='_blank' rel='noopener'>arrêté préfectoral du 8 avril 2014</a>)"  # noqa

    CODES = [
        "soumis",
        "non_soumis",
        "action_requise_proche",
        "non_soumis_proche",
        "action_requise_dans_doute",
        "non_soumis_dans_doute",
        "non_concerne",
    ]

    def get_catalog_data(self):
        data = {}

        if "wetlands_25" not in data:
            data["wetlands_25"] = [
                zone for zone in self.catalog["wetlands"] if zone.distance <= D(m=25)
            ]
            data["wetlands_within_25m"] = bool(data["wetlands_25"])

        if "wetlands_100" not in data:
            data["wetlands_100"] = [
                zone for zone in self.catalog["wetlands"] if zone.distance <= D(m=100)
            ]
            data["wetlands_within_100m"] = bool(data["wetlands_100"])

        if "potential_wetlands_0" not in data:
            data["potential_wetlands_0"] = [
                zone
                for zone in self.catalog["potential_wetlands"]
                if zone.distance <= D(m=0)
            ]
            data["potential_wetlands_within_0m"] = bool(data["potential_wetlands_0"])

        return data

    def get_result_data(self):
        """Evaluate the project and return the different parameter results.

        For this criterion, the evaluation results depends on the project size
        and wether it will impact known wetlands.
        """

        if self.catalog["wetlands_within_25m"]:
            wetland_status = "inside"
        elif self.catalog["wetlands_within_100m"]:
            wetland_status = "close_to"
        elif self.catalog["potential_wetlands_within_0m"]:
            wetland_status = "inside_potential"
        else:
            wetland_status = "outside"

        if self.catalog["created_surface"] >= 100:
            project_size = "big"
        else:
            project_size = "small"

        return wetland_status, project_size

    @property
    def result_code(self):
        """Return the unique result code"""

        wetland_status, project_size = self.get_result_data()
        code_matrix = {
            ("inside", "big"): "soumis",
            ("inside", "small"): "non_soumis",
            ("close_to", "big"): "action_requise_proche",
            ("close_to", "small"): "non_soumis_proche",
            ("inside_potential", "big"): "action_requise_dans_doute",
            ("inside_potential", "small"): "non_soumis_dans_doute",
            ("outside", "big"): "non_concerne",
            ("outside", "small"): "non_concerne",
        }
        code = code_matrix[(wetland_status, project_size)]
        return code

    @cached_property
    def result(self):
        """Run the check for the 3.3.1.0 rule.

        Associate a unique result code with a value from the RESULTS enum.
        """

        code = self.result_code
        result_matrix = {
            "soumis": RESULTS.soumis,
            "non_soumis": RESULTS.non_soumis,
            "action_requise_proche": RESULTS.action_requise,
            "non_soumis_proche": RESULTS.non_soumis,
            "action_requise_dans_doute": RESULTS.action_requise,
            "non_soumis_dans_doute": RESULTS.non_soumis,
            "non_concerne": RESULTS.non_concerne,
        }
        result = result_matrix[code]
        return result

    def _get_map(self):
        map_polygons = []

        wetlands_qs = [
            zone for zone in self.catalog["wetlands"] if zone.map.display_for_user
        ]
        if wetlands_qs:
            map_polygons.append(MapPolygon(wetlands_qs, BLUE, "Zone humide"))

        potential_qs = [
            zone
            for zone in self.catalog["potential_wetlands"]
            if zone.map.display_for_user
        ]
        if potential_qs:
            map_polygons.append(
                MapPolygon(potential_qs, LIGHTBLUE, "Zone humide potentielle")
            )

        if self.catalog["wetlands_within_25m"]:
            caption = "Le projet se situe dans une zone humide référencée."

        elif (
            self.catalog["wetlands_within_100m"]
            and not self.catalog["potential_wetlands_within_0m"]
        ):
            caption = "Le projet se situe à proximité d'une zone humide référencée."

        elif (
            self.catalog["wetlands_within_100m"]
            and self.catalog["potential_wetlands_within_0m"]
        ):
            caption = "Le projet se situe à proximité d'une zone humide référencée et dans une zone humide potentielle."
        elif self.catalog["potential_wetlands_within_0m"] and potential_qs:
            caption = "Le projet se situe dans une zone humide potentielle."
        else:
            caption = "Le projet ne se situe pas dans zone humide référencée."

        if map_polygons:
            criterion_map = Map(
                center=self.catalog["coords"],
                entries=map_polygons,
                caption=caption,
                truncate=False,
            )
        else:
            criterion_map = None

        return criterion_map


class ZoneInondable44(MoulinetteCriterion):
    slug = "zone_inondable_44"
    choice_label = "Natura 2000 > 44 - Zone inondable"
    title = "Impact sur zone inondable Natura 2000"
    subtitle = "Seuil réglementaire : 200 m²"
    header = "« Liste locale 2 » Natura 2000 en Loire-Atlantique (10° de l'art. 1 de l'<a href='/static/pdfs/arrete_08042014.pdf' target='_blank' rel='noopener'>arrêté préfectoral du 8 avril 2014</a>)"  # noqa

    CODES = ["soumis", "non_soumis", "non_concerne"]

    def get_catalog_data(self):
        data = {}

        if "flood_zones_12" not in self.catalog:
            data["flood_zones_12"] = [
                zone for zone in self.catalog["flood_zones"] if zone.distance <= D(m=12)
            ]
            data["flood_zones_within_12m"] = bool(data["flood_zones_12"])
        return data

    @cached_property
    def result_code(self):
        """Run the check for the 3.1.2.0 rule."""

        if self.catalog["flood_zones_within_12m"]:
            flood_zone_status = "inside"
        else:
            flood_zone_status = "outside"

        if self.catalog["final_surface"] >= 200:
            project_size = "big"
        else:
            project_size = "small"

        result_matrix = {
            "inside": {
                "big": RESULTS.soumis,
                "small": RESULTS.non_soumis,
            },
            "outside": {
                "big": RESULTS.non_concerne,
                "small": RESULTS.non_concerne,
            },
        }

        result = result_matrix[flood_zone_status][project_size]
        return result

    def _get_map(self):
        zone_qs = [
            zone for zone in self.catalog["flood_zones"] if zone.map.display_for_user
        ]

        if zone_qs:
            if self.catalog["flood_zones_within_12m"]:
                caption = "Le projet se situe dans une zone inondable."
            else:
                caption = "Le projet ne se situe pas en zone inondable."

            map_polygons = [MapPolygon(zone_qs, "red", "Zone inondable")]
            criterion_map = Map(
                center=self.catalog["coords"],
                entries=map_polygons,
                caption=caption,
                truncate=False,
            )
        else:
            criterion_map = None

        return criterion_map


class IOTA(MoulinetteCriterion):
    slug = "iota"
    choice_label = "Natura 2000 > IOTA"
    title = "Natura 2000 si dossier Loi sur l'eau"
    header = "« Liste nationale » Natura 2000 (4° du I de l'<a href='https://www.legifrance.gouv.fr/codes/id/LEGISCTA000022090322/' target='_blank' rel='noopener'>article R414-19 du Code de l'Environnement</a>)"  # noqa

    CODES = ["soumis", "non_soumis", "a_verifier"]

    @cached_property
    def result_code(self):
        iota = self.moulinette.loi_sur_leau.result
        if iota in (RESULTS.soumis, RESULTS.interdit):
            result = RESULTS.soumis
        elif iota == RESULTS.non_soumis:
            result = RESULTS.non_soumis
        else:
            result = RESULTS.a_verifier

        return result


class LotissementForm(forms.Form):

    # I sacrificed a frog to the god of bad translations for the right to use
    # this variable name. Sorry.
    is_lotissement = forms.ChoiceField(
        label=_("Le projet concerne-t-il un lotissement ?"),
        widget=forms.RadioSelect,
        choices=(("oui", "Oui"), ("non", "Non")),
        required=True,
    )


class Lotissement(MoulinetteCriterion):
    slug = "lotissement"
    choice_label = "Natura 2000 > Lotissement"
    title = "Lotissement dans zone Natura 2000"
    form_class = LotissementForm

    CODES = [
        "soumis_dedans",
        "soumis_proximite_immediate",
        "non_soumis",
        "non_disponible",
    ]

    def get_distance_to_n2000(self):
        perimeters = self.moulinette.perimeters
        perimeter = next((p for p in perimeters if p.criterion == type(self)), None)
        return perimeter.distance.m

    @cached_property
    def result_code(self):

        form = self.get_form()
        if form.is_valid():
            distance_to_n2000 = self.get_distance_to_n2000()
            is_lotissement = form.cleaned_data["is_lotissement"] == "oui"

            if is_lotissement:
                if distance_to_n2000 <= 0.0:
                    code = "soumis_dedans"
                else:
                    code = "soumis_proximite_immediate"
            else:
                code = "non_soumis"

            return code

        return "non_disponible"

    @cached_property
    def result(self):
        code = self.result_code
        result_matrix = {
            "soumis_dedans": RESULTS.soumis,
            "soumis_proximite_immediate": RESULTS.soumis,
            "non_soumis": RESULTS.non_soumis,
            "non_disponible": RESULTS.non_disponible,
        }
        result = result_matrix[code]
        return result


class Lotissement44(Lotissement):
    # Note : this is the legacy name of the criterion.
    # It was renamed "Lotissement", but we keep the old name to avoid breaking
    # existing perimeters.
    slug = "lotissement_44"
    choice_label = "Natura 2000 > 44 - Lotissement (obsolète)"


class Natura2000(MoulinetteRegulation):
    slug = "natura2000"
    title = "Natura 2000"
    criterion_classes = [ZoneHumide44, ZoneInondable44, IOTA, Lotissement]

    @cached_property
    def result(self):
        """Compute global result from individual criterions."""

        results = [criterion.result for criterion in self.criterions]

        if RESULTS.soumis in results:
            result = RESULTS.soumis
        elif RESULTS.action_requise in results:
            result = RESULTS.action_requise
        elif RESULTS.a_verifier in results:
            result = RESULTS.iota_a_verifier
        else:
            result = RESULTS.non_soumis

        return result

    def iota_only(self):
        """Is the IOTA criterion the only valid criterion.

        There is an edge case where projects can be subject to Natura2000 only
        because they are subject to IOTA, even though they are outsite
        Natura 2000 zones.
        """
        return len(self.criterions) == 1 and isinstance(self.criterions[0], IOTA)

    def _get_map(self):
        """Display a Natura 2000 map if a single criterion has been activated.

        Since there is probably a single Natura 2000 map for all Natura 2000
        criterions, we only display a single polygon and a single map source.

        The IOTA criterion must not be taken into account, though, because it's
        perimeter will likely be entire departments, so displaying it will not
        be relevant.
        """

        # Let's find the first perimeter with a map that we can display
        perimeter = next(
            (
                p
                for p in self.moulinette.perimeters
                if p.criterion in self.criterion_classes
                and not p.criterion == IOTA
                and p.map.display_for_user
            ),
            None,
        )
        if not perimeter:
            return None

        map_polygons = [MapPolygon([perimeter], "green", "Site Natura 2000")]

        if perimeter.distance.m <= 0.0:
            caption = "Le projet se situe sur un site Natura 2000."
        else:
            caption = "Le projet se situe à proximité immédiate d’un site Natura 2000."

        map = Map(
            center=self.catalog["coords"],
            entries=map_polygons,
            caption=caption,
            truncate=False,
            zoom=15,
        )

        return map
