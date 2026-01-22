# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _
from odoo.http import request

from odoo.addons.contributors_github.controllers.main import ContributorsController


class ContributorsPSCController(ContributorsController):
    def _get_columns(self, kind):
        columns = super()._get_columns(kind)
        if kind == "translations":
            columns = [
                {"field": "name", "title": _("Name"), "kind": "name"},
            ] + columns
        if kind in ["contributors", "repositories", "translations"]:
            columns.append(
                {
                    "field": "translations",
                    "title": _("Translations"),
                    "kind": "float",
                    "decimals": 0,
                }
            )
        return columns

    def _improve_data(self, data, kind, **kwargs):
        data = super()._improve_data(data, kind, **kwargs)
        if kind == "translations":
            for key, values in data.items():
                partner = request.env["res.partner"].browse(key)
                values["name"] = self._get_partner_name(partner, **kwargs)
                values["github_name"] = partner.github_name
        return data
