# Copyright 2024 ACSONE SA/NV
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _check_entire_pack(self):
        res = super()._check_entire_pack()
        # The return wizard is gone: return pickings are reserved like any
        # other transfer and get the returned package as destination package
        # when the entire package is moved back. Only put back the content.
        returns = self.filtered(
            lambda p: p.return_id.picking_type_id.empty_package_at_return
        )
        returns.move_line_ids.filtered(
            lambda ml: (
                ml.state not in ("done", "cancel")
                and ml.result_package_id
                and ml.result_package_id == ml.package_id
            )
        ).result_package_id = False
        return res
