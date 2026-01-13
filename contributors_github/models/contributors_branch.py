# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContributorsBranch(models.Model):
    _name = "contributors.branch"
    _description = "Contributors Branch"  # TODO

    name = fields.Char(required=True)
    organization_id = fields.Many2one(
        comodel_name="contributors.organization",
        string="Organization",
        required=True,
    )
    _sql_constraints = [
        ("name_uniq", "unique(name, organization_id)", "Branch name must be unique.")
    ]
