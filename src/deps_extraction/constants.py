PROJECT_NAME = "extraction"
DESCRIPTION = "Service stores extracted-data and sends documents to the appropriate plugin."
V1_PREFIX = "/v1"
V2_PREFIX = "/v2"
BASE_API_PREFIX = "/api/extraction"
INTERNAL_API_PREFIX = "/api-internal/extraction"
API_PREFIX = BASE_API_PREFIX + V1_PREFIX
SWAGGER_DOC_URL = "/docs"

EXTRACTION_FIELDS_DESTINATION = "ExtractionFieldsDestination"
DOCUMENTS_EXCHANGER = "Documents"
DOCUMENT_TYPE_EXCHANGER = "DocumentType"
TEMPLATE_EXCHANGER: str = "Template"
CLOUD_NATIVE_EXTRACTION_EXCHANGER = "CloudNativeExtraction"
QUEUE = "extraction"

COMMANDS_QUEUE = "extraction-commands"
COMMANDS_CHANNEL = "ExtractionCommands"
SERVICE_CHANNEL = "ExtractionService"
COMMANDS_REPLIES_CHANNEL = "ExtractionCommandsReplies"

AI_FUSION_COMMANDS = "AiFusionCommands"
