# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_be_codabox_show_iap_token = fields.Boolean(related="company_id.l10n_be_codabox_show_iap_token")

    def l10n_be_codabox_refresh_connection_status(self):
        raise UserError(_("Please install the module CodaBox Bridge Wizard to use this feature (you may have to Update the Apps List first)."))

    def l10n_be_codabox_open_soda_mapping(self):
        raise UserError(_("Please install the module CodaBox Bridge Wizard to use this feature (you may have to Update the Apps List first)."))
