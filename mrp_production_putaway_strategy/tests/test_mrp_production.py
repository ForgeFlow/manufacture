# Copyright 2017-18 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class MrpProductionCase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "X Warehouse",
                "code": "X WH",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
            }
        )

        cls.category = cls.env["product.category"].create({"name": "Test"})

        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.bin_loc_stock = cls.env["stock.location"].create(
            {"name": "Bin 1", "location_id": cls.loc_stock.id, "usage": "internal"}
        )

        cls.product1 = cls.env["product.product"].create(
            {"name": "Test Desk", "is_storable": True, "categ_id": cls.category.id}
        )
        cls.component1 = cls.env["product.product"].create(
            {"name": "Test Component", "is_storable": True}
        )
        cls.bom1 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product1.product_tmpl_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.component1.id, "product_qty": 1.0})
                ],
            }
        )

        cls.putaway_strategy = cls.env["stock.putaway.rule"].create(
            {
                "product_id": cls.product1.id,
                "location_in_id": cls.loc_stock.id,
                "location_out_id": cls.bin_loc_stock.id,
            }
        )
        cls.loc_stock.putaway_rule_ids = cls.putaway_strategy

    def _create_mo(
        self,
        product=False,
        bom=False,
        src_loc=False,
        dest_loc=False,
        qty=10.0,
        uom=False,
    ):
        if not product:
            product = self.product1
        uom = product.uom_id or uom
        if not bom:
            bom = self.bom1
        if not src_loc:
            src_loc = self.loc_stock
        if not dest_loc:
            dest_loc = self.loc_stock
        res = {
            "product_id": product.id,
            "bom_id": bom.id,
            "location_src_id": src_loc.id,
            "location_dest_id": dest_loc.id,
            "product_qty": qty,
            "product_uom_id": uom.id,
        }
        return self.env["mrp.production"].create(res)

    def test_putaway_strategy_01(self):
        """Tests if the putaway strategy applies to a Manufacturing Order."""
        # Create MO
        mo = self._create_mo()
        for finished in mo.move_finished_ids:
            self.assertEqual(
                finished.location_dest_id,
                self.bin_loc_stock,
                "Putaway strategy hasn't been applied.",
            )
