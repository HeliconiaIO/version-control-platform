# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


class VcpOdooModuleVersion(models.Model):
    _name = "vcp.odoo.module.version"
    _description = "Odoo Module on an specific repository branch"
    _inherit = ["vcp.rule.information.mixin"]

    name = fields.Char(required=True)
    path = fields.Char(required=True)
    module_id = fields.Many2one(
        "vcp.odoo.module",
        required=True,
        ondelete="cascade",
    )
    version = fields.Char(required=True)
    repository_branch_id = fields.Many2one(
        "vcp.repository.branch",
    )
    depends_on_module_ids = fields.Many2many(
        "vcp.odoo.module",
    )
    auto_install = fields.Boolean()
    license = fields.Char(string="License (Manifest)", readonly=True)
    summary = fields.Char(string="Summary (Manifest)", readonly=True)
    website = fields.Char(string="Website (Manifest)", readonly=True)
    image_1920 = fields.Image(
        max_width=1920,
        max_height=1920,
        readonly=True,
        string="Image 1920x1920 (Manifest)",
    )
    image_128 = fields.Image(
        related="image_1920",
        readonly=True,
        max_width=128,
        max_height=128,
        string="Image 128x128 (Manifest)",
    )
    lib_python_ids = fields.Many2many(
        "vcp.odoo.lib.python",
        string="Python Libraries",
    )
    bin_package_ids = fields.Many2many(
        "vcp.odoo.bin.package",
        string="Python Binaries",
    )

    def _get_local_path(self):
        return f"{self.repository_branch_id.local_path}/{self.path}"


class VcpOdooLibPython(models.Model):
    _name = "vcp.odoo.lib.python"
    _description = "Python Library required by an Odoo Module"

    name = fields.Char(required=True)

    @tools.ormcache("name")
    def _get_lib_python(self, name):
        lib = self.search([("name", "=", name)], limit=1)
        if not lib:
            lib = self.create({"name": name})
        return lib.id


class VcpOdooBinPackage(models.Model):
    _name = "vcp.odoo.bin.package"
    _description = "Binary Package required by an Odoo Module"

    name = fields.Char(required=True)

    @tools.ormcache("name")
    def _get_bin(self, name):
        bin_src = self.search([("name", "=", name)], limit=1)
        if not bin_src:
            bin_src = self.create({"name": name})
        return bin_src.id
