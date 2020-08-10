from django.core.management.base import BaseCommand

from locations.models import City, ZipCode

DEFAULT_CITIES_WITH_ZIP_CODES = [
    {"name": "Atherton", "zip_codes": ["94027"],},
    {"name": "Belmont", "zip_codes": ["94002"],},
    {"name": "Burlingame", "zip_codes": ["94011"],},
    {"name": "Campbell", "zip_codes": ["95008", "95009", "95011"],},
    {"name": "Cupertino", "zip_codes": ["95014", "95015"],},
    {"name": "Foster City", "zip_codes": ["94404"],},
    {"name": "Hillsborough", "zip_codes": ["94010"],},
    {"name": "Palo Alto", "zip_codes": ["94301", "94302", "94303", "94304", "94305", "94306"],},
    {"name": "Portola Valley", "zip_codes": ["94025", "94026", "94028"],},
    {"name": "Redwood City", "zip_codes": ["94061", "94062", "94063", "94064", "94065"],},
    {"name": "San Carlos", "zip_codes": ["94070"],},
    {"name": "San Mateo", "zip_codes": ["94401", "94402", "94403", "94497"],},
    {
        "name": "Santa Clara",
        "zip_codes": ["95050", "95051", "95052", "95053", "95054", "95055", "95056"],
    },
    {
        "name": "San Jose",
        "zip_codes": [
            "94088",
            "95106",
            "95120",
            "95124",
            "95128",
            "95153",
            "95157",
            "95164",
            "95190",
            "95194",
            "95108",
            "95112",
            "95117",
            "95125",
            "95129",
            "95154",
            "95158",
            "95170",
            "95191",
            "95196",
            "95109",
            "95113",
            "95118",
            "95126",
            "95130",
            "95134",
            "95155",
            "95160",
            "95172",
            "95192",
            "95002",
            "95103",
            "95110",
            "95115",
            "95123",
            "95173",
            "95193",
        ],
    },
    {"name": "Los Altos", "zip_codes": ["94022", "94023", "94024"],},
    {"name": "Los Altos Hills", "zip_codes": ["94022", "94023", "94024"],},
    {"name": "Los Gatos", "zip_codes": ["95030", "95032", "95033"],},
    {"name": "Menlo Park", "zip_codes": ["94025", "94026", "94028"],},
    {"name": "Mountain View", "zip_codes": ["94040", "94041", "94042", "94043"],},
    {"name": "Saratoga", "zip_codes": ["95070", "95071"],},
    {"name": "Stanford", "zip_codes": ["94301", "94302", "94303", "94304", "94305", "94306"],},
    {"name": "Sunnyvale", "zip_codes": ["94085", "94086", "94087", "94089"],},
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for item in DEFAULT_CITIES_WITH_ZIP_CODES:
            city, _ = City.objects.update_or_create(name=item["name"])

            for element in item["zip_codes"]:
                zip_code, _ = ZipCode.objects.update_or_create(value=element)
                city.zip_code_list.add(zip_code)

            print(f"{zip_code} added for {city}")
