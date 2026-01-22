# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
    url = fields.Char(compute="_compute_url")

    @api.depends("organization_id", "key")
    def _compute_url(self):
        for record in self:
            record.url = f"https://github.com/orgs/{record.organization_id.name}/projects/{record.key}"
