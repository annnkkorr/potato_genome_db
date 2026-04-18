from pydantic import BaseModel, field_validator
import re

_SAFE_PATTERN = re.compile(r"^[\w\s\-./,()]+$")


def _safe_string(v: str | None) -> str | None:
    if v is None:
        return v
    if not _SAFE_PATTERN.match(v):
        raise ValueError(f"Value '{v}' contains forbidden characters.")
    return v


class GenomeAssemblyCreate(BaseModel):
    genome_id:       str
    assembly_file:   str | None = None
    assembly_link:   str | None = None
    masked_file:     str | None = None
    masked_link:     str | None = None
    softmasked_file: str | None = None
    softmasked_link: str | None = None
    release_date:    str | None = None   # expected format: YYYY-MM-DD

    @field_validator("genome_id", "assembly_file", "masked_file",
                     "softmasked_file", "release_date", mode="before")
    @classmethod
    def validate_safe(cls, v):
        return _safe_string(v)

    @field_validator("release_date", mode="before")
    @classmethod
    def validate_date(cls, v):
        if v is None:
            return v
        v = v.strip()
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", v):
            d, m, y = v.split("/")
            return f"{y}-{m}-{d}"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            return v
        raise ValueError("Дата должна быть в формате дд/мм/гггг")


class GenomeAssemblyUpdate(BaseModel):
    assembly_file:   str | None = None
    assembly_link:   str | None = None
    masked_file:     str | None = None
    masked_link:     str | None = None
    softmasked_file: str | None = None
    softmasked_link: str | None = None
    release_date:    str | None = None

    @field_validator("assembly_file", "masked_file", "softmasked_file", mode="before")
    @classmethod
    def validate_safe(cls, v):
        return _safe_string(v)

    @field_validator("release_date", mode="before")
    @classmethod
    def validate_date(cls, v):
        if v is None:
            return v
        v = v.strip()
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", v):
            d, m, y = v.split("/")
            return f"{y}-{m}-{d}"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            return v
        raise ValueError("Дата должна быть в формате дд/мм/гггг")


class GenomeAssemblyRead(BaseModel):
    genome_id:       str
    assembly_file:   str | None = None
    assembly_link:   str | None = None
    masked_file:     str | None = None
    masked_link:     str | None = None
    softmasked_file: str | None = None
    softmasked_link: str | None = None
    release_date:    str | None = None

    model_config = {"from_attributes": True}
