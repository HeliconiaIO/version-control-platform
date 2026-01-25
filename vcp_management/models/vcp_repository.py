# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VcpRepository(models.Model):
    """
    Repository of code
    """

    _name = "vcp.repository"
    _description = "Repository"

    name = fields.Char(required=True, index=True)
    description = fields.Char(readonly=True)
    platform_id = fields.Many2one(
        comodel_name="vcp.platform",
        required=True,
    )
    created_at = fields.Datetime(readonly=True)
    stargazers_count = fields.Integer(readonly=True)
    fork_count = fields.Integer(readonly=True)
    watchers_count = fields.Integer(readonly=True)
    from_date = fields.Datetime(readonly=True, required=True)
    request_ids = fields.One2many("vcp.request", inverse_name="repository_id")
    request_count = fields.Integer(compute="_compute_request_count")
    test_field = fields.Char()  # TODO remove after testing
    active = fields.Boolean(default=True)
    information_update = fields.Boolean(
        compute="_compute_information_update",
        store=True,
        readonly=False,
    )
    branch_update = fields.Boolean(default=False)
    branch_update_date = fields.Datetime(
        readonly=True, required=True, default=fields.Datetime.now
    )
    local_path = fields.Char(compute="_compute_local_path")
    rule_ids = fields.Many2many(
        "vcp.rule",
        string="Processing Rules",
    )
    override_parent_rules = fields.Boolean()
    branch_ids = fields.One2many(
        "vcp.repository.branch",
        inverse_name="repository_id",
    )

    def _get_rules(self):
        rules = self.rule_ids
        if not self.override_parent_rules:
            rules |= self.platform_id.rule_ids
        return rules

    @api.depends("platform_id.local_path", "name")
    def _compute_local_path(self):
        for record in self:
            record.local_path = f"{record.platform_id.local_path}/{record.name}"

    def _get_git_url(self):
        self.ensure_one()
        return self.platform_id._get_git_url(self)

    @api.depends("platform_id")
    def _compute_information_update(self):
        for record in self:
            record.information_update = (
                record.platform_id.default_update_repository_information
            )

    @api.depends("request_ids")
    def _compute_request_count(self):
        for record in self:
            record.request_count = len(record.request_ids)

    def update_branches(self):
        self.ensure_one()
        now = fields.Datetime.now()
        getattr(self, f"_update_branches_{self.platform_id.kind}")()
        self.branch_update_date = now

    def force_update_information(self):
        self.update_information(update_interval_days=365)

    def update_information(self, update_interval_days=None):
        self.ensure_one()
        getattr(self, f"_update_information_{self.platform_id.kind}")(
            update_interval_days=update_interval_days
        )

    def _cron_update_repositories(self, limit=1):
        repositories = self.search(
            [("information_update", "=", True)], limit=limit, order="from_date ASC"
        )
        for repository in repositories:
            repository.update_information()

    def _cron_update_branches(self, limit=1):
        repositories = self.search(
            [("branch_update", "=", True)], limit=limit, order="branch_update_date ASC"
        )
        for repository in repositories:
            repository.update_branches()

    def _get_repository_url(self):
        self.ensure_one()
        return False
