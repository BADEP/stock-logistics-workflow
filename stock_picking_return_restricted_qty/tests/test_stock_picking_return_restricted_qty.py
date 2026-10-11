# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import Command

from odoo.addons.base.tests.common import BaseCommon


class StockPickingReturnRestrictedQtyTest(BaseCommon):
    _test_user_groups = ("stock.group_stock_manager",)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        product = cls.env["product.product"].create(
            {"name": "test_product", "is_storable": True, "type": "consu"}
        )
        picking_type_out = cls.env.ref("stock.picking_type_out")
        stock_location = cls.env.ref("stock.stock_location_stock")
        customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": picking_type_out.id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "reference": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 20,
                            "uom_id": product.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        }
                    )
                ],
            }
        )
        cls.picking.action_confirm()
        cls.picking.action_assign()
        cls.picking.move_ids[:1].quantity = 20
        cls.picking.button_validate()

    def _process_return(self, return_picking):
        return_picking.action_confirm()
        return_picking.action_assign()

    def test_return_not_allowed(self):
        """On this test we create a return picking with more quantity
        than the quantity that client have on his hand"""
        self.picking.picking_type_id.restrict_return_qty = True
        return_picking = self.picking._create_return()
        self.assertEqual(return_picking.move_ids.product_uom_qty, 20)
        with self.assertRaises(UserError):
            return_picking.move_ids.product_uom_qty = 30

    def test_return_without_restriction(self):
        """On this test we create a return picking with more quantity
        than the quantity that client have on his hand
        without the quantity restriction"""
        self.picking.picking_type_id.restrict_return_qty = False
        return_picking = self.picking._create_return()
        self.assertEqual(return_picking.move_ids.product_uom_qty, 20)
        return_picking.move_ids.product_uom_qty = 30
        self._process_return(return_picking)
        self.assertEqual(return_picking.move_ids.product_uom_qty, 30)

    def test_multiple_return(self):
        """On this test we are going to follow a sequence that a client
        can follow if he tries to return a product"""
        self.picking.picking_type_id.restrict_return_qty = True
        picking_returned = self.picking._create_return()
        picking_returned.move_ids.product_uom_qty = 10
        self._process_return(picking_returned)
        return_picking = self.picking._create_return()
        self.assertEqual(return_picking.move_ids.product_uom_qty, 10)
        # Creating a new return unreserves the pending ones: drop it and
        # reserve the first return again
        return_picking.action_cancel()
        picking_returned.action_assign()
        picking_returned.move_ids.picked = True
        picking_returned._action_done()
        return_picking = self.picking._create_return()
        self.assertEqual(return_picking.move_ids.product_uom_qty, 10)

        with self.assertRaises(UserError):
            return_picking.move_ids.product_uom_qty = 80

    def test_multiple_return_without_restriction(self):
        """On this test we are going to follow a sequence that a client
        can follow if he tries to return a product
        without the quantity restriction"""
        self.picking.picking_type_id.restrict_return_qty = False
        picking_returned = self.picking._create_return()
        picking_returned.move_ids.product_uom_qty = 10
        self._process_return(picking_returned)
        return_picking = self.picking._create_return()
        self.assertEqual(return_picking.move_ids.product_uom_qty, 10)

        return_picking.action_cancel()
        picking_returned.action_assign()
        picking_returned.move_ids.picked = True
        picking_returned._action_done()
        return_picking = self.picking._create_return()
        self.assertEqual(return_picking.move_ids.product_uom_qty, 10)

        return_picking.move_ids.product_uom_qty = 80
        self.assertEqual(return_picking.move_ids.product_uom_qty, 80)
