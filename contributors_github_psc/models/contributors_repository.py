# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContributorsRepository(models.Model):
    _inherit = "contributors.repository"

    psc_id = fields.Many2one(
        "contributors.organization.psc",
        readonly=True,
    )
