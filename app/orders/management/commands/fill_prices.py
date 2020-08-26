from django.core.management.base import BaseCommand
from django.db import transaction

from orders.models import Item, Price, Service

PRICE_LIST = [
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


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            for raw_service in PRICE_LIST:
                service, _ = Service.objects.update_or_create(title=raw_service["service"],)
                print(f"service {service} added")

                for raw_item in raw_service["item_list"]:
                    item, _ = Item.objects.update_or_create(
                        title=raw_item["item"], defaults={"is_visible": raw_item["is_visible"],}
                    )
                    print(f"item {item} added")

                    raw_price = raw_item["price"]
                    price, _ = Price.objects.update_or_create(
                        service=service,
                        item=item,
                        defaults={
                            "value": raw_price["value"],
                            "count": raw_price["count"],
                            "unit": raw_price["unit"],
                        },
                    )
                    print(f"price {price} added")
