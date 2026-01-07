# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contributors Github Psc",
    "summary": """Integrate PSCs""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA-contributors/contributors-module",
    "depends": ["contributors_github"],
    "data": [
        "views/contributors_repository.xml",
        "security/ir.model.access.csv",
        "views/contributors_organization_psc.xml",
        "views/contributors_organization.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "contributors_github_psc/static/src/components/**/*.esm.js",
            "contributors_github_psc/static/src/components/**/*.xml",
            "contributors_github_psc/static/src/components/**/*.scss",
        ],
    },
    "demo": [],
}
