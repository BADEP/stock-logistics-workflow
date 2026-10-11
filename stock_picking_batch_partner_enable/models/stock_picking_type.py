# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        # OVERRIDE to add important information in the help message
        res = super().fields_get(allfields, attributes)
        # In Odoo 20 the form shows batch_creation_type (same help as auto_batch)
        for fname in ("auto_batch", "batch_creation_type"):
            if fname in res and res[fname].get("help"):
                res[fname]["help"] += "\n\n" + self.env._(
                    "Note: Partners must be 'Allowed for batch grouping' for the "
                    "picking to be included in batches."
                )
        return res
