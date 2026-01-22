# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import logging
from collections import defaultdict
from datetime import datetime
from math import sqrt

import github3
import requests
from dateutil.relativedelta import relativedelta

from odoo import fields, models, tools

_logger = logging.getLogger(__name__)


class ContributorsOrganization(models.Model):
    _name = "contributors.organization"
    _description = "Contributors Organization"  # TODO

    name = fields.Char(required=True)
    description = fields.Char(readonly=True)
    short_description = fields.Char(readonly=True)
    branch_ids = fields.One2many(
        comodel_name="contributors.branch",
        inverse_name="organization_id",
        string="Branches",
        readonly=True,
    )
    repository_ids = fields.One2many(
        comodel_name="contributors.repository",
        inverse_name="organization_id",
        string="Repositories",
        readonly=True,
    )
    key_ids = fields.One2many(
        comodel_name="contributors.organization.key",
        inverse_name="organization_id",
        string="API Keys",
    )
    last_update = fields.Datetime(readonly=True)
    active = fields.Boolean(default=True)
    update_interval_days = fields.Integer(default=3)
    image_1920 = fields.Image()
    image_128 = fields.Image(
        max_width=128,
        max_height=128,
        store=True,
        related="image_1920",
        string="Image 128",
    )
    image_64 = fields.Image(
        max_width=64, max_height=64, store=True, related="image_1920", string="Image 64"
    )

    def _get_clients(self):
        git = []
        for key in self.key_ids:
            git.append(github3.login(token=key.name))
        return git

    def update_information(self):
        self.ensure_one()
        clients = self._get_clients()
        org = clients[0].organization(self.name)
        self.short_description = org.name
        self.description = org.description
        if org.avatar_url:
            response = requests.get(org.avatar_url, timeout=10)
            response.raise_for_status()
            self.image_1920 = base64.b64encode(response.content)
        repos = org.repositories()
        for repo in repos:
            self.env["contributors.repository"]._update_repository(repo, self)
        self.last_update = fields.Datetime.now()

    def _cron_update_organizations(self):
        for organization in self.search([("key_ids", "!=", False)]):
            try:
                organization.update_information()
            except Exception as e:
                _logger.error(
                    "Error updating organization %s: %s", organization.name, str(e)
                )

    @tools.ormcache("self.id", "name")
    def _get_branch(self, name):
        branch = self.env["contributors.branch"].search(
            [("organization_id", "=", self.id), ("name", "=", name)],
            limit=1,
        )
        if not branch:
            branch = (
                self.env["contributors.branch"]
                .sudo()
                .create(
                    {
                        "organization_id": self.id,
                        "name": name,
                    }
                )
            )
        return branch.id

    def _get_merged_domain(self, start, end, **values):
        return [
            ("repository_id.organization_id", "in", self.ids),
            ("is_merged", "=", True),
            ("closed_at", ">=", start),
            ("closed_at", "<", end),
        ]

    def _get_created_domain(self, start, end, **values):
        return [
            ("repository_id.organization_id", "in", self.ids),
            ("created_at", ">=", start),
            ("created_at", "<", end),
        ]

    def _get_comments_domain(self, start, end, **values):
        return [
            ("pull_request_id.repository_id.organization_id", "in", self.ids),
            ("created_at", ">=", start),
            ("created_at", "<", end),
        ]

    def _get_reviews_domain(self, start, end, **values):
        return [
            ("pull_request_id.repository_id.organization_id", "in", self.ids),
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

    def _get_default_data(self, start, end, field, kind, **values):
        return {
            "name": "",
            "github_name": "",
            "index": 0,
            "created_pull_requests": 0,
            "merged_pull_requests": 0,
            "comments": 0,
            "reviews": 0,
            "developers": 0,
        }

    def _generate_data(self, start, end, field, kind, extra_domain=None, **values):
        if extra_domain is None:
            extra_domain = []
        default_dict = self._get_default_data(start, end, field, kind, **values)
        data = defaultdict(lambda: default_dict.copy())
        if not field:
            return data
        for merged in (
            self.env["contributors.pull.request"]
            .sudo()
            .read_group(
                self._get_merged_domain(start, end, **values)
                + extra_domain
                + [(field, "!=", False)],
                [field],
                [field],
            )
        ):
            data[merged[field][0]]["merged_pull_requests"] = merged[f"{field}_count"]
        for pr in (
            self.env["contributors.pull.request"]
            .sudo()
            .read_group(
                self._get_created_domain(start, end, **values)
                + extra_domain
                + [(field, "!=", False)],
                [field, "partner_id:count_distinct"]
                if field != "partner_id"
                else [field],
                [field],
            )
        ):
            data[pr[field][0]]["created_pull_requests"] = pr[f"{field}_count"]
            if field != "partner_id":
                data[pr[field][0]]["developers"] = pr["partner_id"]
        for comment in (
            self.env["contributors.comment"]
            .sudo()
            .read_group(
                self._get_comments_domain(start, end, **values)
                + extra_domain
                + [(field, "!=", False)],
                [field],
                [field],
            )
        ):
            data[comment[field][0]]["comments"] = comment[f"{field}_count"]
        for review in (
            self.env["contributors.review"]
            .sudo()
            .read_group(
                self._get_reviews_domain(start, end, **values)
                + extra_domain
                + [(field, "!=", False)],
                [field],
                [field],
            )
        ):
            data[review[field][0]]["reviews"] = review[f"{field}_count"]
        return data

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


class ContributorsOrganizationKey(models.Model):
    _name = "contributors.organization.key"
    _description = "Contributors Organization API Key"  # TODO

    organization_id = fields.Many2one(
        comodel_name="contributors.organization",
        string="Organization",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(required=True)

    _sql_constraints = [
        ("name_uniq", "unique(name, organization_id)", "API Key must be unique.")
    ]
