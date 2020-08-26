from orders.models import Price

"""
Why we use native objects instead of storing them as JSON (fixtures)?

Because fixtures have some problems:
- They don't give a guarantee that relations such as ForeignKey, OneToOne, ManyToMany
will be resolved correctly. Relations by default represented as integers (PK) and 
at records creation time, `loaddata` doesn't guarantee a correct order of model creation.
Preferable, to use `--natural-foreign` and `--natural-primary` with `dumpdata` command.
But it require of implementation `get_by_natural_key` and `natural_key` method on models and managers.
Reference:
    - https://docs.djangoproject.com/en/2.2/ref/django-admin/#dumpdata
    - https://docs.djangoproject.com/en/2.2/topics/serialization/#topics-serialization-natural-keys
- Fixture doesn't provide a guarantee between ports of databases. As example, we can't load data
from PostgreSQL into SQLite and vice versa.
"""


#
# Packages
#

PACKAGES = [
    {
        "name": "payc",
        "description": "Pay as You Clean",
        "price": 0,
        "dry_clean": 0,
        "laundry": 0,
        "wash_fold": 0,
        "alterations": 0,
        "has_delivery": False,
        "has_welcome_box": False,
        "has_seasonal_garment": False,
        "has_credit_back": False,
        "is_most_popular": False,
    },
    {
        "name": "gold",
        "description": "Pre Pay Credit",
        "price": 199,
        "dry_clean": 10,
        "laundry": 10,
        "wash_fold": 10,
        "alterations": 10,
        "has_delivery": True,
        "has_welcome_box": True,
        "has_seasonal_garment": False,
        "has_credit_back": False,
        "is_most_popular": False,
    },
    {
        "name": "platinum",
        "price": 299,
        "dry_clean": 20,
        "laundry": 20,
        "wash_fold": 20,
        "alterations": 20,
        "has_delivery": True,
        "has_welcome_box": True,
        "has_seasonal_garment": True,
        "has_credit_back": True,
        "is_most_popular": True,
    },
]


#
# Admins
#

ADMINS = [
    {
        "email": "api@evrone.com",
        "password": "helloevrone",
        "number": "12001230210",
        "is_superuser": True,
        "is_staff": True,
    },
    {
        "email": "ds.ionin@evrone.com",
        "password": "helloevrone",
        "number": "12001230211",
        "is_superuser": True,
        "is_staff": True,
    },
    {
        "email": "savoskin@evrone.com",
        "password": "helloevrone",
        "number": "12001230212",
        "is_superuser": True,
        "is_staff": True,
    },
    {
        "email": "og@evrone.com",
        "password": "helloevrone",
        "number": "12001230213",
        "is_superuser": True,
        "is_staff": True,
    },
]


#
# Cities
#

