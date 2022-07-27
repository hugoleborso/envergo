from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as D
from django.db import models
from django.utils.translation import gettext_lazy as _

from envergo.geodata.models import Department
from envergo.moulinette.fields import CriterionChoiceField
from envergo.moulinette.regulations.natura2000 import Natura2000
from envergo.moulinette.regulations.waterlaw import WaterLaw

# WGS84, geodetic coordinates, units in degrees
# Good for storing data and working wordwide
EPSG_WGS84 = 4326

# Projected coordinates
# Used for displaying tiles in web map systems (OSM, GoogleMaps)
# Good for working in meters
EPSG_MERCATOR = 3857


class Perimeter(models.Model):
    """Link a map and regulation criteria."""

    name = models.CharField(_("Name"), max_length=256)
    map = models.ForeignKey(
        "geodata.Map",
        verbose_name=_("Map"),
        related_name="perimeters",
        on_delete=models.PROTECT,
    )
    criterion = CriterionChoiceField(_("Criterion"))

    class Meta:
        verbose_name = _("Perimeter")
        verbose_name_plural = _("Perimeters")

    def __str__(self):
        return self.name


class MoulinetteCatalog(dict):
    """Custom class responsible for fetching data used in regulation evaluations."""

    pass


class Moulinette:
    """Automatic environment law evaluation processing tool.

    Given a bunch of relevant user provided data, we try to perform an
    automatic computation and tell if the project is subject to the Water Law
    or other regulations.
    """

    def __init__(self, data):
        self.catalog = MoulinetteCatalog(**data)
        self.catalog.update(self.get_catalog_data())
        self.criterions = self.get_criterions(self.catalog['coords'])
        self.regulations = [WaterLaw(self.catalog, self.criterions), Natura2000(self.catalog, self.criterions)]

    def get_catalog_data(self):
        """Fetch / compute data required for further computations."""

        lng = self.catalog["lng"]
        lat = self.catalog["lat"]
        lng_lat = Point(float(lng), float(lat), srid=EPSG_WGS84)

        catalog = {}
        catalog["project_surface"] = (
            self.catalog["existing_surface"] + self.catalog["created_surface"]
        )

        catalog["coords"] = lng_lat.transform(EPSG_MERCATOR, clone=True)
        catalog["department"] = Department.objects.filter(
            geometry__contains=lng_lat
        ).first()
        catalog["circle_12"] = catalog["coords"].buffer(12)
        catalog["circle_25"] = catalog["coords"].buffer(25)
        catalog["circle_100"] = catalog["coords"].buffer(100)
        return catalog

    def get_criterions(self, coords):
        """Find regulation criterions activated by a perimeter.

        Regulation criterions have a geographical component and must only computed in
        certain zones.
        """
        perimeters = Perimeter.objects.filter(map__zones__geometry__dwithin=(coords, D(m=0)))
        criterions = [perimeter.criterion for perimeter in perimeters]
        return criterions

    def is_evaluation_available(self):
        """Moulinette evaluations are only available on some departments.

        When a department is available, we fill it's contact data.
        """
        department = self.catalog["department"]
        contact_info = getattr(department, "contact_md", None)
        return bool(contact_info)

    def __getattr__(self, attr):
        """Returs the corresponding regulation.

        Allows to do something like this:
        moulinette.water_law to fetch the correct regulation.
        """
        return self.get_regulation(attr)

    def get_regulation(self, regulation_slug):
        """Return the regulation with the given slug."""

        def select_regulation(regulation):
            return regulation.slug == regulation_slug

        regul = next(filter(select_regulation, self.regulations), None)
        return regul

    def result(self):
        """Export all results as a dict."""

        result = {}
        for regulation in self.regulations:
            result[regulation.slug] = {
                "result": regulation.result,
                "criterions": {},
            }
            for criterion in regulation.criterions:
                result[regulation.slug]["criterions"][criterion.slug] = criterion.result

        return result
