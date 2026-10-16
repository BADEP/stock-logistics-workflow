# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import typing

from odoo import models


class StockPickingBatch(models.Model):
    _name = "stock.picking.batch"
    _inherit: typing.ClassVar[list[str]] = [
        "stock.picking.batch",
        "base.substate.mixin",
    ]
