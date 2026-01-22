# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.contributors_github.controllers.main import ContributorsController


class ContributorsPSCController(ContributorsController):
    def _get_partner_name(self, partner, psc_id=None, **kwargs):
        result = super()._get_partner_name(partner, **kwargs)
        if psc_id:
            if psc_id in partner.psc_ids.ids:
                result += " ★"
        return result
