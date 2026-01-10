# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContributorsRepository(models.Model):
    _inherit = "contributors.repository"

    weblate_url = fields.Char(related="organization_id.weblate_url")
