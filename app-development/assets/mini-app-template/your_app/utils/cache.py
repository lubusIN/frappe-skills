import frappe


def cache_get(key: str):
    return frappe.cache().get_value(key)


def cache_set(key: str, value, expires_in_sec: int = 300):
    frappe.cache().set_value(key, value, expires_in_sec=expires_in_sec)
