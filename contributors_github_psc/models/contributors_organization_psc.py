# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContributorsOrganizationPsc(models.Model):
    _name = "contributors.organization.psc"
    _description = "Contributors Organization Psc"  # TODO

    organization_id = fields.Many2one(
        comodel_name="contributors.organization",
        string="Organization",
        required=True,
    )
    name = fields.Char(required=True)
    key = fields.Char(required=True)
    member_ids = fields.Many2many(
        "res.partner",
        readonly=True,
    )
