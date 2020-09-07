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
    - https://docs.djangoproject.com/en/22/ref/django-admin/#dumpdata
    - https://docs.djangoproject.com/en/22/topics/serialization/#topics-serialization-natural-keys
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
        "price": 19900,
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
        "price": 29900,
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
# Coupons
#

COUPONS = [
    {"code": "AMOUNT", "discount_by": "amount", "value_off": 1000,},
    {"code": "PERCENTAGE", "discount_by": "percentage", "value_off": 20,},
]


#
# Admins
#

ADMINS = [
    {
        # has a good payment method - success
        # card № 4000 0025 0000 3155
        "email": "api@evrone.com",
        "password": "helloevrone",
        "number": "12001230210",
        "is_superuser": True,
        "is_staff": True,
        "stripe_id": "cus_HsLFiIYxwKsoOC",
    },
    {
        # has a good payment method - success
        # card № 4242 4242 4242 4242
        "email": "ds.ionin@evrone.com",
        "password": "helloevrone",
        "number": "12001230211",
        "is_superuser": True,
        "is_staff": True,
        "stripe_id": "cus_HxSYa6ACuzQdtS",
    },
    {
        # has bad payment method - fail
        # card № 4000 0000 0000 9995
        "email": "savoskin@evrone.com",
        "password": "helloevrone",
        "number": "12001230212",
        "is_superuser": True,
        "is_staff": True,
        "stripe_id": "cus_HxSYL19Joq6KTq",
    },
    {
        # have no any payment methods - fail
        "email": "og@evrone.com",
        "password": "helloevrone",
        "number": "12001230213",
        "is_superuser": True,
        "is_staff": True,
        "stripe_id": "cus_HxSY7DuMrXnEc1",
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
        "service": "Laundry",
        "item_list": [
            {
                "item": "Blouse [Hang Press]",
                "is_visible": False,
                "price": {"value": 695, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Pants",
                "is_visible": False,
                "price": {"value": 695, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jeans",
                "is_visible": False,
                "price": {"value": 695, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Polo",
                "is_visible": False,
                "price": {"value": 595, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt",
                "is_visible": False,
                "price": {"value": 595, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt [Press + Hang] [Cotton]",
                "is_visible": True,
                "price": {"value": 395, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt [Press + Fold] [Cotton]",
                "is_visible": True,
                "price": {"value": 695, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "T-shirt",
                "is_visible": True,
                "price": {"value": 595, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shorts",
                "is_visible": False,
                "price": {"value": 595, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Tuxedo Shirt",
                "is_visible": True,
                "price": {"value": 795, "count": 1, "unit": Price.PCS},
            },
        ],
    },
    {
        "service": "Dry Cleaning",
        "item_list": [
            {
                "item": "Blouse",
                "is_visible": True,
                "price": {"value": 595, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blouse [Hang-Press]",
                "is_visible": False,
                "price": {"value": 695, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Blazer",
                "is_visible": True,
                "price": {"value": 1295, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Coat [Reg]",
                "is_visible": True,
                "price": {"value": 1495, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Coat [Long]",
                "is_visible": False,
                "price": {"value": 1695, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Coat [Full Length]",
                "is_visible": False,
                "price": {"value": 1995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Dress [Reg]",
                "is_visible": True,
                "price": {"value": 1395, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Dress [Fancy]",
                "is_visible": False,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Dress [Grown] [Minimal price $2995]",
                "is_visible": True,
                "price": {"value": 3995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Dress [Fancy]",
                "is_visible": False,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Jacket [Reg]",
                "is_visible": True,
                "price": {"value": 1595, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Jacket [Leather] [Minimal price $4995]",
                "is_visible": True,
                "price": {"value": 4995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pants",
                "is_visible": True,
                "price": {"value": 695, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Jeans",
                "is_visible": False,
                "price": {"value": 695, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Polo",
                "is_visible": True,
                "price": {"value": 595, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Scarf [Reg]",
                "is_visible": True,
                "price": {"value": 595, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Scarf or Shall [Large]",
                "is_visible": False,
                "price": {"value": 795, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Shirt",
                "is_visible": True,
                "price": {"value": 595, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Shirt Press + Fold [Cotton]",
                "is_visible": False,
                "price": {"value": 895, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Shirt Press + Hung [Cotton]",
                "is_visible": False,
                "price": {"value": 595, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "T-shirt",
                "is_visible": False,
                "price": {"value": 595, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Shorts",
                "is_visible": True,
                "price": {"value": 595, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Skirts [Reg]",
                "is_visible": True,
                "price": {"value": 595, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Skirts [Long]",
                "is_visible": False,
                "price": {"value": 795, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Dress [Fancy]",
                "is_visible": False,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sweater [Reg]",
                "is_visible": True,
                "price": {"value": 595, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sweater [Heavy]",
                "is_visible": False,
                "price": {"value": 795, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sweater [Body]",
                "is_visible": False,
                "price": {"value": 995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Suits [2 Pcs]",
                "is_visible": True,
                "price": {"value": 1995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Suits [3 Pcs]",
                "is_visible": False,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Ties",
                "is_visible": True,
                "price": {"value": 495, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Tuxedo [2 Pcs]",
                "is_visible": True,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Tuxedo [3 Pcs]",
                "is_visible": True,
                "price": {"value": 3495, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Tuxedo shirt",
                "is_visible": False,
                "price": {"value": 995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Vest",
                "is_visible": True,
                "price": {"value": 595, "count": 1, "unit": Price.PCS,},
            },
        ],
    },
    {
        "service": "Wash & Folds",
        "item_list": [
            {
                "item": "Option 1 [min 20 LBS]",
                "is_visible": True,
                "price": {"value": 399, "count": 1, "unit": Price.LBS},
            },
            {
                "item": "Option 2 [1 Bag]",
                "is_visible": True,
                "price": {"value": 7900, "count": 1, "unit": Price.BAG},
            },
            {
                "item": "Option 2 [2 Bag]",
                "is_visible": True,
                "price": {"value": 14800, "count": 1, "unit": Price.BAG},
            },
            {
                "item": "Option 2 [3 Bag]",
                "is_visible": True,
                "price": {"value": 20700, "count": 3, "unit": Price.BAG},
            },
            {
                "item": "Option 2 [4 Bag]",
                "is_visible": True,
                "price": {"value": 25600, "count": 1, "unit": Price.BAG},
            },
            {
                "item": "Option 2 [Each Bag thereafter 4 Bags] [245 + 49$ per Additional Bag]",
                "is_visible": True,
                "price": {"value": 4900, "count": 1, "unit": Price.BAG},
            },
        ],
    },
    {
        "service": "Households",
        "item_list": [
            {
                "item": "Bed Sheet [Set] [4 PCs]",
                "is_visible": True,
                "price": {"value": 2695, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Bed Sheet [Single]",
                "is_visible": True,
                "price": {"value": 1295, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blanket [Single or Twin]",
                "is_visible": True,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Blanket [Q/K]",
                "is_visible": False,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Single or Twin]",
                "is_visible": True,
                "price": {"value": 3495, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Q/K]",
                "is_visible": False,
                "price": {"value": 3995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Down] [Signle Twin]",
                "is_visible": True,
                "price": {"value": 4495, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Comforter [Down] [Q/K]",
                "is_visible": False,
                "price": {"value": 4995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Curtain [Per panel]",
                "is_visible": True,
                "price": {"value": 3995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Draperies [Short or Unlined]",
                "is_visible": True,
                "price": {"value": 495, "count": 1, "unit": Price.PLEAT,},
            },
            {
                "item": "Draperies [Long or Lined]",
                "is_visible": False,
                "price": {"value": 895, "count": 1, "unit": Price.PLEAT,},
            },
            {
                "item": "Napkin",
                "is_visible": True,
                "price": {"value": 395, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Reg]",
                "is_visible": True,
                "price": {"value": 1995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Med]",
                "is_visible": False,
                "price": {"value": 3995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Large]",
                "is_visible": False,
                "price": {"value": 5995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Ex-Large]",
                "is_visible": False,
                "price": {"value": 9995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Case]",
                "is_visible": True,
                "price": {"value": 595, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Pillow [Sham]",
                "is_visible": False,
                "price": {"value": 795, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sofa Cover",
                "is_visible": True,
                "price": {"value": 3995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sofa Cover [Large]",
                "is_visible": False,
                "price": {"value": 5995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Sofa Cover [Ex-Large]",
                "is_visible": False,
                "price": {"value": 8995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Table Cloth [Small]",
                "is_visible": True,
                "price": {"value": 1695, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Table Cloth [Large]",
                "is_visible": False,
                "price": {"value": 1995, "count": 1, "unit": Price.PCS,},
            },
            {
                "item": "Table Cloth [Ex-Large]",
                "is_visible": False,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS,},
            },
        ],
    },
    {
        "service": "Alterations & Repair",
        "item_list": [
            {
                "item": "Button Replacement [With Cleaning]",
                "is_visible": True,
                "price": {"value": 395, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Button Replacement [Without Cleaning]",
                "is_visible": True,
                "price": {"value": 795, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Button Replacement [Special] [Minimal Price $995]",
                "is_visible": False,
                "price": {"value": 995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Button Replacement [Without Cleaning]",
                "is_visible": False,
                "price": {"value": 795, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blouse Hem [Reg]",
                "is_visible": True,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blouse Sleeves [Reg]",
                "is_visible": False,
                "price": {"value": 2695, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blouse Taper [Reg]",
                "is_visible": True,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blazer Sleeves [Reg]",
                "is_visible": True,
                "price": {"value": 4995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blazer Hem [Reg]",
                "is_visible": False,
                "price": {"value": 9995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blazer Shoulder [Reg]",
                "is_visible": False,
                "price": {"value": 29995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Blazer Taper [Reg]",
                "is_visible": True,
                "price": {"value": 14995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Hem [Reg]",
                "is_visible": False,
                "price": {"value": 6995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Sleeves [Reg]",
                "is_visible": True,
                "price": {"value": 6995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Taper [Reg]",
                "is_visible": False,
                "price": {"value": 14995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Shoulder [Reg]",
                "is_visible": False,
                "price": {"value": 29995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Hem [Long]",
                "is_visible": False,
                "price": {"value": 6995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Sleeves [Long]",
                "is_visible": True,
                "price": {"value": 6995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Taper [Long]",
                "is_visible": False,
                "price": {"value": 14995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Shoulder [Long]",
                "is_visible": False,
                "price": {"value": 29995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Hem [Full Length]",
                "is_visible": False,
                "price": {"value": 6995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Sleeves [Full Length]",
                "is_visible": False,
                "price": {"value": 6995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Taper [Full Length]",
                "is_visible": False,
                "price": {"value": 14995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Coat Shoulder [Full Length]",
                "is_visible": False,
                "price": {"value": 29995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Hem [Reg]",
                "is_visible": True,
                "price": {"value": 4995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Taper [Reg]",
                "is_visible": True,
                "price": {"value": 6995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Zipper [Reg]",
                "is_visible": True,
                "price": {"value": 5995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Hem [Fancy]",
                "is_visible": False,
                "price": {"value": 6995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Taper [Fancy]",
                "is_visible": False,
                "price": {"value": 9995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Zipper [Fancy]",
                "is_visible": False,
                "price": {"value": 7995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Hem [Gown]",
                "is_visible": False,
                "price": {"value": 14995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Taper [Gown]",
                "is_visible": False,
                "price": {"value": 19995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Dress Zipper [Gown]",
                "is_visible": False,
                "price": {"value": 9995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jacket Hem [Reg]",
                "is_visible": False,
                "price": {"value": 7995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jacket Taper [Reg]",
                "is_visible": False,
                "price": {"value": 14995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jacket Sleeves [Reg]",
                "is_visible": False,
                "price": {"value": 5995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jacket Shoulder [Reg]",
                "is_visible": False,
                "price": {"value": 29995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Pants Hem [Reg]",
                "is_visible": True,
                "price": {"value": 1895, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Pants Hem [Original]",
                "is_visible": True,
                "price": {"value": 2295, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Pants Tapper [Reg]",
                "is_visible": True,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Pants Waist [IN or Out]",
                "is_visible": True,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Pants Zipper [Reg]",
                "is_visible": True,
                "price": {"value": 1995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Hem [Reg]",
                "is_visible": True,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Tapper [Reg]",
                "is_visible": False,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Waist [Reg]",
                "is_visible": True,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Zipper [Reg]",
                "is_visible": False,
                "price": {"value": 1295, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Hem [Long]",
                "is_visible": False,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Tapper [Long]",
                "is_visible": False,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Waist [Long]",
                "is_visible": False,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Skirt Zipper [Long]",
                "is_visible": False,
                "price": {"value": 1295, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Zipper Replaced [Minimal price $20]",
                "is_visible": True,
                "price": {"value": 1995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sleeves Shortened [Minimal Price $25]",
                "is_visible": True,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Meding [Tears or Misc] [Minimal Price $10]",
                "is_visible": True,
                "price": {"value": 995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jeans Hem [Original]",
                "is_visible": False,
                "price": {"value": 2295, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jeans Waist [Reg]",
                "is_visible": False,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jeans Tapper [Reg]",
                "is_visible": False,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Jeans Zipper [Reg]",
                "is_visible": False,
                "price": {"value": 1995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Hem [Reg]",
                "is_visible": False,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Sleeve [Reg]",
                "is_visible": False,
                "price": {"value": 2695, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Tapper [Reg]",
                "is_visible": False,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Hem [Cotton]",
                "is_visible": False,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Sleeve [Cotton]",
                "is_visible": False,
                "price": {"value": 2695, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Tapper [Cotton]",
                "is_visible": False,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Hem [Cotton][Fold]",
                "is_visible": False,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Sleeve [Cotton] [Fold]",
                "is_visible": False,
                "price": {"value": 2695, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt Tapper [Cotton] [Fold]",
                "is_visible": False,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Hem [Reg]",
                "is_visible": False,
                "price": {"value": 2295, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Tapper [Reg]",
                "is_visible": False,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Zipper [Req]",
                "is_visible": False,
                "price": {"value": 2295, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Hem [Heavy]",
                "is_visible": False,
                "price": {"value": 2295, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Tapper [Heavy]",
                "is_visible": False,
                "price": {"value": 2995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Zipper [Heavy]",
                "is_visible": False,
                "price": {"value": 2795, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Hem [Body]",
                "is_visible": False,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Tapper [Body]",
                "is_visible": False,
                "price": {"value": 3495, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Sweater Zipper [Body]",
                "is_visible": False,
                "price": {"value": 3995, "count": 1, "unit": Price.PCS},
            },
        ],
    },
    {
        "service": "Wedding Growns",
        "item_list": [
            {
                "item": "Clean Only [Minimal price $14995]",
                "is_visible": True,
                "price": {"value": 14995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Clean + Preservation [Minimal price $29995]",
                "is_visible": True,
                "price": {"value": 29995, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Additional Accessories [Minimal price $2495]",
                "is_visible": True,
                "price": {"value": 2495, "count": 1, "unit": Price.PCS},
            },
        ],
    },
    {
        "service": "Rug Area",
        "item_list": [
            {
                "item": "Machine Made [Minimal price $99]",
                "is_visible": True,
                "price": {"value": 39500, "count": 1, "unit": Price.SQ_FT},
            },
            {
                "item": "Handmade Rug [Persian/Indian] [Minimal Price $99]",
                "is_visible": True,
                "price": {"value": 69500, "count": 1, "unit": Price.SQ_FT},
            },
            {
                "item": "Cowhide Rug [Minimal Price 99$]",
                "is_visible": True,
                "price": {"value": 9900, "count": 1, "unit": Price.PCS},
            },
        ],
    },
]
