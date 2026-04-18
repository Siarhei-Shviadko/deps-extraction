from random import choice, randint
from uuid import uuid4

from deps_extraction.domain.model import FieldType, StringFieldDescription

__all__ = [
    "create_field_payload",
    "create_field_payload_2",
    "update_field_payload",
    "create_field_with_full_payload",
]

create_field_payload = {
    "name": uuid4().hex,
    "type": choice(list(FieldType)),
    "required": choice((True, False)),
}

create_field_payload_2 = {
    "name": uuid4().hex,
    "type": choice(list(FieldType)),
    "required": choice((True, False)),
}

update_field_payload = {
    "name": uuid4().hex,
    "required": choice((True, False)),
}


create_field_with_full_payload = {
    "name": uuid4().hex,
    "type_": FieldType.STRING,
    "description": StringFieldDescription(),
    "required": choice((True, False)),
    "order": randint(1, 10),
    "read_only": choice((True, False)),
    "confidential": choice((True, False)),
}
