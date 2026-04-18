from .base import BusinessException, NotFoundError

__all__ = [
    "ExtractionWorkflowExhaustedError",
    "ExtractionWorkflowError",
    "ExtractionWorkflowExecutionError",
    "ExtractionWorkflowCreationError",
    "ExtractionWorkflowNotFoundError",
    "ExtractionStepException",
]


class ExtractionWorkflowError(BusinessException):
    code = "extraction_workflow_error"


class ExtractionWorkflowCreationError(ExtractionWorkflowError):
    code = "extraction_workflow_creation_error"


class ExtractionWorkflowExecutionError(ExtractionWorkflowError):
    code = "extraction_execution_error"


class ExtractionWorkflowExhaustedError(ExtractionWorkflowError):
    code = "extraction_workflow_start_error"


class ExtractionWorkflowNotFoundError(NotFoundError):
    code = "extraction_workflow_not_found_error"


class ExtractionStepException(ExtractionWorkflowError):
    code = "extraction_step_error"
