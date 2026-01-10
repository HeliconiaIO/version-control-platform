# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import requests
import yaml

from odoo import fields, models


class ContributorsOrganization(models.Model):
    _inherit = "contributors.organization"

    psc_repository = fields.Char()
    psc_repository_conf = fields.Char()
    psc_ids = fields.One2many(
        "contributors.organization.psc",
        inverse_name="organization_id",
        readonly=True,
    )

    def update_information(self):
        res = super().update_information()
        if self.psc_repository:
            client = self._get_clients()[0]
            repository = client.repository(self.name, self.psc_repository)
            psc_files = repository.directory_contents(f"{self.psc_repository_conf}/psc")
            repository_files = repository.directory_contents(
                f"{self.psc_repository_conf}/repo"
            )
            for _psc_filename, psc_file in psc_files:
                req = requests.get(psc_file.download_url, timeout=10)
                req.raise_for_status()
                psc_data = yaml.safe_load(req.content)
                for psc_name in psc_data:
                    psc_record = self.env["contributors.organization.psc"].search(
                        [
                            ("organization_id", "=", self.id),
                            ("key", "=", psc_name),
                        ],
                        limit=1,
                    )
                    if not psc_record:
                        psc_record = (
                            self.env["contributors.organization.psc"]
                            .sudo()
                            .create(
                                {
                                    "organization_id": self.id,
                                    "key": psc_name,
                                    "name": psc_data[psc_name].get("name", psc_name),
                                }
                            )
                        )
                    else:
                        psc_record.sudo().write(
                            {
                                "name": psc_data[psc_name].get("name", psc_name),
                            }
                        )
                    member_logins = psc_data[psc_name].get("members", []) + psc_data[
                        psc_name
                    ].get("representatives", [])
                    members = []
                    for member in member_logins:
                        members.append(
                            self.env["res.partner"]._get_github_user(member, client)
                        )
                    psc_record.sudo().member_ids = self.env["res.partner"].browse(
                        members
                    )
            for _repo_filename, repo_file in repository_files:
                req = requests.get(repo_file.download_url, timeout=10)
                req.raise_for_status()
                repo_data = yaml.safe_load(req.content)
                for repo_name in repo_data:
                    psc_name = repo_data[repo_name].get("psc")
                    psc_record = self.env["contributors.organization.psc"].search(
                        [
                            ("organization_id", "=", self.id),
                            ("key", "=", psc_name),
                        ],
                        limit=1,
                    )
                    if not psc_record:
                        continue
                    repo_record = (
                        self.env["contributors.repository"]
                        .sudo()
                        .search(
                            [
                                ("organization_id", "=", self.id),
                                ("name", "=", repo_name),
                            ],
                            limit=1,
                        )
                    )
                    if repo_record:
                        repo_record.sudo().write(
                            {
                                "psc_id": psc_record.id,
                            }
                        )
        return res
