# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict
from datetime import datetime
from math import sqrt

from dateutil.relativedelta import relativedelta

from odoo import http
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
            .search([("name", "=", organization)], limit=1)
            .id
        )
        return request.render(
            "contributors_github.contributors_organization_template",
            {"organization": organization_id, **values},
        )

    def _get_dates(self, year, month, period, **values):
        if month == 12:
            end = datetime(year + 1, 1, 1, 0, 0, 0)
        else:
            end = datetime(year, month + 1, 1, 0, 0, 0)
        if period == "YTD":
            start = datetime(year, 1, 1, 0, 0, 0)
        elif period == "MAT":
            start = end - relativedelta(years=1)
        else:
            start = datetime(year, month, 1, 0, 0, 0)
        return start, end

    def _get_merged_domain(self, organization, start, end, **values):
        return [
            ("repository_id.organization_id", "=", organization.id),
            ("is_merged", "=", True),
            ("closed_at", ">=", start),
            ("closed_at", "<", end),
        ]

    def _get_created_domain(self, organization, start, end, **values):
        return [
            ("repository_id.organization_id", "=", organization.id),
            ("created_at", ">=", start),
            ("created_at", "<", end),
        ]

    def _get_comments_domain(self, organization, start, end, **values):
        return [
            ("pull_request_id.repository_id.organization_id", "=", organization.id),
            ("created_at", ">=", start),
            ("created_at", "<", end),
        ]

    def _get_reviews_domain(self, organization, start, end, **values):
        return [
            ("pull_request_id.repository_id.organization_id", "=", organization.id),
            ("submitted_at", ">=", start),
            ("submitted_at", "<", end),
        ]

    def _get_index(self, data):
        return round(
            sqrt(data["created_pull_requests"])
            + data["merged_pull_requests"]
            + sqrt(data["comments"])
            + data["reviews"],
            2,
        )

    @http.route(["/contributors/fetch"], type="json", auth="user", readonly=True)
    def fetch_data(self, organization_id, year, month, kind, period, **values):
        start, end = self._get_dates(year, month, period, **values)
        organization = (
            request.env["contributors.organization"].browse(organization_id).exists()
        )
        if not organization:
            return []
        data = defaultdict(
            lambda: {
                "name": "",
                "github_name": "",
                "index": 0,
                "created_pull_requests": 0,
                "merged_pull_requests": 0,
                "comments": 0,
                "reviews": 0,
            }
        )
        if kind == "contributors":
            field = "partner_id"
        elif kind == "organizations":
            field = "organization_id"
        elif kind == "repositories":
            field = "repository_id"
        else:
            return []

        for merged in (
            request.env["contributors.pull.request"]
            .sudo()
            .read_group(
                self._get_merged_domain(organization, start, end, **values)
                + [(field, "!=", False)],
                [field],
                [field],
            )
        ):
            data[merged[field][0]]["merged_pull_requests"] = merged[f"{field}_count"]
        for pr in (
            request.env["contributors.pull.request"]
            .sudo()
            .read_group(
                self._get_created_domain(organization, start, end, **values)
                + [(field, "!=", False)],
                [field],
                [field],
            )
        ):
            data[pr[field][0]]["created_pull_requests"] = pr[f"{field}_count"]
        for comment in (
            request.env["contributors.comment"]
            .sudo()
            .read_group(
                self._get_comments_domain(organization, start, end, **values)
                + [(field, "!=", False)],
                [field],
                [field],
            )
        ):
            data[comment[field][0]]["comments"] = comment[f"{field}_count"]
        for review in (
            request.env["contributors.review"]
            .sudo()
            .read_group(
                self._get_reviews_domain(organization, start, end, **values)
                + [(field, "!=", False)],
                [field],
                [field],
            )
        ):
            data[review[field][0]]["reviews"] = review[f"{field}_count"]
        return self._improve_data(data, kind, **values)

    def _improve_data(self, data, kind, **kwargs):
        for key, values in data.items():
            if kind == "contributors":
                partner = request.env["res.partner"].browse(key)
                values["name"] = self._get_partner_name(partner, **kwargs)
                values["github_name"] = partner.github_name
                values["index"] = self._get_index(values)
            elif kind == "organizations":
                organization = request.env["res.partner"].browse(key)
                values["name"] = organization.name
                values["github_name"] = organization.github_name or organization.name
            elif kind == "repositories":
                repository = request.env["contributors.repository"].browse(key)
                values["name"] = repository.name
                values["github_name"] = (
                    f"{repository.organization_id.name}/{repository.name}"
                )
                values["index"] = self._get_index(values)
        return data

    def _get_partner_name(self, partner, **kwargs):
        return partner.name
