# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContributorsTranslation(models.Model):
    _name = "contributors.translation"
    _description = "Contributors Translation"  # TODO

    integration_id = fields.Char()
    unit = fields.Char()
    translation = fields.Char()
    component = fields.Char()
    partner_id = fields.Many2one("res.partner")
    organization_id = fields.Many2one("contributors.organization")
    repository_id = fields.Many2one("contributors.repository")
    branch_id = fields.Many2one("contributors.branch")
    date = fields.Datetime()
    lang_id = fields.Many2one("res.lang")
    action = fields.Selection(
        [
            ("0", "Resource updated"),
            ("1", "Translation completed"),
            ("2", "Translation changed"),
            ("3", "Comment added"),
            ("4", "Suggestion added"),
            ("5", "Translation added"),
            ("6", "Automatically translated"),
            ("7", "Suggestion accepted"),
            ("8", "Translation reverted"),
            ("9", "Translation uploaded"),
            ("13", "Source string added"),
            ("14", "Component locked"),
            ("15", "Component unlocked"),
            ("17", "Changes committed"),
            ("18", "Changes pushed"),
            ("19", "Repository reset"),
            ("20", "Repository merged"),
            ("21", "Repository rebased"),
            ("22", "Repository merge failed"),
            ("23", "Repository rebase failed"),
            ("24", "Parsing failed"),
            ("25", "Translation removed"),
            ("26", "Suggestion removed"),
            ("27", "Translation replaced"),
            ("28", "Repository push failed"),
            ("29", "Suggestion removed during cleanup"),
            ("30", "Source string changed"),
            ("31", "String added"),
            ("32", "Bulk status changed"),
            ("33", "Visibility changed"),
            ("34", "User added"),
            ("35", "User removed"),
            ("36", "Translation approved"),
            ("37", "Marked for edit"),
            ("38", "Component removed"),
            ("39", "Project removed"),
            ("41", "Project renamed"),
            ("42", "Component renamed"),
            ("43", "Moved component"),
            ("45", "Contributor joined"),
            ("46", "Announcement posted"),
            ("47", "Alert triggered"),
            ("48", "Language added"),
            ("49", "Language requested"),
            ("50", "Project created"),
            ("51", "Component created"),
            ("52", "User invited"),
            ("53", "Repository notification received"),
            ("54", "Translation replaced file by upload"),
            ("55", "License changed"),
            ("56", "Contributor license agreement changed"),
            ("57", "Screenshot added"),
            ("58", "Screenshot uploaded"),
            ("59", "String updated in the repository"),
            ("60", "Add-on installed"),
            ("61", "Add-on configuration changed"),
            ("62", "Add-on uninstalled"),
            ("63", "String removed"),
            ("64", "Comment removed"),
            ("65", "Comment resolved"),
            ("66", "Explanation updated"),
            ("67", "Category removed"),
            ("68", "Category renamed"),
            ("69", "Category moved"),
            ("70", "Saving string failed"),
            ("71", "String added in the repository"),
            ("72", "String updated in the upload"),
            ("73", "String added in the upload"),
            ("74", "Translation updated by source upload"),
            ("75", "Component translation completed"),
            ("76", "Applied enforced check"),
            ("77", "Propagated change"),
            ("78", "File uploaded"),
            ("79", "Extra flags updated"),
        ]
    )
    details = fields.Json()
