from pydantic import BaseModel, field_validator
from typing import Literal
import re

_SAFE_PATTERN = re.compile(r"^[\w\s\-./,()]+$")


def _safe_string(v: str | None) -> str | None:
    if v is None:
        return v
    if not _SAFE_PATTERN.match(v):
        raise ValueError(f"Value '{v}' contains forbidden characters.")
    return v


class GenomeAnnotationCreate(BaseModel):
    genome_id: str
    set_type:  Literal["hc", "representative", "working"]
    gff3_file: str | None = None
    gff3_link: str | None = None
    cdna_file: str | None = None
    cdna_link: str | None = None
    cds_file:  str | None = None
    cds_link:  str | None = None
    pep_file:  str | None = None
    pep_link:  str | None = None

    @field_validator("genome_id", "gff3_file", "cdna_file", "cds_file", "pep_file", mode="before")
    @classmethod
    def validate_safe(cls, v):
        return _safe_string(v)


class GenomeAnnotationUpdate(BaseModel):
    gff3_file: str | None = None
    gff3_link: str | None = None
    cdna_file: str | None = None
    cdna_link: str | None = None
    cds_file:  str | None = None
    cds_link:  str | None = None
    pep_file:  str | None = None
    pep_link:  str | None = None

    @field_validator("gff3_file", "cdna_file", "cds_file", "pep_file", mode="before")
    @classmethod
    def validate_safe(cls, v):
        return _safe_string(v)


class GenomeAnnotationRead(BaseModel):
    genome_id: str
    set_type:  str
    gff3_file: str | None = None
    gff3_link: str | None = None
    cdna_file: str | None = None
    cdna_link: str | None = None
    cds_file:  str | None = None
    cds_link:  str | None = None
    pep_file:  str | None = None
    pep_link:  str | None = None

    model_config = {"from_attributes": True}
