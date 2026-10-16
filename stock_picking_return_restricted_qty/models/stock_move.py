# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def get_returned_restricted_quantity(self, exclude_moves=None):
        """This function is created to know how many products
        have the person who tries to create a return picking
        on his hand."""
        self.ensure_one()
        qty = self.product_qty
        for line in self.move_dest_ids.move_line_ids:
            if exclude_moves and line.move_id in exclude_moves:
                continue
            if (
                line.move_id.origin_returned_move_id
                and line.move_id.origin_returned_move_id != self
            ):
                continue
            if line.state in {"partially_available", "assigned", "done"}:
                qty -= line.quantity
        return max(qty, 0.0)

    @api.constrains("product_uom_qty")
    def _check_returned_restricted_quantity(self):
        for move in self:
            origin_move = move.origin_returned_move_id
            if (
                not origin_move
                or move.state in ("done", "cancel")
                or not origin_move.picking_id.picking_type_id.restrict_return_qty
            ):
                continue
            qty = origin_move.get_returned_restricted_quantity(exclude_moves=move)
            if move.product_uom_qty > qty:
                raise UserError(
                    self.env._("Return more quantities than delivered is not allowed.")
                )
