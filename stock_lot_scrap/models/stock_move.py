# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_scrap(self):
        self.ensure_one()
        for lot in self.lot_ids if self.is_scrap else ():
            lot.message_post(
                body=Markup(
                    self.env._(
                        "Lot was scrapped by <b>%(name)s</b>.", name=self.env.user.name
                    )
                )
            )
        return super().action_scrap()
