# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import github3

from odoo import fields, models


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

    _sql_constraints = [
        (
            "github_name_uniq",
            "unique(github_name)",
            "The GitHub username must be unique across partners.",
        ),
    ]

    def _get_github_user(self, gh, client):
        if not gh:
            return False
        partner = self.with_context(active_test=False).search(
            [("github_name", "=ilike", str(gh))], limit=1
        )
        if not partner:
            if isinstance(gh, str):
                gh = client.user(str(gh))
            return self.create(
                {
                    "name": getattr(gh, "name", None) or str(gh),
                    "github_name": str(gh),
                    "github_user": True,
                }
            ).id
        if not partner.github_user:
            partner.github_user = True
        return partner.id

    def _get_github_organization(self, gh, client):
        if not gh:
            return False
        partner = self.with_context(active_test=False).search(
            [("github_name", "=ilike", str(gh))], limit=1
        )
        if not partner:
            try:
                org = client.organization(str(gh))
                if org:
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
        if not partner.github_organization:
            partner.github_organization = True
        return partner.id
