from sqladmin import ModelView
from wtforms import Form, StringField
from wtforms.validators import Optional

from models.entity import Product, ProductHS

PRODUCT_NAME = "name"


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
        PRODUCT_NAME: "Наименование",
        #  (
        #    "Наименование:(0[NOT_DEFINED] - не определено,"
        #    "1[ON_BALANCE] - на остатках,"
        #    "2[DEDUCTED] - списан,"
        #    "3[IN_HS_DEDUCTED] - есть в ЧЗ нет на остатках)"
        #  ),
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
    column_default_sort = [(PRODUCT_NAME, True)]
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

    async def scaffold_form(
        self, rules: list[str] | None = None
    ) -> type[Form]:
        form_class = await super().scaffold_form(rules)
        default_render_kw = {
            "class": "form-control",  # Основной класс стилей
            "autocomplete": "off",  # Стандартный атрибут в SQLAdmin
            "spellcheck": "false",  # Отключение проверки орфографии
        }
        form_class.code_mark = StringField(
            "QR криптохвост",
            validators=[Optional()],
            render_kw=default_render_kw,
        )
        form_class.code_mark_mid = StringField(
            "QR сред", validators=[Optional()], render_kw=default_render_kw
        )
        form_class.doc_out = StringField(
            "Исходящий документ",
            validators=[Optional()],
            render_kw=default_render_kw,
        )
        return form_class  # type: ignore


class ProductHSAdmin(ModelView, model=ProductHS):  # type: ignore
    page_title = "Управление QR"
    column_list = [
        ProductHS.name,
        ProductHS.code_mark_head,
        ProductHS.brand,
        ProductHS.code_hs,
        ProductHS.code_customs,
        ProductHS.inn_supplier,
        ProductHS.name_supplier,
        ProductHS.data_in,
    ]
    column_labels = {
        PRODUCT_NAME: "Наименование",
        "code_mark_head": "QR код",
        "brand": "Бренд",
        "code_hs": "Код GTIN",
        "code_customs": "ТН ВЭД",
        "inn_supplier": "ИНН производителя/импортера",
        "name_supplier": "Производитель",
        "data_in": "Дата ввода в оборот",
    }
    column_default_sort = [(PRODUCT_NAME, True)]
    column_sortable_list = [
        ProductHS.name,
        ProductHS.brand,
        ProductHS.inn_supplier,
        ProductHS.data_in,
    ]
    column_searchable_list = [
        Product.name,
        Product.code_mark_head,
    ]
    can_create = True
    can_edit = True
    can_delete = True
    page_size = 50
