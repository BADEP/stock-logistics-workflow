# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Scrap Reason Code",
    "version": "20.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Reason code for scrapping",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "data": [
        "views/reason_code_view.xml",
        "views/stock_move_views.xml",
        "security/ir.access.csv",
    ],
    "maintainers": ["bodedra"],
    "installable": True,
}
