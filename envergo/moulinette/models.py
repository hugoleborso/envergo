from django.contrib.gis.geos import Point
from django.core.serializers import serialize

from envergo.geodata.models import Department
from envergo.moulinette.regulations import WaterLaw

# WGS84, geodetic coordinates, units in degrees
# Good for storing data and working wordwide
EPSG_WGS84 = 4326

# Projected coordinates
# Used for displaying tiles in web map systems (OSM, GoogleMaps)
# Good for working in meters
EPSG_MERCATOR = 3857


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
        self.regulations = [WaterLaw(self.catalog)]

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
