# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def before_validate(doc, method):
    def set_existing_batch(item):
        if item.pb_expiry_date and not item.batch_no:
            has_batch_no, has_expiry_date = frappe.db.get_value(
                "Item", item.item_code, ["has_batch_no", "has_expiry_date"]
            )
            if has_batch_no and has_expiry_date:
                batch_no = frappe.db.exists(
                    "Batch",
                    {"item": item.item_code, "expiry_date": item.pb_expiry_date},
                )
                item.batch_no = batch_no

    def create_new_batch(item):
        if item.warehouse and item.pb_expiry_date and not item.batch_no:
            has_batch_no, create_new_batch, has_expiry_date = frappe.db.get_value(
                "Item",
                item.item_code,
                ["has_batch_no", "create_new_batch", "has_expiry_date"],
            )
            if has_batch_no and create_new_batch and has_expiry_date:
                batch = frappe.get_doc(
                    {
                        "doctype": "Batch",
                        "item": item.item_code,
                        "expiry_date": item.pb_expiry_date,
                        "supplier": doc.supplier,
                        "reference_doctype": doc.doctype,
                        "reference_name": doc.name,
                    }
                ).insert()
                item.batch_no = batch.name

    manage_batch = frappe.db.get_single_value("POS Bahrain Settings", "manage_batch")

    if manage_batch and doc._action == "save":
        map(set_existing_batch, doc.items)

        # TODO: when `before_validate` gets merged into master create_new_batch should
        # run when doc._action == 'submit'.
        # also update `hooks.py` to use `before_validate` instead of the current
        # `before_save` method
        map(create_new_batch, doc.items)
