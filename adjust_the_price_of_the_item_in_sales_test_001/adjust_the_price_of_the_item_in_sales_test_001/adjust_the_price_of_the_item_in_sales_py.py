# Copyright (c) 2024, Mahmoud Khattab
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

from frappe.utils import nowdate


import json
from frappe.utils import flt


from frappe.exceptions import ValidationError


@frappe.whitelist()
def create_print_msg(doc, method=None):
    frappe.msgprint(str("Adjust Item Price based on Foreign Purchases with Average Purchase Price profit margin"), alert=True)
    # doc.reload()






@frappe.whitelist()
def adjust_item_price_based_on_foreign_purchases_with_average_purchase_price_profit_margin(doc, method=None):
    """
    Adjust Item Price based on Foreign Purchases with Average Purchase Price and Profit Margin.
    This function is triggered on Submit of the Purchase Invoice.
    """
    for item in doc.items:
        item_code = item.item_code
        uom = item.uom

        # Fetch Item document
        item_doc = frappe.get_doc("Item", item_code)

        if item_doc.foreign_purchases_items_a_001:
            profit_margin = flt(item_doc.profit_margin_percentage_items_a_001)

            avg_purchase_price = calculate_average_purchase_price(item_code)

            if avg_purchase_price is not None:
                new_price = avg_purchase_price * (1 + profit_margin / 100)

                item_price_name = frappe.db.get_value("Item Price", {
                    "item_code": item_code,
                    "uom": uom
                }, "name")

                if item_price_name:
                    item_price_doc = frappe.get_doc("Item Price", item_price_name)
                    item_price_doc.price_list_rate = new_price
                    item_price_doc.save(ignore_permissions=True)
                else:
                    new_item_price = frappe.new_doc("Item Price")
                    new_item_price.item_code = item_code
                    new_item_price.uom = uom
                    new_item_price.price_list_rate = new_price
                    new_item_price.price_list = "Standard Selling"
                    new_item_price.save(ignore_permissions=True)

                frappe.msgprint(
                    f"Item Price for {item_code} has been updated to {new_price:.2f}.",
                    alert=True
                )


def calculate_average_purchase_price(item_code):
    """
    Calculate the average purchase price based on previous Purchase Invoices for the given item code.
    """
    purchase_invoices = frappe.db.sql(
        """
        SELECT
            AVG(base_net_rate) AS avg_rate
        FROM
            `tabPurchase Invoice Item`
        WHERE
            item_code = %s
        AND
            docstatus = 1
        """,
        (item_code,), as_dict=True
    )

    if purchase_invoices and purchase_invoices[0].avg_rate:
        return flt(purchase_invoices[0].avg_rate)

    return None




