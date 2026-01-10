# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contributors Weblate",
    "summary": """Get Weblate information and integrate it in the system""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA-contributors/contributors-module",
    "depends": [
        "contributors_github",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/contributors_translation.xml",
        "views/contributors_repository.xml",
        "views/contributors_organization.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_frontend": [
            "contributors_weblate/static/src/**/*.xml",
            "contributors_weblate/static/src/**/*.esm.js",
        ],
    },
}
