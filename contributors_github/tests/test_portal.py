# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo.fields import Date
from odoo.tests import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserDemo, HttpCaseWithUserPortal


@tagged("post_install", "-at_install")
class TestUi(HttpCaseWithUserDemo, HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # be sure some expected values are set otherwise homepage may fail
        date = Date.today()
        date = date - timedelta(days=date.day)
        cls.partner_portal.write(
            {
                "city": "Bayonne",
                "company_name": "YourCompany",
                "country_id": cls.env.ref("base.us").id,
                "phone": "(683)-556-5104",
                "street": "858 Lynn Street",
                "zip": "07002",
            }
        )
        organization = cls.env["contributors.organization"].create(
            {
                "name": "oca",
                "short_description": "OCA",
                "description": "OCA",
            }
        )
        repository = cls.env["contributors.repository"].create(
            {
                "name": "contributors-module",
                "description": "OCA/contributors-module",
                "organization_id": organization.id,
                "from_date": date,
            }
        )
        user_01 = cls.env["res.partner"].create(
            {
                "name": "Enric Tobella",
                "github_name": "etobella",
                "github_user": True,
            }
        )
        user_02 = cls.env["res.partner"].create(
            {
                "name": "Luis Rodriguez",
                "github_name": "luisDixmit",
                "github_user": True,
            }
        )
        user_03 = cls.env["res.partner"].create(
            {
                "name": "Jordi Ballester",
                "github_name": "JordiBForgeFlow",
                "github_user": True,
            }
        )
        org_01 = cls.env["res.partner"].create(
            {
                "name": "Dixmit",
                "github_name": "dixmit",
                "github_organization": True,
            }
        )
        org_02 = cls.env["res.partner"].create(
            {
                "name": "ForgeFlow",
                "github_name": "ForgeFlow",
                "github_organization": True,
            }
        )
        pull_request_01 = cls.env["contributors.pull.request"].create(
            {
                "github_id": 1,
                "name": "Test PR",
                "repository_id": repository.id,
                "partner_id": user_01.id,
                "organization_id": org_01.id,
                "created_at": date,
                "closed_at": date,
                "is_merged": True,
            }
        )
        cls.env["contributors.pull.request"].create(
            {
                "github_id": 2,
                "name": "Test PR",
                "repository_id": repository.id,
                "partner_id": user_02.id,
                "organization_id": org_01.id,
                "created_at": date,
                "is_merged": False,
            }
        )
        cls.env["contributors.pull.request"].create(
            {
                "github_id": 3,
                "name": "Test PR",
                "repository_id": repository.id,
                "partner_id": user_03.id,
                "organization_id": org_02.id,
                "created_at": date,
                "is_merged": False,
            }
        )
        cls.env["contributors.review"].create(
            {
                "github_id": 1,
                "body": "Test Review",
                "state": "APPROVED",
                "pull_request_id": pull_request_01.id,
                "partner_id": user_01.id,
                "submitted_at": date,
            }
        )
        cls.env["contributors.comment"].create(
            {
                "github_id": 1,
                "body": "Test Comment",
                "pull_request_id": pull_request_01.id,
                "partner_id": user_01.id,
                "created_at": date,
            }
        )

    def test_01_portal_load_tour(self):
        self.start_tour("/", "portal_load_contributors_github", login="portal")
