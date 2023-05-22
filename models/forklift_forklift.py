import uuid

from odoo import _, api, fields, models, tools


class ForkliftImage(models.Model):
    _name = "forklift.forklift_image"
    _description = "Forklift Image"

    image = fields.Binary(string="Image", attachment=True)
    forklift_id = fields.Many2one(
        "forklift.forklift", string="Forklift", ondelete="cascade"
    )


class Forklift(models.Model):
    _name = "forklift.forklift"
    _description = "Forklift Model"

    _description_fields = [
        "manufacturer_id",
        "type",
        "year_built",
        "lifting_capacity_kg",
        "lifting_height_mm",
        "mast_type",
        "hydraulic_control_circuits",
        "optical_condition",
        "technical_condition",
        "battery",
        "charging_connector",
        "lighting",
        "cabin",
        "air_conditioning",
        "driver_protection",
        "wheels",
        "wheel_axle",
    ]

    product_id = fields.Many2one(
        "product.template",
        "Product",
        help="Product configure",
        ondelete="cascade",
        readonly=True,
    )
    category_id = fields.Many2one("product.category", string="Category")
    manufacturer_id = fields.Many2one("forklift.manufacturer", string="Manufacturer")
    image_ids = fields.One2many(
        "forklift.forklift_image", "forklift_id", string="Images"
    )

    type = fields.Char(string="Type")
    price = fields.Float(string="Price")
    device_type = fields.Char(string="Device Type")
    device_structure = fields.Char(string="Device Structure")
    serial_number = fields.Char(string="Serial Number")
    year_built = fields.Integer(string="Year Built")
    empty_weight = fields.Float(string="Empty Weight")
    battery_weight = fields.Float(string="Battery Weight")
    operating_hours = fields.Float(string="Operating Hours")
    lifting_capacity_kg = fields.Float(string="Lifting Capacity (kg)")
    lifting_height_mm = fields.Float(string="Lifting Height (mm)")
    construction_height_mm = fields.Float(string="Construction Height (mm)")
    free_lift_mm = fields.Float(string="Free Lift (mm)")
    mast_type = fields.Char(string="Mast Type")
    hydraulic_control_circuits = fields.Char(string="Hydraulic Control Circuits")
    additional_function = fields.Char(string="Additional Function")
    internal_reference = fields.Char(string="Internal Reference")
    barcode = fields.Char(string="Barcode")
    product_keywords = fields.Char(string="Product Keywords")
    battery = fields.Char(string="Battery")
    charging_connector = fields.Char(string="Charging Connector")
    fork_length = fields.Float(string="Fork Length")
    next_inspection_date = fields.Date(string="Next Inspection Date")
    optical_condition = fields.Selection(
        [
            ("excellent", "Excellent"),
            ("good", "Good"),
            ("average", "Average"),
            ("poor", "Poor"),
        ],
        string="Optical Condition",
    )
    technical_condition = fields.Selection(
        [
            ("excellent", "Excellent"),
            ("good", "Good"),
            ("average", "Average"),
            ("poor", "Poor"),
        ],
        string="Technical Condition",
    )
    device_status = fields.Selection(
        [("available", "Available"), ("unavailable", "Unavailable")],
        string="Device Status",
    )
    lighting = fields.Boolean(string="Lighting")
    cabin = fields.Boolean(string="Cabin")
    air_conditioning = fields.Boolean(string="Air Conditioning")
    driver_protection = fields.Boolean(string="Driver Protection")
    wheels = fields.Char(string="Wheels")
    wheel_axle = fields.Char(string="Wheel/Axle")

    @api.model
    def create(self, data):
        # Extract the first image data if it exists
        images_data = data.get("image_ids", [])
        first_image_data = None
        if len(images_data) > 0:
            first_image_data = images_data[0][2]["image"]
            images_data = images_data[1:]

        # Create the forklift record
        forklift = super(Forklift, self.with_context(mail_create_nolog=True)).create(
            data
        )

        # Handle the manufacturer attribute
        attribute = self._get_or_create_attribute("Manufacturer")
        attribute_value = self._get_or_create_attribute_value(
            attribute, forklift.manufacturer_id.name
        )

        # Create the product and assign its ID to the forklift
        product = self._create_product(
            forklift, first_image_data, data.get("price", 0.0)
        )
        forklift.product_id = product.id
        product.forklift_id = forklift.id

        self._set_product_images(product, images_data)
        self._create_product_attribute_line(product, attribute, attribute_value)

        return forklift

    def write(self, vals):
        res = super(Forklift, self).write(vals)
        if vals.get("type") or any(field in vals for field in self._description_fields):
            for forklift in self:
                forklift.product_id.description_sale = forklift._generate_description()
        return res

    def open_related_product(self):
        self.ensure_one()
        return {
            "name": "Related Product",
            "type": "ir.actions.act_window",
            "res_model": "product.template",
            "res_id": self.product_id.id,
            "view_mode": "form",
            "target": "current",
        }

    @api.model
    @tools.ormcache("attribute_name")
    def _get_or_create_attribute(self, attribute_name):
        # Check if the attribute exists or create one if it doesn't
        attribute = self.env["product.attribute"].search(
            [("name", "=", attribute_name)], limit=1
        )
        if not attribute:
            attribute = self.env["product.attribute"].create({"name": attribute_name})
        return attribute

    @api.model
    @tools.ormcache("attribute", "value_name")
    def _get_or_create_attribute_value(self, attribute, value_name):
        # Check if the attribute value exists or create one if it doesn't
        attribute_value = self.env["product.attribute.value"].search(
            [
                ("attribute_id", "=", attribute.id),
                ("name", "=", value_name),
            ],
            limit=1,
        )
        if not attribute_value:
            attribute_value = self.env["product.attribute.value"].create(
                {
                    "attribute_id": attribute.id,
                    "name": value_name,
                }
            )
        return attribute_value

    def _create_product(self, forklift, first_image_data, price):
        # Prepare the product data
        product_data = {
            "name": f"{forklift.manufacturer_id.name} {forklift.type}",
            "type": "consu",
            "detailed_type": "consu",
            "categ_id": forklift.category_id.id,
            "description_sale": forklift._generate_description(),
            "list_price": price,
        }

        # Assign the first image data if it exists
        if first_image_data:
            product_data["image_1920"] = first_image_data

        # Create the product
        product = self.env["product.template"].create(product_data)

        return product

    def _create_product_attribute_line(self, product, attribute, attribute_value):
        # Create a product attribute line for the product
        self.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": product.id,
                "attribute_id": attribute.id,
                "value_ids": [(6, 0, [attribute_value.id])],
            }
        )

    def _set_product_images(self, product, images_data):
        for image_data in images_data:
            data = image_data[2]
            self.env["product.image"].create(
                {
                    "name": str(uuid.uuid4()),
                    "image_1920": data["image"],
                    "product_tmpl_id": product.id,
                }
            )

    def _generate_description(self):
        description = _(
            "This {} {} forklift, built in {}, has a lifting capacity of {} kg and a lifting height of {} mm. It features a {} mast type and {} hydraulic control circuits. The forklift is in {} optical condition and {} technical condition. It comes with a {} battery and {} charging connector."
        ).format(
            self.manufacturer_id.name,
            self.type,
            self.year_built,
            self.lifting_capacity_kg,
            self.lifting_height_mm,
            self.mast_type,
            self.hydraulic_control_circuits,
            self.optical_condition,
            self.technical_condition,
            self.battery,
            self.charging_connector,
        )
        if self.lighting:
            description += _(" The forklift is equipped with lighting.")
        if self.cabin:
            description += _(" It also has a cabin.")
        if self.air_conditioning:
            description += _(" Air conditioning is installed for the driver's comfort.")
        if self.driver_protection:
            description += _(" Driver protection features are also included.")

        description += _(
            " The forklift has {} wheels and a {} wheel/axle configuration."
        ).format(self.wheels, self.wheel_axle)
        return description

    def unlink(self):
        products_to_unlink = self.mapped("product_id")
        res = super(Forklift, self).unlink()
        products_to_unlink.unlink()
        return res
