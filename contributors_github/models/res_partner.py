# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import github3

from odoo import api, fields, models, tools


class ResPartner(models.Model):
    _inherit = "res.partner"

    github_name = fields.Char(
        string="GitHub Username",
        help="GitHub username of the contributor or organization",
        readonly=True,
    )
    github_organization = fields.Boolean(
        string="Is GitHub Organization",
        help="Check if this partner represents a GitHub organization",
        readonly=True,
    )
    github_user = fields.Boolean(
        string="Is GitHub User",
        help="Check if this partner represents a GitHub user",
        readonly=True,
    )
    github_merged_pull_requests = fields.Integer(
        compute="_compute_github_contributions",
        string="Merged Pull Requests",
        prefetch=False,
    )
    github_created_pull_requests = fields.Integer(
        compute="_compute_github_contributions",
        string="Created Pull Requests",
        prefetch=False,
    )
    github_comments = fields.Integer(
        compute="_compute_github_contributions", string="Comments", prefetch=False
    )
    github_reviews = fields.Integer(
        compute="_compute_github_contributions", string="Reviews", prefetch=False
    )

    _sql_constraints = [
        (
            "github_name_uniq",
            "unique(github_name)",
            "The GitHub username must be unique across partners.",
        ),
    ]

    @api.depends("github_name")
    def _compute_github_contributions(self):
        self.filtered(lambda p: p.github_user)._compute_github_contributions_field(
            "partner_id"
        )
        self.filtered(lambda p: not p.github_user)._compute_github_contributions_field(
            "organization_id"
        )

    @api.model
    def _get_contributors_field_map(self):
        return {
            "github_merged_pull_requests": "merged_pull_requests",
            "github_created_pull_requests": "created_pull_requests",
            "github_comments": "comments",
            "github_reviews": "reviews",
        }

    def _compute_github_contributions_field(self, field):
        today = fields.Date.today()
        start, end = self.env["contributors.organization"]._get_dates(
            today.year, today.month, "MAT"
        )
        data = (
            self.env["contributors.organization"]
            .search([])
            ._generate_data(
                start=start, end=end, field=field, kind="user", extra_domain=[]
            )
        )
        field_map = self._get_contributors_field_map()
        for partner in self:
            partner.update(
                {key: data[partner.id].get(field_map[key], 0) for key in field_map}
            )

    @tools.ormcache("github_login")
    def _get_github_user_id(self, github_login):
        partner = self.with_context(active_test=False).search(
            [("github_name", "=ilike", github_login)], limit=1
        )
        if not partner:
            return False
        if not partner.github_user:
            partner.github_user = True
        return partner.id

    @tools.ormcache("github_login")
    def _get_github_organization_id(self, github_login):
        partner = self.with_context(active_test=False).search(
            [("github_name", "=ilike", github_login)], limit=1
        )
        if not partner:
            return False
        if not partner.github_organization:
            partner.github_organization = True
        return partner.id

    def _get_github_user(self, gh, client):
        if not gh:
            return False
        if isinstance(gh, github3.users.User):
            github_login = gh.login
        else:
            github_login = str(gh)
        partner = self._get_github_user_id(github_login)
        if partner:
            return partner
        if isinstance(gh, str):
            try:
                gh = client.user(github_login)
                name = gh.name or github_login
            except github3.exceptions.NotFoundError:
                name = gh
        else:
            if hasattr(gh, "name"):
                name = gh.name or github_login
            else:
                name = github_login
        self.env.registry.clear_cache()
        return self.create(
            {
                "name": name,
                "github_name": github_login,
                "github_user": True,
            }
        ).id

    def _get_github_organization(self, gh, client):
        if not gh:
            return False
        partner = self._get_github_organization_id(str(gh))
        if partner:
            return partner
        self.env.registry.clear_cache()
        try:
            org = client.organization(str(gh))

            return self.create(
                {
                    "name": org.name or str(gh),
                    "github_name": str(gh),
                    "github_organization": True,
                }
            ).id
        except github3.exceptions.NotFoundError:
            user = client.user(str(gh))
            name = user.name or str(gh)
        except github3.exceptions.ForbiddenError:
            name = str(gh)
        return self.create(
            {
                "name": name,
                "github_name": str(gh),
                "github_user": True,
                "github_organization": True,
            }
        ).id

    def _get_contributor_url(self):
        if self.is_published and self.website_url:
            return self.website_url
        if self.github_name:
            return f"https://github.com/{self.github_name}"
        return False

    def _get_contributors_name(self, kind, **kwargs):
        return self.name
