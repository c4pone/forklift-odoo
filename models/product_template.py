from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_forklift = fields.Boolean('Is a Forklift', default=False)
    forklift_id = fields.Many2one('forklift.forklift', readonly=True, string="Forklift")