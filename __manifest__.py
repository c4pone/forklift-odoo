# -*- coding: utf-8 -*-
# More info at https://www.odoo.com/documentation/master/reference/module.html
{
    "name": "Forklift Management",
    "version": "1.0",
    "author": "Florian Kirchner",
    "category": "Warehouse",
    "license": "LGPL-3",
    "summary": "Manage forklifts as products in eCommerce",
    "depends": ["base", "product", "website_sale"],
    "data": [
        "views/forklift_detail_page.xml",
        "views/action_product_form.xml",
        "views/forklift_views.xml",
        "views/manufacturer_views.xml",
        "views/forklift_menu.xml",
        "views/forklift_image_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": True,
}
