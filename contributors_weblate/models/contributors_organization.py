# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import re
from datetime import timedelta

import requests

from odoo import _, fields, models, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ContributorsOrganization(models.Model):
    _inherit = "contributors.organization"

    weblate_url = fields.Char()
    weblate_auth_token = fields.Char()
    weblate_last_update = fields.Datetime()
    weblate_load_delay = fields.Integer(
        help="Number of days to load each time", default=7
    )

    def get_weblate_data(self):
        self.ensure_one()
        if not self.weblate_last_update:
            raise ValidationError(
                _("Please set the last update date for Weblate data.")
            )
        auth = {}
        if self.weblate_auth_token:
            auth = {"Authorization": f"Token {self.weblate_auth_token}"}
        before_date = min(
            self.weblate_last_update + timedelta(days=self.weblate_load_delay),
            fields.Datetime.now(),
        )
        req = requests.get(
            f"{self.weblate_url}/api/changes/",
            params={
                "timestamp_after": (
                    self.weblate_last_update + timedelta(days=-1)
                ).isoformat(),
                "timestamp_before": before_date.isoformat(),
                "format": "json",
            },
            timeout=10,
            headers=auth,
        )
        # self.weblate_last_update = before_date
        total = 0
        client = self._get_clients()[0]
        while True:
            results = req.json().get("results", [])
            max_total = req.json().get("count", 0)
            for result in results:
                translation = self.env["contributors.translation"].search(
                    [("integration_id", "=", str(result["id"]))]
                )
                partner = False
                if result["user"]:
                    splitted = result["user"].split("/")
                    if len(splitted) >= 2:
                        partner = self.env["res.partner"]._get_github_user(
                            splitted[-2], client
                        )
                vals = {
                    "integration_id": result["id"],
                    "unit": result["unit"],
                    "translation": result["translation"],
                    "component": result["component"],
                    "organization_id": self.id,
                    "partner_id": partner,
                    "date": self.env["contributors.repository"]._parse_date(
                        result["timestamp"]
                    ),
                    "action": str(result["action"]),
                    "repository_id": self._get_repository(result["component"]),
                    "branch_id": self._get_weblate_branch(result["component"]),
                    "lang_id": self._get_lang(result["translation"]),
                }
                if not translation:
                    translation = (
                        self.env["contributors.translation"].sudo().create(vals)
                    )
                else:
                    translation.sudo().write(vals)
                total += 1
                if total % 100 == 0:
                    _logger.debug(
                        f"Processed {total} of {max_total} Weblate translation changes"
                    )
            if req.json().get("next"):
                req = requests.get(req.json().get("next"), timeout=10, headers=auth)
            else:
                break
        self.weblate_last_update = before_date
        _logger.info(f"Processed a total of {total} Weblate translation changes")

    @tools.ormcache("self.id", "translation")
    def _get_lang(self, translation):
        if not translation:
            return False
        parts = translation.split("/")
        lang = (
            self.env["res.lang"]
            .search(
                [("iso_code", "=", parts[-2]), ("active", "in", [True, False])], limit=1
            )
            .id
        )
        if lang:
            return lang
        if len(parts[-2]) == 2:
            lang = (
                self.env["res.lang"]
                .search(
                    [
                        ("iso_code", "=ilike", parts[-2] + "_%"),
                        ("active", "in", [True, False]),
                    ],
                    limit=1,
                )
                .id
            )
            if lang:
                return lang
        return (
            self.env["res.lang"]
            .search(
                [("code", "=", parts[-2]), ("active", "in", [True, False])], limit=1
            )
            .id
        )

    @tools.ormcache("self.id", "component")
    def _get_weblate_branch(self, component):
        if not component:
            return False
        parts = component.split("/")
        if len(parts) < 3:
            return False
        found = re.match(r"^[\w-]+-(\d+-\d)$", parts[-3])
        if not found:
            return False
        return self._get_branch(found.group(1))

    @tools.ormcache("self.id", "component")
    def _get_repository(self, component):
        if not component:
            return False
        parts = component.split("/")
        if len(parts) < 3:
            return False
        found = re.match(r"^([\w-]+)-\d+-\d$", parts[-3])
        if not found:
            return False
        return (
            self.env["contributors.repository"]
            .search(
                [("name", "=", found.group(1)), ("organization_id", "=", self.id)],
                limit=1,
            )
            .id
        )

    def _cron_weblate_data(self):
        organizations = self.search([("weblate_url", "!=", False)])
        for organization in organizations:
            try:
                organization.get_weblate_data()
            except Exception as e:
                _logger.error(
                    "Error while updating Weblate data for organization "
                    f"{organization.name}: {e}"
                )
