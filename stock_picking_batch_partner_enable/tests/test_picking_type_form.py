# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, TransactionCase


class TestPickingTypeForm(TransactionCase):
    def test_picking_type_form_help_message(self):
        # Odoo 20: batch options are only shown to batch transfer users, and the
        # form displays batch_creation_type instead of auto_batch
        self.env.user.write(
            {
                "group_ids": [
                    Command.link(self.env.ref("stock.group_stock_picking_batch").id)
                ]
            }
        )
        form = Form(self.env["stock.picking.type"])
        self.assertIn(
            "Note: Partners must be 'Allowed for batch grouping'",
            form._view["fields"].get("batch_creation_type").get("help"),
            "The help message should contain the note about the partner setting",
        )
