# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.contributors_github.controllers.main import ContributorsController


class ContributorsPSCController(ContributorsController):
    def _get_merged_domain(self, organization, start, end, psc_id=None, **values):
        result = super()._get_merged_domain(
            organization, start, end, psc_id=psc_id, **values
        )
        if psc_id:
            result.append(("repository_id.psc_id", "=", int(psc_id)))
        return result

    def _get_created_domain(self, organization, start, end, psc_id=None, **values):
        result = super()._get_created_domain(
            organization, start, end, psc_id=psc_id, **values
        )
        if psc_id:
            result.append(("repository_id.psc_id", "=", int(psc_id)))
        return result

    def _get_comments_domain(self, organization, start, end, psc_id=None, **values):
        result = super()._get_comments_domain(
            organization, start, end, psc_id=psc_id, **values
        )
        if psc_id:
            result.append(("repository_id.psc_id", "=", int(psc_id)))
        return result

    def _get_reviews_domain(self, organization, start, end, psc_id=None, **values):
        result = super()._get_reviews_domain(
            organization, start, end, psc_id=psc_id, **values
        )
        if psc_id:
            result.append(("repository_id.psc_id", "=", int(psc_id)))
        return result

    def _get_partner_name(self, partner, psc_id=None, **kwargs):
        result = super()._get_partner_name(partner, **kwargs)
        if psc_id:
            if psc_id in partner.psc_ids.ids:
                result += " ★"
        return result
