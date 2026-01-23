# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    psc_ids = fields.Many2many(
        comodel_name="contributors.organization.psc",
        readonly=True,
    )

    def _get_contributors_name(self, kind, psc_id=None, **kwargs):
        name = super()._get_contributors_name(kind, **kwargs)
        if kind == "contributors" and psc_id and psc_id in self.psc_ids.ids:
            name += " ★"
        return name
