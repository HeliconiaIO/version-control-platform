# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    psc_ids = fields.Many2many(
        comodel_name="contributors.organization.psc",
        readonly=True,
    )
