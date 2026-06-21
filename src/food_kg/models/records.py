"""Validated, storage-neutral records used between curated data and Neo4j."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

NODE_LABELS = frozenset({
    "Nutrient", "Ingredient", "Additive", "FoodCategory", "FunctionalClass",
    "Allergen", "Alias", "HealthClaim", "HealthOutcome", "Source", "Regulation",
})
RELATIONSHIP_TYPES = frozenset({
    "IS_A", "DERIVED_FROM", "HAS_NUTRIENT", "CONTAINS_ALLERGEN", "HAS_FUNCTION",
    "PERMITTED_IN", "COMMON_IN", "OBSERVED_IN", "REFERS_TO", "SUBJECT_OF",
    "OUTCOME", "EVIDENCED_BY", "GOVERNS", "IN_CATEGORY", "BROADER_THAN",
    "SUPPORTED_BY", "SUPERSEDES",
})

class NodeRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str
    id: str = Field(pattern=r"^[A-Z_]+:[A-Z0-9_]+$")
    properties: dict[str, Any] = Field(default_factory=dict)

    @field_validator("label")
    @classmethod
    def label_is_allowed(cls, value: str) -> str:
        if value not in NODE_LABELS:
            raise ValueError(f"Unsupported node label: {value}")
        return value

class RelationshipRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start_id: str = Field(pattern=r"^[A-Z_]+:[A-Z0-9_]+$")
    end_id: str = Field(pattern=r"^[A-Z_]+:[A-Z0-9_]+$")
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)

    @field_validator("type")
    @classmethod
    def type_is_allowed(cls, value: str) -> str:
        if value not in RELATIONSHIP_TYPES:
            raise ValueError(f"Unsupported relationship type: {value}")
        return value

class CuratedRelease(BaseModel):
    version: str
    released_at: date
    source_ids: list[str]
    notes: str | None = None
