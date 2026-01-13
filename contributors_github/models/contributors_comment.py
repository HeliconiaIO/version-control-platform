# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContributorsComment(models.Model):
    _name = "contributors.comment"
    _description = "Contributors Comment"  # TODO

    github_id = fields.Char(readonly=True, required=True, index=True)
    body = fields.Html(readonly=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
    )
    organization_id = fields.Many2one(
        related="pull_request_id.organization_id",
        readonly=True,
        store=True,
    )
    repository_id = fields.Many2one(
        related="pull_request_id.repository_id",
        readonly=True,
        store=True,
    )
    created_at = fields.Datetime(readonly=True)
    updated_at = fields.Datetime(readonly=True)
    pull_request_id = fields.Many2one(
        comodel_name="contributors.pull.request",
        string="Pull Request",
        readonly=True,
    )
    _sql_constraints = [
        ("github_id_uniq", "unique(github_id)", "GitHub ID must be unique.")
    ]
