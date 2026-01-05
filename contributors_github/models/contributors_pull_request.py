# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


class ContributorsPullRequest(models.Model):
    _name = "contributors.pull.request"
    _description = "Contributors Pull Request"  # TODO

    github_id = fields.Char(string="GitHub ID", readonly=True)
    name = fields.Char(readonly=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Contributor",
        readonly=True,
    )
    repository_id = fields.Many2one(
        comodel_name="contributors.repository",
        readonly=True,
        ondelete="cascade",
    )
    branch_id = fields.Many2one(
        comodel_name="contributors.branch",
        readonly=True,
        ondelete="restrict",
    )
    organization_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
    )
    url = fields.Char(readonly=True)
    state = fields.Char(readonly=True)
    is_merged = fields.Boolean(readonly=True)
    created_at = fields.Datetime(readonly=True)
    updated_at = fields.Datetime(readonly=True)
    closed_at = fields.Datetime(readonly=True)
    number = fields.Integer(readonly=True)
    label_ids = fields.Many2many(
        comodel_name="contributors.pull.request.label",
        string="Labels",
        readonly=True,
    )
    commits = fields.Integer(readonly=True)
    additions = fields.Integer(readonly=True)
    deletions = fields.Integer(readonly=True)
    total_comments = fields.Integer(readonly=True)
    review_comments = fields.Integer(readonly=True)

    _sql_constraints = [
        ("github_id_uniq", "unique(github_id)", "GitHub ID must be unique.")
    ]


class ContributorsPullRequestLabel(models.Model):
    _name = "contributors.pull.request.label"
    _description = "Contributors Pull Request Label"  # TODO

    name = fields.Char(required=True)

    _sql_constraints = [("name_uniq", "unique(name)", "Label name must be unique.")]

    @tools.ormcache()
    def _get_label(self, name):
        label = self.search([("name", "=", name)], limit=1)
        if not label:
            label = self.sudo().create({"name": name})
        return label.id
