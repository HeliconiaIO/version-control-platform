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

    def _get_default_data(self, organization, start, end, field, kind, **values):
        data = super()._get_default_data(
            organization, start, end, field, kind, **values
        )
        data["translations"] = 0
        return data

    def _get_translation_domain(
        self,
        organization,
        start,
        end,
        psc_id=None,
        lang_id=None,
        actions=None,
        **values,
    ):
        if actions is None:
            actions = request.env["contributors.organization"]._translation_actions()
        domain = [
            ("organization_id", "=", organization.id),
            ("date", ">=", start),
            ("date", "<", end),
            ("action", "in", actions),
        ]
        if lang_id:
            domain.append(("lang_id", "=", lang_id))
        if psc_id and "psc_id" in request.env["contributors.repository"]._fields:
            # To avoid an extra module we add the psc_id filter here
            domain.append(("repository_id.psc_id", "=", int(psc_id)))
        return domain

    def _improve_data(self, data, kind, **kwargs):
        data = super()._improve_data(data, kind, **kwargs)
        if kind == "translations":
            for key, values in data.items():
                partner = request.env["res.partner"].browse(key)
                values["name"] = self._get_partner_name(partner, **kwargs)
                values["github_name"] = partner.github_name
        return data

    def _generate_data(
        self, organization, start, end, field, kind, lang_id=None, **values
    ):
        data = super()._generate_data(organization, start, end, field, kind, **values)
        if kind == "translations" and not field:
            field = "partner_id"
        if (
            kind in ["contributors", "repositories", "translations"]
            and organization.weblate_url
        ):
            for merged in (
                request.env["contributors.translation"]
                .sudo()
                .read_group(
                    self._get_translation_domain(
                        organization,
                        start,
                        end,
                        lang_id=lang_id if kind == "translations" else None,
                        **values,
                    )
                    + [(field, "!=", False)],
                    [field],
                    [field],
                )
            ):
                data[merged[field][0]]["translations"] = merged[f"{field}_count"]
        return data