CITIES = [
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


#
# Prices
#

PRICES = [
    {
        "service": "Dry Cleaning",
        "item_list": [
            {
                "item": "Blouse",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blouse [Hang-Press]",
                "is_visible": False,
                "price": {"value": 6.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Blazer",
                "is_visible": True,
                "price": {"value": 12.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Coat [Med]",
                "is_visible": True,
                "price": {"value": 14.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Coat [Long]",
                "is_visible": False,
                "price": {"value": 16.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Coat [Full Length]",
                "is_visible": False,
                "price": {"value": 19.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Dress [Reg]",
                "is_visible": True,
                "price": {"value": 13.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Dress [Fancy]",
                "is_visible": False,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Dress [Grown] [Minimal price 29.95$]",
                "is_visible": True,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Dress [Fancy]",
                "is_visible": False,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Jacket [Reg]",
                "is_visible": True,
                "price": {"value": 15.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Jacket [Leather] [Minimal price 49.95$]",
                "is_visible": True,
                "price": {"value": 49.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pants",
                "is_visible": True,
                "price": {"value": 6.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Jeans",
                "is_visible": True,
                "price": {"value": 6.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Polo",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Scarf [Reg]",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Scarf or Shall [Large]",
                "is_visible": True,
                "price": {"value": 7.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Shirt",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Shirt Press + Fold [Cotton]",
                "is_visible": True,
                "price": {"value": 8.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Shirt Press + Hung [Cotton]",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "T-shirt",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Shorts",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Skirts",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Skirts [Long]",
                "is_visible": True,
                "price": {"value": 7.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Dress [Fancy]",
                "is_visible": False,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sweater [Reg]",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sweater [Heavy]",
                "is_visible": False,
                "price": {"value": 7.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sweater [Body]",
                "is_visible": False,
                "price": {"value": 9.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Suits [2 Pcs]",
                "is_visible": True,
                "price": {"value": 19.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Suits [3 Pcs]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Ties",
                "is_visible": True,
                "price": {"value": 4.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Tuxedo [2 Pcs]",
                "is_visible": True,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Tuxedo [3 Pcs]",
                "is_visible": True,
                "price": {"value": 34.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Tuxedo shirt",
                "is_visible": True,
                "price": {"value": 9.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Vest",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Bed Sheet [Set][4 Pcs]",
                "is_visible": True,
                "price": {"value": 26.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Bed Sheet [Single]",
                "is_visible": True,
                "price": {"value": 12.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Blanket [Single or Twin]",
                "is_visible": True,
                "price": {"value": 12.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Blanket [Q/K]",
                "is_visible": False,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Single or Twin]",
                "is_visible": True,
                "price": {"value": 34.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Q/K]",
                "is_visible": False,
                "price": {"value": 39.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Down] [Signle or Twin]",
                "is_visible": True,
                "price": {"value": 44.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Down] [Q/K]",
                "is_visible": False,
                "price": {"value": 49.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Curtain [Per panel]",
                "is_visible": True,
                "price": {"value": 39.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Draperies [Short or Unlined]",
                "is_visible": True,
                "price": {"value": 4.95, "count": 1, "unit": Price.PLEAT,},
            },
            {
                "item": "Draperies [Long or Lined]",
                "is_visible": False,
                "price": {"value": 8.95, "count": 1, "unit": Price.PLEAT,},
            },
            {
                "item": "Napkin",
                "is_visible": True,
                "price": {"value": 3.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Reg]",
                "is_visible": True,
                "price": {"value": 19.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Med]",
                "is_visible": True,
                "price": {"value": 39.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Large]",
                "is_visible": True,
                "price": {"value": 59.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Ex-Large]",
                "is_visible": True,
                "price": {"value": 99.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Case]",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Sham]",
                "is_visible": False,
                "price": {"value": 7.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sofa Cover [Med]",
                "is_visible": True,
                "price": {"value": 39.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sofa Cover [Large]",
                "is_visible": False,
                "price": {"value": 59.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sofa Cover [Ex-Large]",
                "is_visible": False,
                "price": {"value": 89.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Table Cloth [Small]",
                "is_visible": True,
                "price": {"value": 16.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Table Cloth [Large]",
                "is_visible": False,
                "price": {"value": 19.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Table Cloth [Ex-Large]",
                "is_visible": False,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Wedding Gowns [Minimal price 149.95 $]",
                "is_visible": True,
                "price": {"value": 149.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Wedding Gowns [Additional Accessories] [Minimal Price 24.95$]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS,},
            },
        ],
    },
    {
        "service": "Laundry",
        "item_list": [
            {
                "item": "Blouse [Hang Press]",
                "is_visible": False,
                "price": {"value": 6.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Pants",
                "is_visible": False,
                "price": {"value": 6.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jeans",
                "is_visible": False,
                "price": {"value": 6.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Polo",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt [Press + Hang] [Cotton]",
                "is_visible": True,
                "price": {"value": 3.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt [Press + Fold] [Cotton]",
                "is_visible": True,
                "price": {"value": 6.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "T-shirt",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shorts",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Tuxedo Shirt",
                "is_visible": True,
                "price": {"value": 7.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Bed Sheet [Set] [4 PCs]",
                "is_visible": True,
                "price": {"value": 26.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Bed Sheet [Single]",
                "is_visible": True,
                "price": {"value": 12.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blanket [Single or Twin]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Blanket [Q/K]",
                "is_visible": False,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Single or Twin]",
                "is_visible": True,
                "price": {"value": 34.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Q/K]",
                "is_visible": False,
                "price": {"value": 39.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Down] [Signle or Twin]",
                "is_visible": True,
                "price": {"value": 44.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Down] [Q/K]",
                "is_visible": False,
                "price": {"value": 49.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Napkin",
                "is_visible": True,
                "price": {"value": 3.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Reg]",
                "is_visible": True,
                "price": {"value": 19.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Med]",
                "is_visible": True,
                "price": {"value": 39.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Large]",
                "is_visible": True,
                "price": {"value": 59.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Ex-Large]",
                "is_visible": True,
                "price": {"value": 99.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Case]",
                "is_visible": True,
                "price": {"value": 5.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Sham]",
                "is_visible": False,
                "price": {"value": 7.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sofa Cover [Med]",
                "is_visible": True,
                "price": {"value": 39.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sofa Cover [Large]",
                "is_visible": False,
                "price": {"value": 59.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sofa Cover [Ex-Large]",
                "is_visible": False,
                "price": {"value": 89.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Table Cloth [Small]",
                "is_visible": True,
                "price": {"value": 16.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Table Cloth [Large]",
                "is_visible": False,
                "price": {"value": 19.95, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Table Cloth [Ex-Large]",
                "is_visible": False,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS,},
            },
        ],
    },
    {
        "service": "Alterations & Repair",
        "item_list": [
            {
                "item": "Blouse Hem [Reg]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blouse Sleeves [Reg]",
                "is_visible": True,
                "price": {"value": 26.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blouse Taper [Reg]",
                "is_visible": True,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blazer Hem [Reg]",
                "is_visible": True,
                "price": {"value": 99.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blazer Sleeves [Reg]",
                "is_visible": True,
                "price": {"value": 49.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blazer Shoulder [Reg]",
                "is_visible": True,
                "price": {"value": 299.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blazer Taper [Reg]",
                "is_visible": True,
                "price": {"value": 149.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Hem [Reg]",
                "is_visible": True,
                "price": {"value": 69.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Sleeves [Reg]",
                "is_visible": True,
                "price": {"value": 69.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Taper [Reg]",
                "is_visible": True,
                "price": {"value": 149.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Shoulder [Reg]",
                "is_visible": True,
                "price": {"value": 299.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Hem [Long]",
                "is_visible": True,
                "price": {"value": 69.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Sleeves [Long]",
                "is_visible": True,
                "price": {"value": 69.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Taper [Long]",
                "is_visible": True,
                "price": {"value": 149.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Shoulder [Long]",
                "is_visible": True,
                "price": {"value": 299.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Hem [Full Length]",
                "is_visible": True,
                "price": {"value": 69.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Sleeves [Full Length]",
                "is_visible": True,
                "price": {"value": 69.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Taper [Full Length]",
                "is_visible": True,
                "price": {"value": 149.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Shoulder [Full Length]",
                "is_visible": True,
                "price": {"value": 299.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Hem [Reg]",
                "is_visible": True,
                "price": {"value": 49.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Taper [Reg]",
                "is_visible": True,
                "price": {"value": 69.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Zipper [Reg]",
                "is_visible": True,
                "price": {"value": 59.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Hem [Fancy]",
                "is_visible": True,
                "price": {"value": 69.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Taper [Fancy]",
                "is_visible": True,
                "price": {"value": 99.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Zipper [Fancy]",
                "is_visible": True,
                "price": {"value": 79.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Hem [Gown]",
                "is_visible": True,
                "price": {"value": 149.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Taper [Gown]",
                "is_visible": True,
                "price": {"value": 199.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Zipper [Gown]",
                "is_visible": True,
                "price": {"value": 99.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jacket Hem [Reg]",
                "is_visible": True,
                "price": {"value": 79.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jacket Taper [Reg]",
                "is_visible": True,
                "price": {"value": 149.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jacket Sleeves [Reg]",
                "is_visible": True,
                "price": {"value": 59.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jacket Shoulder [Reg]",
                "is_visible": True,
                "price": {"value": 299.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Pants Hem [Reg]",
                "is_visible": True,
                "price": {"value": 18.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Pants Hem [Original]",
                "is_visible": True,
                "price": {"value": 22.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Pants Waist [IN or Out]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Pants Zipper [Reg]",
                "is_visible": True,
                "price": {"value": 19.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Zipper Repair [Minimal price 20$]",
                "is_visible": True,
                "price": {"value": 19.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sleeves Shortened [Minimal Price 25$]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Meding [Tears or Misc] [Minimal Price 10$]",
                "is_visible": True,
                "price": {"value": 9.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Button Replacement [With Cleaning]",
                "is_visible": True,
                "price": {"value": 3.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Button Replacement [Without Cleaning]",
                "is_visible": True,
                "price": {"value": 7.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Button Replacement [Special] [Minimal Price 9.95$]",
                "is_visible": True,
                "price": {"value": 9.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Button Replacement [Without Cleaning]",
                "is_visible": True,
                "price": {"value": 7.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jeans Hem [Original]",
                "is_visible": True,
                "price": {"value": 22.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jeans Waist [Reg]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jeans Tapper [Reg]",
                "is_visible": True,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jeans Zipper [Reg]",
                "is_visible": True,
                "price": {"value": 19.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Hem [Reg]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Sleeve [Reg]",
                "is_visible": True,
                "price": {"value": 26.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Tapper [Reg]",
                "is_visible": True,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Hem [Cotton]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Sleeve [Cotton]",
                "is_visible": True,
                "price": {"value": 26.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Tapper [Cotton]",
                "is_visible": True,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Hem [Cotton] [Fold]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Sleeve [Cotton] [Fold]",
                "is_visible": True,
                "price": {"value": 26.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Tapper [Cotton] [Fold]",
                "is_visible": True,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Hem [Reg]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Tapper [Reg]",
                "is_visible": True,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Waist [Reg]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Zipper [Reg]",
                "is_visible": True,
                "price": {"value": 12.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Hem [Long]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Tapper [Long]",
                "is_visible": True,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Waist [Long]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Zipper [Long]",
                "is_visible": True,
                "price": {"value": 12.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Hem [Reg]",
                "is_visible": True,
                "price": {"value": 22.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Tapper [Reg]",
                "is_visible": True,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Zipper [Req]",
                "is_visible": True,
                "price": {"value": 22.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Hem [Heavy]",
                "is_visible": True,
                "price": {"value": 22.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Tapper [Heavy]",
                "is_visible": True,
                "price": {"value": 29.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Zipper [Heavy]",
                "is_visible": True,
                "price": {"value": 27.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Hem [Body]",
                "is_visible": True,
                "price": {"value": 24.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Tapper [Body]",
                "is_visible": True,
                "price": {"value": 34.95, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Zipper [Body]",
                "is_visible": True,
                "price": {"value": 39.95, "count": 1, "unit": Price.PCS},
            },
        ],
    },
    {
        "service": "Wash & Folds",
        "item_list": [
            {
                "item": "Option 1 [min 20 LBS]",
                "is_visible": True,
                "price": {"value": 3.99, "count": 1, "unit": Price.LBS},
            },
            {
                "item": "Option 2 [1 Bag]",
                "is_visible": True,
                "price": {"value": 79, "count": 1, "unit": Price.BAG},
            },
            {
                "item": "Option 2 [2 Bag]",
                "is_visible": True,
                "price": {"value": 148, "count": 1, "unit": Price.BAG},
            },
            {
                "item": "Option 2 [3 Bag]",
                "is_visible": True,
                "price": {"value": 207, "count": 3, "unit": Price.BAG},
            },
            {
                "item": "Option 2 [4 Bag]",
                "is_visible": True,
                "price": {"value": 256, "count": 1, "unit": Price.BAG},
            },
            {
                "item": "Option 2 [Each Bag thereafter 4 Bags] [245 + 49 per Additional Bag]",
                "is_visible": True,
                "price": {"value": 49, "count": 1, "unit": Price.BAG},
            },
        ],
    },
    {
        "service": "Rug Cleaning",
        "item_list": [
            {
                "item": "Machinemade Rug",
                "is_visible": True,
                "price": {"value": 3.95, "count": 1, "unit": Price.SQ_FT},
            },
            {
                "item": "Handmade Rug [Persian/Indian] [Minimal Price 100$]",
                "is_visible": True,
                "price": {"value": 6.95, "count": 1, "unit": Price.SQ_FT},
            },
            {
                "item": "Cowhide Rug [Minimal Price 99$]",
                "is_visible": True,
                "price": {"value": 99, "count": 1, "unit": Price.PCS},
            },
        ],
    },
    {
        "service": "Dry cleaning + Preservation",
        "item_list": [
            {
                "item": "Wedding Gowns",
                "is_visible": True,
                "price": {"value": 299.95, "count": 1, "unit": Price.PCS},
            },
        ],
    },
]
