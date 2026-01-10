# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import logging

import github3
import requests

from odoo import fields, models

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
