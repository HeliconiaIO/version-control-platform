# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserDemo, HttpCaseWithUserPortal


@tagged("post_install", "-at_install")
class TestUi(HttpCaseWithUserDemo, HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # be sure some expected values are set otherwise homepage may fail
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
        cls.env["contributors.organization"].create(
            {
                "name": "oca",
                "short_description": "OCA",
                "description": "OCA",
            }
        )

    def test_01_portal_load_tour(self):
        self.start_tour("/", "portal_load_contributors_github", login="portal")
