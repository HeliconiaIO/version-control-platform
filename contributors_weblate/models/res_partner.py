# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    weblate_translations = fields.Integer(
        compute="_compute_github_contributions", string="Translations", prefetch=False
    )

    @api.model
    def _get_contributors_field_map(self):
        result = super()._get_contributors_field_map()
        result["weblate_translations"] = "translations"
        return result
