# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from math import sqrt

from markupsafe import Markup

from odoo import _, http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class ContributorsController(CustomerPortal):
    @http.route(
        [
            "/contributors",
            "/contributors/<string:organization>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def contributors_organization(self, organization=None):
        values = self._prepare_portal_layout_values()
        values.update(self._prepare_home_portal_values([]))
        if organization is None:
            organizations = request.env["contributors.organization"].search([])
            return request.render(
                "contributors_github.contributors_template",
                {"organizations": organizations, **values},
            )
        organization_id = (
            request.env["contributors.organization"]
            .sudo()
            .search([("name", "=ilike", organization)], limit=1)
            .id
        )
        return request.render(
            "contributors_github.contributors_organization_template",
            {"organization": organization_id, **values},
        )

    def _get_index(self, data):
        return round(
            sqrt(data["created_pull_requests"])
            + data["merged_pull_requests"]
            + sqrt(data["comments"])
            + data["reviews"],
            2,
        )

    def _get_field(self, kind):
        if kind == "contributors":
            return "partner_id"
        elif kind == "organizations":
            return "organization_id"
        elif kind == "repositories":
            return "repository_id"
        return False

    @http.route(["/contributors/fetch"], type="json", auth="user", readonly=True)
    def fetch_data(self, organization_id, year, month, kind, period, **values):
        organization = (
            request.env["contributors.organization"].browse(organization_id).exists()
        )
        if not organization:
            return []
        start, end = organization._get_dates(year, month, period, **values)
        data = organization._generate_data(
            start, end, self._get_field(kind), kind, **values
        )
        return {
            "columns": self._get_columns(kind),
            "data": self._improve_data(data, kind, **values),
        }

    def _get_columns(self, kind):
        if kind == "contributors":
            return [
                {"field": "name", "title": _("Name"), "kind": "name"},
                {
                    "field": "index",
                    "title": _("Contributor Index"),
                    "kind": "float",
                    "decimals": 2,
                    "tooltip": Markup(
                        request.env["ir.qweb"]._render(
                            "contributors_github.contributor_index_tooltip", {}
                        )
                    ),
                },
                {
                    "field": "created_pull_requests",
                    "title": _("Created Pull Requests"),
                    "kind": "float",
                    "decimals": 0,
                },
                {
                    "field": "merged_pull_requests",
                    "title": _("Merged Pull Requests"),
                    "kind": "float",
                    "decimals": 0,
                },
                {
                    "field": "comments",
                    "title": _("Comments"),
                    "kind": "float",
                    "decimals": 0,
                },
                {
                    "field": "reviews",
                    "title": _("Reviews"),
                    "kind": "float",
                    "decimals": 0,
                },
            ]
        elif kind == "organizations":
            return [
                {"field": "name", "title": _("Organization Name"), "kind": "name"},
                {
                    "field": "created_pull_requests",
                    "title": _("Created Pull Requests"),
                    "kind": "float",
                    "decimals": 0,
                },
                {
                    "field": "merged_pull_requests",
                    "title": _("Merged Pull Requests"),
                    "kind": "float",
                    "decimals": 0,
                },
                {
                    "field": "comments",
                    "title": _("Comments"),
                    "kind": "float",
                    "decimals": 0,
                },
                {
                    "field": "reviews",
                    "title": _("Reviews"),
                    "kind": "float",
                    "decimals": 0,
                },
                {
                    "field": "developers",
                    "title": _("Developers"),
                    "kind": "float",
                    "decimals": 0,
                },
            ]
        elif kind == "repositories":
            return [
                {"field": "name", "title": _("Repository Name"), "kind": "name"},
                {
                    "field": "index",
                    "title": _("Repository Index"),
                    "kind": "float",
                    "decimals": 2,
                    "tooltip": Markup(
                        request.env["ir.qweb"]._render(
                            "contributors_github.contributor_index_tooltip", {}
                        )
                    ),
                },
                {
                    "field": "created_pull_requests",
                    "title": _("Created Pull Requests"),
                    "kind": "float",
                    "decimals": 0,
                },
                {
                    "field": "merged_pull_requests",
                    "title": _("Merged Pull Requests"),
                    "kind": "float",
                    "decimals": 0,
                },
                {
                    "field": "comments",
                    "title": _("Comments"),
                    "kind": "float",
                    "decimals": 0,
                },
                {
                    "field": "reviews",
                    "title": _("Reviews"),
                    "kind": "float",
                    "decimals": 0,
                },
                {
                    "field": "developers",
                    "title": _("Developers"),
                    "kind": "float",
                    "decimals": 0,
                },
            ]
        return []

    def _improve_data(self, data, kind, **kwargs):
        for key, values in data.items():
            if kind == "contributors":
                partner = request.env["res.partner"].browse(key)
                values["name"] = self._get_partner_name(partner, **kwargs)
                values["github_name"] = partner.github_name
                values["url"] = (partner.is_published and partner.website_url) or (
                    f"https://github.com/{partner.github_name}"
                )
                values["index"] = self._get_index(values)
            elif kind == "organizations":
                organization = request.env["res.partner"].browse(key)
                values["name"] = organization.name
                github_name = organization.github_name or organization.name
                values["github_name"] = github_name
                values["url"] = (
                    organization.is_published and organization.website_url
                ) or (f"https://github.com/{github_name}")
            elif kind == "repositories":
                repository = request.env["contributors.repository"].browse(key)
                values["name"] = repository.name
                github_name = f"{repository.organization_id.name}/{repository.name}"
                values["github_name"] = github_name
                values["url"] = f"https://github.com/{github_name}"
                values["index"] = self._get_index(values)
        return data

    def _get_partner_name(self, partner, **kwargs):
        return partner.name
