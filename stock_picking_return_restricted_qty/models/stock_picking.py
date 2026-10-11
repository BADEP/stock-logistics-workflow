# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _create_return(self):
        # Compute the quantities still on the customer's hands before core
        # unreserves the pending returns of the same moves.
        restricted_qties = {
            move.id: move.get_returned_restricted_quantity()
            for move in self.move_ids.filtered(lambda m: m.state != "cancel")
        }
        return super(
            StockPicking,
            self.with_context(return_restricted_qties=restricted_qties),
        )._create_return()

    def _prepare_return_move_default_values(self, move_id):
        vals = super()._prepare_return_move_default_values(move_id)
        restricted_qties = self.env.context.get("return_restricted_qties")
        # Only on regular returns, where core proposes a zero demand
        # (exchanges keep the returned quantity).
        if self.show_return:
            if restricted_qties and move_id.id in restricted_qties:
                vals["product_uom_qty"] = restricted_qties[move_id.id]
            else:
                vals["product_uom_qty"] = move_id.get_returned_restricted_quantity()
        return vals
