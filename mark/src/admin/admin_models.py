from sqladmin import ModelView

from models.entity import Product


class ProductAdmin(ModelView, model=Product):  # type: ignore
    page_title = "Управление QR"
    column_list = [
        Product.name,
        Product.status,
        Product.code_work,
        Product.code_hs,
        Product.code_mark_head,
        Product.code_mark,
        Product.code_mark_mid,
        Product.doc_in,
        Product.data_in,
        Product.doc_out,
        Product.data_out,
    ]
    column_labels = {
        "name": (
            "Наименование:(0[NOT_DEFINED] - не определено,"
            "1[ON_BALANCE] - на остатках,"
            "2[DEDUCTED] - списан,"
            "3[IN_HS_DEDUCTED] - есть в ЧЗ нет на остатках)"
        ),
        "code_work": "Код work",
        "code_hs": "Код GTIN",
        "code_mark_head": "QR код",
        "code_mark": "QR криптохвост",
        "code_mark_mid": "QR сред",
        "doc_in": "Входящий документ",
        "data_in": "Дата прихода",
        "doc_out": "Исходящий документ",
        "data_out": "Дата выбытия",
        "status": "Статус",
    }
    column_default_sort = [("name", True)]
    column_sortable_list = [
        Product.name,
        Product.data_in,
        Product.data_out,
        Product.status,
    ]
    column_searchable_list = [
        Product.name,
        Product.code_mark_head,
        Product.doc_in,
    ]
    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50
