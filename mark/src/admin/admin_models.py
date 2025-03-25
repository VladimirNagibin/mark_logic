from sqladmin import ModelView

from models.entity import Product


class ProductAdmin(ModelView, model=Product):  # type: ignore
    column_list = [
        Product.name,
        Product.code_mark_head,
        Product.doc_in,
        Product.code_work,
        Product.code_hs,
        Product.code_mark,
        Product.data_in,
        Product.doc_out,
        Product.data_out,
        Product.status,
    ]
    can_create = True
    can_edit = True
    can_delete = True
