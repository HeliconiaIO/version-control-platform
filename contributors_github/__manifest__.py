# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contributors Github",
    "summary": """Get Contributors and Contributions from Github""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA-contributors/contributors-module",
    "maintainers": ["etobella"],
    "depends": ["portal"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/contributors_comment.xml",
        "views/contributors_review.xml",
        "views/contributors_branch.xml",
        "views/contributors_pull_request.xml",
        "views/contributors_repository.xml",
        "views/contributors_organization.xml",
        "views/res_partner.xml",
        "data/ir_cron.xml",
        "templates/templates.xml",
    ],
    "external_dependencies": {"python": ["github3.py", "PyYAML"]},
    "demo": [],
    "assets": {
        "web.assets_frontend": [
            "contributors_github/static/src/components/**/*.esm.js",
            "contributors_github/static/src/components/**/*.xml",
            "contributors_github/static/src/components/**/*.scss",
        ],
        "web.assets_tests": [
            "contributors_github/static/tests/**/*",
        ],
    },
}
