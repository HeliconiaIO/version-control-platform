# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import os
import re

import git

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VcpRepositoryBranch(models.Model):
    _name = "vcp.repository.branch"
    _description = "Links Branches with Repositories"

    branch_id = fields.Many2one(
        "vcp.branch",
        string="Branch",
        required=True,
    )
    repository_id = fields.Many2one(
        "vcp.repository",
        required=True,
    )
    platform_id = fields.Many2one(
        related="repository_id.platform_id",
        readonly=True,
    )
    last_commit = fields.Char(readonly=True)
    local_path = fields.Char(compute="_compute_local_path")
    rule_ids = fields.Many2many(
        "vcp.rule",
        string="Processing Rules",
    )
    override_parent_rules = fields.Boolean()
    rule_information_ids = fields.One2many(
        "vcp.repository.branch.rule.information",
        inverse_name="repository_branch_id",
    )
    update_rule_processing_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
    )

    def _cron_process_branch_rules(self, limit=10):
        branches = self.search([], limit=limit, order="update_rule_processing_date asc")
        for branch in branches:
            branch.process_rules()

    @api.constrains("branch_id", "repository_id")
    def _check_branch_repository(self):
        for record in self:
            if record.branch_id.platform_id != record.repository_id.platform_id:
                raise ValidationError(
                    _("The branch and the repository must belong to the same platform.")
                )

    def _get_rules(self):
        rules = self.rule_ids
        if not self.override_parent_rules:
            rules |= self.repository_id._get_rules()
        return rules

    @api.depends("repository_id.local_path", "branch_id.name")
    def _compute_local_path(self):
        for record in self:
            record.local_path = (
                f"{record.repository_id.local_path}/{record.branch_id.name}"
            )

    def process_rules(self):
        for record in self:
            rules = record._get_rules()
            for rule in rules:
                if re.match(rule.branch_pattern, record.branch_id.name):
                    rule._process_rule(record)

    def _download_code(self):
        self.ensure_one()
        local_path = self.local_path
        try:
            os.makedirs(local_path, exist_ok=True)
        except PermissionError as err:
            raise ValidationError(
                _(
                    "Unable to create a folder in '%(local_path)s'.",
                    local_path=local_path,
                )
            ) from err

        try:
            repo = git.Repo(local_path)
            for remote in repo.remotes:
                if remote.url == self.repository_id._get_git_url():
                    remote.fetch(self.branch_id.name)
                    repo.git.reset("--hard", f"{remote.name}/{self.branch_id.name}")
                    break
        except git.exc.InvalidGitRepositoryError:
            # Not cloned yet
            repo = git.Repo.clone_from(
                self.repository_id._get_git_url(),
                local_path,
                branch=self.branch_id.name,
                depth=1,
            )


class VcpRepositoryBranchRuleInformation(models.Model):
    _name = "vcp.repository.branch.rule.information"
    _description = "Information about the processing of a rule on a repository branch"

    repository_branch_id = fields.Many2one(
        "vcp.repository.branch",
        required=True,
    )
    rule_id = fields.Many2one(
        "vcp.rule",
        required=True,
    )
    code_count = fields.Integer()
    documentation_count = fields.Integer()
    empty_count = fields.Integer()
    total_count = fields.Integer(store=True, compute="_compute_total_count")
    scanned_files = fields.Integer()

    @api.depends("code_count", "documentation_count", "empty_count")
    def _compute_total_count(self):
        for item in self:
            item.total_count = (
                item.code_count + item.documentation_count + item.empty_count
            )
