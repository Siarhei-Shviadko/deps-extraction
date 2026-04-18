from enum import StrEnum

from .cloud_native_extractors import *

__all__ = ["ExtractorType"]


class ExtractorType(StrEnum):
    PLUGIN = "plugin"
    TEMPLATE = "template"
    PROTOTYPE = "prototype"
    LLM = "llm"
    AZURE_CLOUD_EXTRACTOR = CloudNativeExtractors.AZURE_CLOUD_EXTRACTOR.value
