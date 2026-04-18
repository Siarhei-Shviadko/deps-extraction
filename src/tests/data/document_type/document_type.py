__all__ = [
    "raw_prototype_document_type",
    "raw_plugin_document_type",
    "raw_template_document_type",
    "raw_document_type_without_extraction_type",
]

raw_prototype_document_type = {
    "document_type_id": "f9c001a3f5324f2e9d7afd84dedff6e3",
    "extraction_type": "prototype",
    "name": "111",
    "tenant_id": "3d2e2f95-a6d1-4035-b9ec-9ca63edd4009",
    "fields": [
        {
            "name": "Date",
            "required": False,
            "order": 0,
            "field_type": "date",
            "field_data": {"format": "%m/%d/%Y", "display_char_limit": 2},
            "code": "Date",
        },
    ],
}

raw_plugin_document_type = {
    "document_type_id": "10b4558feaa14c7dbdeed42170331dfb",
    "extraction_type": "plugin",
    "name": "DocumentType1",
    "tenant_id": "3d2e2f95-a6d1-4035-b9ec-9ca63edd4009",
    "fields": [
        {
            "name": "5656",
            "required": True,
            "order": 0,
            "field_type": "list",
            "field_data": {
                "base_type": "enum",
                "base_type_data": {
                    "options": ["23", "4"],
                },
            },
            "code": "88888",
        },
    ],
}

raw_template_document_type = {
    "document_type_id": "054d14cd2be244c2813fa9b5ba6d1889",
    "extraction_type": "template",
    "name": "Payroll Report",
    "tenant_id": "3d2e2f95-a6d1-4035-b9ec-9ca63edd4009",
    "fields": [
        {
            "name": "New",
            "required": False,
            "order": 1,
            "field_type": "string",
            "field_data": {
                "char_type": None,
                "char_whitelist": None,
                "char_blacklist": None,
                "display_char_limit": 1,
            },
            "code": "New",
        },
    ],
}

raw_document_type_without_extraction_type = {
    "document_type_id": "220486ca9d7a4ec1b8f8ddb4f87a2508",
    "extraction_type": None,
    "name": "test",
    "tenant_id": "3d2e2f95-a6d1-4035-b9ec-9ca63edd4009",
    "fields": [
        {
            "name": "Test34",
            "required": True,
            "order": 0,
            "field_type": "dict",
            "field_data": {
                "key_type": "string",
                "value_type": "string",
                "key_meta": None,
                "value_meta": None,
            },
            "code": "tttt",
        },
    ],
}
