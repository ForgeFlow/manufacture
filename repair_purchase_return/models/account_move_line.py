from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_computed_account(self):
        account = super(AccountMoveLine, self)._get_computed_account()
        if self.purchase_return_line_id.repair_line_ids:
            loc = self.purchase_return_line_id.repair_line_ids[0].location_dest_id
            acc = loc.valuation_in_account_id
            if acc:
                return acc
        return account
