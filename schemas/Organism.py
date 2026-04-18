from pydantic import BaseModel, field_validator
import re


_SAFE_PATTERN = re.compile(r"^[\w\s\-./,()]+$")


def _safe_string(v: str | None) -> str | None:
    """Reject strings that look like SQL injection attempts."""
    if v is None:
        return v
    if not _SAFE_PATTERN.match(v):
        raise ValueError(
            f"Value '{v}' contains forbidden characters. "
            "Only letters, digits, spaces and -./,() are allowed."
        )
    return v


class OrganismCreate(BaseModel):
    """Schema for POST /organisms — all required fields."""
    genome_id:     str
    organism_name: str | None = None
    ploidy_type:   str | None = None
    description:   str | None = None

    @field_validator("genome_id", "organism_name", "ploidy_type", "description", mode="before")
    @classmethod
    def validate_safe(cls, v):
        return _safe_string(v)


class OrganismUpdate(BaseModel):
    """Schema for PUT /organisms/{genome_id} — all fields optional."""
    organism_name: str | None = None
    ploidy_type:   str | None = None
    description:   str | None = None

    @field_validator("organism_name", "ploidy_type", "description", mode="before")
    @classmethod
    def validate_safe(cls, v):
        return _safe_string(v)


class OrganismRead(BaseModel):
    """Schema for GET responses."""
    genome_id:     str
    organism_name: str | None = None
    ploidy_type:   str | None = None
    description:   str | None = None

    model_config = {"from_attributes": True}
