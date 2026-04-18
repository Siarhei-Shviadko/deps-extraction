from enum import StrEnum

from .cloud_native_extractors import *

__all__ = ["ExtractionType"]


class ExtractionType(StrEnum):
    PLUGIN = "plugin"
    TEMPLATE = "template"
    PROTOTYPE = "prototype"
    NON = "non"
    AZURE_CLOUD_EXTRACTOR = CloudNativeExtractors.AZURE_CLOUD_EXTRACTOR.value
