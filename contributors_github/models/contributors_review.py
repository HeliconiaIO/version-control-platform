# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContributorsReview(models.Model):
    _name = "contributors.review"
    _description = "Contributors Review"  # TODO

    github_id = fields.Char(
        string="GitHub ID", readonly=True, required=True, index=True
    )
    body = fields.Html(readonly=True)
    state = fields.Char(readonly=True)
    partner_id = fields.Many2one("res.partner", readonly=True)
    submitted_at = fields.Datetime(readonly=True)
    pull_request_id = fields.Many2one(
        "contributors.pull.request",
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

    _sql_constraints = [
        ("github_id_uniq", "unique(github_id)", "GitHub ID must be unique.")
    ]
