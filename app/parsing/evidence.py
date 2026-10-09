"""Evidence data model and related types for TraceLens."""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EvidenceType(str, Enum):
    """Types of evidence that can be analyzed."""

    LOG = "log"
    STACK_TRACE = "stack_trace"
    SOURCE_CODE = "source_code"
    GIT_DIFF = "git_diff"
    DOCUMENTATION = "documentation"


class EvidenceSource(str, Enum):
    """Source categorization for evidence."""

    APPLICATION_LOG = "application_log"
    SYSTEM_LOG = "system_log"
    EXCEPTION = "exception"
    CODE_FILE = "code_file"
    GIT_COMMIT = "git_commit"
    DOCUMENTATION_FILE = "documentation_file"


class Evidence(BaseModel):
    """
    Represents a piece of evidence from an incident.

    Maintains full provenance through the pipeline: source file, line numbers,
    timestamps, and any applicable metadata.
    """

    id: str = Field(..., description="Unique identifier for this evidence")
    type: EvidenceType = Field(..., description="Classification of evidence type")
    source: EvidenceSource = Field(..., description="Source categorization")
    source_file: str = Field(..., description="Original source file or path")
    content: str = Field(..., description="Raw evidence content")

    # Line/position information
    start_line: Optional[int] = Field(None, description="Start line number (1-indexed)")
    end_line: Optional[int] = Field(None, description="End line number (1-indexed)")

    # Temporal information
    timestamp: Optional[datetime] = Field(None, description="When this evidence was generated")

    # Service and component information
    service: Optional[str] = Field(None, description="Service that generated this evidence")
    component: Optional[str] = Field(None, description="Component mentioned in evidence")

    # Error/exception information
    exception_type: Optional[str] = Field(None, description="Exception class if applicable")
    exception_message: Optional[str] = Field(None, description="Exception message if applicable")
    error_level: Optional[str] = Field(
        None, description="Log level if applicable (ERROR, WARN, DEBUG, etc.)"
    )

    # Additional metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional arbitrary metadata preserved from source",
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = False
        json_schema_extra = {
            "example": {
                "id": "evidence_001_log",
                "type": "log",
                "source": "application_log",
                "source_file": "logs/payment-service.log",
                "content": "ERROR PaymentService: NullPointerException at line 142",
                "start_line": 2845,
                "end_line": 2845,
                "timestamp": "2024-01-15T10:32:45.123Z",
                "service": "payment-service",
                "component": "PaymentService",
                "exception_type": "NullPointerException",
                "error_level": "ERROR",
                "metadata": {"source": "splunk"},
            }
        }

    def to_embedding_text(self) -> str:
        """
        Convert evidence to text suitable for embedding.

        Includes context from metadata to improve semantic similarity.
        """
        parts = [self.content]

        if self.service:
            parts.append(f"Service: {self.service}")

        if self.component:
            parts.append(f"Component: {self.component}")

        if self.exception_type:
            parts.append(f"Exception: {self.exception_type}")

        if self.error_level:
            parts.append(f"Level: {self.error_level}")

        return " | ".join(parts)
