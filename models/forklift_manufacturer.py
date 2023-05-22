# models/manufacturer.py
from odoo import models, fields

class Manufacturer(models.Model):
    _name = 'forklift.manufacturer'
    _description = 'Forklift Manufacturer'

    name = fields.Char(string='Manufacturer Name', required=True)