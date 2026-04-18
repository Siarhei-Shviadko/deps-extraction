import random
import string

from factory import Factory, LazyFunction, fuzzy, lazy_attribute
from faker import Faker

from deps_extraction.domain.model import (
    CharType,
    DateFieldDescription,
    DictFieldDescription,
    EnumFieldDescription,
    FieldDescription,
    FieldProfile,
    FieldType,
    ListFieldDescription,
    StringFieldDescription,
    TableColumnDescription,
    TableFieldDescription,
)

__all__ = [
    "FieldProfileFactory",
    "StringFieldDescriptionFactory",
    "EnumFieldDescriptionFactory",
    "DateFieldDescriptionFactory",
    "DictFieldDescriptionFactory",
    "TableFieldDescriptionFactory",
    "ListFieldDescriptionFactory",
]

fake = Faker()


class FieldDescriptionFactory(Factory):
    class Meta:
        model = FieldDescription


class StringFieldDescriptionFactory(Factory):
    class Meta:
        model = StringFieldDescription

    char_type = fuzzy.FuzzyChoice((None, *list(CharType)))
    char_whitelist = fuzzy.FuzzyChoice((None, *string.ascii_lowercase))
    char_blacklist = fuzzy.FuzzyChoice((None, *string.ascii_lowercase))
    display_char_limit = fuzzy.FuzzyInteger(0, 10)


class EnumFieldDescriptionFactory(Factory):
    class Meta:
        model = EnumFieldDescription

    options = LazyFunction(lambda: [fake.name() for _ in range(random.randint(0, 3))])


class DateFieldDescriptionFactory(Factory):
    class Meta:
        model = DateFieldDescription

    format = fuzzy.FuzzyChoice(("%d.%m.%Y", "%d/%m/%Y", "%m.%d.%Y"))
    display_char_limit = fuzzy.FuzzyInteger(0, 10)


class DictFieldDescriptionFactory(Factory):
    class Meta:
        model = DictFieldDescription

    key_type = FieldType.STRING
    key_meta = fuzzy.FuzzyChoice((None, StringFieldDescriptionFactory.build()))
    value_type = FieldType.STRING
    value_meta = fuzzy.FuzzyChoice((None, StringFieldDescriptionFactory.build()))


class TableColumnDescriptionFactory(Factory):
    class Meta:
        model = TableColumnDescription

    title = fake.name()
    column_type = FieldType.STRING
    column_data = fuzzy.FuzzyChoice((None, StringFieldDescriptionFactory.build()))


class TableFieldDescriptionFactory(Factory):
    class Meta:
        model = TableFieldDescription

    columns = LazyFunction(lambda: [TableColumnDescriptionFactory()])


class ListFieldDescriptionFactory(Factory):
    class Meta:
        model = ListFieldDescription

    item_type = fuzzy.FuzzyChoice(
        (
            FieldType.STRING,
            FieldType.ENUM,
            FieldType.CHECKMARK,
            FieldType.DICT,
            FieldType.TABLE,
            FieldType.DATE,
        )
    )

    @lazy_attribute
    def item_type_data(self):
        if self.item_type == FieldType.STRING:
            return StringFieldDescriptionFactory()
        if self.item_type == FieldType.DICT:
            return DictFieldDescriptionFactory()
        if self.item_type == FieldType.TABLE:
            return TableFieldDescriptionFactory()
        if self.item_type == FieldType.ENUM:
            return EnumFieldDescriptionFactory()
        if self.item_type == FieldType.DATE:
            return DateFieldDescriptionFactory()
        return None


class FieldProfileFactory(Factory):
    class Meta:
        model = FieldProfile

    type_ = fuzzy.FuzzyChoice(
        (
            FieldType.STRING,
            FieldType.ENUM,
            FieldType.CHECKMARK,
            FieldType.DICT,
            FieldType.TABLE,
            FieldType.DATE,
            FieldType.LIST,
        )
    )

    @lazy_attribute
    def description(self):
        if self.type_ == FieldType.STRING:
            return StringFieldDescriptionFactory()
        if self.type_ == FieldType.DICT:
            return DictFieldDescriptionFactory()
        if self.type_ == FieldType.TABLE:
            return TableFieldDescriptionFactory()
        if self.type_ == FieldType.LIST:
            return ListFieldDescriptionFactory()
        if self.type_ == FieldType.ENUM:
            return EnumFieldDescriptionFactory()
        if self.type_ == FieldType.DATE:
            return DateFieldDescriptionFactory()

        return FieldDescriptionFactory()
