# Copyright (C) 2019 IBM Corp.
# Copyright (C) 2019 Open Source Integrators
# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class StockScrap(BaseCommon):
    _test_user_groups = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.categ_1 = cls.env.ref("product.product_category_goods")
        cls.categ_2 = cls.env["product.category"].create({"name": "Test category"})
        stock_location_locations_virtual = cls.env["stock.location"].create(
            {"name": "Virtual Locations", "usage": "view"}
        )
        cls.scrapped_location = cls.env["stock.location"].create(
            {
                "name": "Scrapped",
                "location_id": stock_location_locations_virtual.id,
                "usage": "inventory",
            }
        )

        cls.scrap_product = cls.env["product.product"].create(
            {
                "name": "Scrap Product A",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.categ_1.id,
            }
        )
        cls.scrap_product_2 = cls.env["product.product"].create(
            {
                "name": "Scrap Product A",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.categ_2.id,
            }
        )

        cls.reason_code = cls.env["scrap.reason.code"].create(
            {
                "name": "DM300",
                "description": "Product is damage",
                "location_id": cls.scrapped_location.id,
            }
        )
        cls.reason_code_only_categ_2 = cls.env["scrap.reason.code"].create(
            {
                "name": "Test Code 2",
                "description": "Test description",
                "product_category_ids": [(6, 0, cls.categ_2.ids)],
            }
        )

        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

    def test_scrap_reason_code(self):
        """Scrap the product of a picking. Then modify the
        done linked stock move and ensure the scrap quantity is also
        updated and verify scrap reason code
        """
        self.env["stock.quant"]._update_available_quantity(
            self.scrap_product, self.stock_location, 10
        )
        partner = self.env["res.partner"].create({"name": "BOdedra"})
        picking = self.env["stock.picking"].create(
            {
                "name": "A single picking with one move to scrap",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        move1 = self.env["stock.move"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_id": self.scrap_product.id,
                "uom_id": self.uom_unit.id,
                "product_uom_qty": 1.0,
                "picking_id": picking.id,
            }
        )
        move1._action_confirm()

        self.assertEqual(move1.state, "assigned")
        scrap = self.env["stock.move"].create(
            {
                "is_scrap": True,
                "product_id": self.scrap_product.id,
                "uom_id": self.scrap_product.uom_id.id,
                "quantity": 5,
                "location_id": self.stock_location.id,
                "picking_id": picking.id,
                "reason_code_id": self.reason_code.id,
            }
        )
        scrap._onchange_reason_code_id()
        self.assertEqual(scrap.location_dest_id, self.scrapped_location)
        scrap.action_scrap()
        all_moves = self.env["stock.move"].search([("picking_id", "=", picking.id)])
        self.assertEqual(len(all_moves), 2)
        scrapped_move = all_moves.filtered(lambda m: m.state == "done")
        self.assertTrue(scrapped_move, "No scrapped move created.")
        self.assertEqual(scrapped_move, scrap, "Wrong scrap move.")
        self.assertEqual(
            scrap.quantity,
            5,
            "Scrap quantity has been modified and is not correct anymore.",
        )
        moves = scrap
        self.assertEqual(moves.mapped("reason_code_id.id"), [self.reason_code.id])

        scrapped_move.quantity = 8
        self.assertEqual(scrap.quantity, 8, "Scrap quantity is not updated.")

    def test_scrap_reason_code_write(self):
        """Scrap the product of a picking2. Then modify the
        done linked stock move and ensure the scrap quantity is also
        updated and verify scrap reason code
        """
        self.env["stock.quant"]._update_available_quantity(
            self.scrap_product, self.stock_location, 10
        )
        partner2 = self.env["res.partner"].create({"name": "BOdedra 2"})
        picking2 = self.env["stock.picking"].create(
            {
                "name": "A single picking with one move to scrap 2",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": partner2.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        move2 = self.env["stock.move"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_id": self.scrap_product.id,
                "uom_id": self.uom_unit.id,
                "product_uom_qty": 1.0,
                "picking_id": picking2.id,
            }
        )
        move2._action_confirm()

        self.assertEqual(move2.state, "assigned")
        scrap2 = self.env["stock.move"].create(
            {
                "is_scrap": True,
                "product_id": self.scrap_product.id,
                "uom_id": self.scrap_product.uom_id.id,
                "quantity": 5,
                "location_id": self.stock_location.id,
                "picking_id": picking2.id,
            }
        )
        scrap2.write(
            {
                "reason_code_id": self.reason_code.id,
            }
        )
        self.assertEqual(scrap2.location_dest_id, self.scrapped_location)
        scrap2._onchange_reason_code_id()
        scrap2.action_scrap()
        all_moves = self.env["stock.move"].search([("picking_id", "=", picking2.id)])
        self.assertEqual(len(all_moves), 2)
        scrapped_move = all_moves.filtered(lambda m: m.state == "done")
        self.assertTrue(scrapped_move, "No scrapped move created.")
        self.assertEqual(scrapped_move, scrap2, "Wrong scrap move.")
        self.assertEqual(
            scrap2.quantity,
            5,
            "Scrap quantity has been modified and is not correct anymore.",
        )
        moves = scrap2
        self.assertEqual(moves.mapped("reason_code_id.id"), [self.reason_code.id])

        scrapped_move.quantity = 8
        self.assertEqual(scrap2.quantity, 8, "Scrap quantity is not updated.")

    def test_allowed_reason_codes(self):
        with self.assertRaises(ValidationError):
            self.env["stock.move"].create(
                {
                    "is_scrap": True,
                    "product_id": self.scrap_product.id,
                    "uom_id": self.scrap_product_2.uom_id.id,
                    "quantity": 5,
                    "reason_code_id": self.reason_code_only_categ_2.id,
                }
            )
        scrap = self.env["stock.move"].create(
            {
                "is_scrap": True,
                "product_id": self.scrap_product.id,
                "uom_id": self.scrap_product.uom_id.id,
                "quantity": 5,
                "reason_code_id": self.reason_code.id,
            }
        )
        self.assertEqual(scrap.allowed_reason_code_ids, self.reason_code)
        with self.assertRaises(ValidationError):
            scrap.write({"reason_code_id": self.reason_code_only_categ_2.id})
        scrap = self.env["stock.move"].create(
            {
                "is_scrap": True,
                "product_id": self.scrap_product_2.id,
                "uom_id": self.scrap_product_2.uom_id.id,
                "quantity": 5,
                "reason_code_id": self.reason_code_only_categ_2.id,
            }
        )
        with self.assertRaises(ValidationError):
            scrap.write({"product_id": self.scrap_product.id})
        self.assertEqual(
            scrap.allowed_reason_code_ids,
            (self.reason_code + self.reason_code_only_categ_2),
        )
        scrap.write({"reason_code_id": self.reason_code.id})
