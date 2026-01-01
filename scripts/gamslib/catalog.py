"""GAMSLIB catalog dataclasses for model metadata tracking.

This module provides dataclasses for managing the GAMSLIB model catalog,
which tracks model metadata, download status, and (in Sprint 14) convexity
verification results.

Example usage:
    >>> from scripts.gamslib.catalog import GamslibCatalog, ModelEntry
    >>>
    >>> # Create a new catalog
    >>> catalog = GamslibCatalog(gams_version="51.3.0")
    >>>
    >>> # Add a model
    >>> model = ModelEntry(
    ...     model_id="trnsport",
    ...     sequence_number=1,
    ...     model_name="A Transportation Problem",
    ...     gamslib_type="LP",
    ...     source_url="https://www.gams.com/latest/gamslib_ml/trnsport.1",
    ... )
    >>> catalog.models.append(model)
    >>>
    >>> # Save to file
    >>> catalog.save("data/gamslib/catalog.json")
    >>>
    >>> # Load from file
    >>> catalog = GamslibCatalog.load("data/gamslib/catalog.json")
    >>>
    >>> # Query by type
    >>> lp_models = catalog.get_models_by_type("LP")
    >>> pending = catalog.get_models_by_status("pending")
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Valid model types from GAMSLIB
VALID_MODEL_TYPES = frozenset(
    [
        "LP",  # Linear Program (always convex)
        "NLP",  # Nonlinear Program
        "QCP",  # Quadratically Constrained Program
        "MIP",  # Mixed Integer Program (excluded)
        "MINLP",  # Mixed Integer NLP (excluded)
        "MIQCP",  # Mixed Integer QCP (excluded)
        "MCP",  # Mixed Complementarity Problem (excluded)
        "MPEC",  # Math Program with Equilibrium Constraints (excluded)
        "CNS",  # Constrained Nonlinear System (excluded)
        "DNLP",  # Discontinuous NLP (excluded)
        "EMP",  # Extended Mathematical Program (excluded)
        "MPSGE",  # General Equilibrium (excluded)
        "GAMS",  # GAMS-specific (excluded)
        "DECIS",  # Stochastic programming (excluded)
    ]
)

# Valid download status values
VALID_DOWNLOAD_STATUS = frozenset(
    [
        "pending",  # Not yet downloaded
        "downloaded",  # Successfully downloaded
        "failed",  # Download failed
        "excluded",  # Excluded from corpus
    ]
)


@dataclass
class ModelEntry:
    """Single model entry in the GAMSLIB catalog.

    Attributes:
        model_id: Unique identifier (lowercase model name, e.g., "trnsport")
        sequence_number: GAMSLIB sequence number (used in download URL)
        model_name: Human-readable model name from GAMSLIB
        gamslib_type: Model type as declared in GAMSLIB (LP, NLP, QCP, etc.)
        source_url: Direct download URL for .gms file
        web_page_url: URL to GAMSLIB documentation page
        description: Brief description from GAMSLIB
        keywords: List of keywords/tags from GAMSLIB
        download_status: Current download status (pending, downloaded, failed, excluded)
        download_date: ISO 8601 timestamp of successful download
        file_path: Relative path to downloaded .gms file
        file_size_bytes: Size of downloaded file in bytes
        notes: Free-form notes about the model
    """

    # Identification
    model_id: str
    sequence_number: int
    model_name: str

    # Type and classification
    gamslib_type: str

    # Source information
    source_url: str
    web_page_url: str | None = None
    description: str | None = None
    keywords: list[str] = field(default_factory=list)

    # Download status
    download_status: str = "pending"
    download_date: str | None = None
    file_path: str | None = None
    file_size_bytes: int | None = None

    # Metadata
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if self.gamslib_type not in VALID_MODEL_TYPES:
            raise ValueError(
                f"Invalid gamslib_type '{self.gamslib_type}'. "
                f"Valid types: {sorted(VALID_MODEL_TYPES)}"
            )
        if self.download_status not in VALID_DOWNLOAD_STATUS:
            raise ValueError(
                f"Invalid download_status '{self.download_status}'. "
                f"Valid values: {sorted(VALID_DOWNLOAD_STATUS)}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelEntry":
        """Create ModelEntry from dictionary."""
        return cls(**data)


def _get_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class GamslibCatalog:
    """GAMSLIB model catalog.

    Attributes:
        schema_version: Semantic version of the schema (e.g., "1.0.0")
        created_date: ISO 8601 timestamp when catalog was created
        updated_date: ISO 8601 timestamp of last update
        gams_version: GAMS version used for model discovery
        models: List of ModelEntry objects
    """

    schema_version: str = "1.0.0"
    created_date: str = field(default_factory=_get_utc_timestamp)
    updated_date: str = field(default_factory=_get_utc_timestamp)
    gams_version: str | None = None
    models: list[ModelEntry] = field(default_factory=list)

    @property
    def total_models(self) -> int:
        """Return the total number of models in the catalog."""
        return len(self.models)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "schema_version": self.schema_version,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "gams_version": self.gams_version,
            "total_models": self.total_models,
            "models": [m.to_dict() for m in self.models],
        }

    def save(self, path: str | Path) -> None:
        """Save catalog to JSON file.

        Args:
            path: Path to output JSON file
        """
        self.updated_date = _get_utc_timestamp()
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "GamslibCatalog":
        """Load catalog from JSON file.

        Args:
            path: Path to input JSON file

        Returns:
            GamslibCatalog instance
        """
        with open(path) as f:
            data = json.load(f)

        models = [ModelEntry.from_dict(m) for m in data.get("models", [])]
        return cls(
            schema_version=data.get("schema_version", "1.0.0"),
            created_date=data.get("created_date", ""),
            updated_date=data.get("updated_date", ""),
            gams_version=data.get("gams_version"),
            models=models,
        )

    def get_models_by_type(self, gamslib_type: str) -> list[ModelEntry]:
        """Get all models of a specific type.

        Args:
            gamslib_type: Model type to filter by (e.g., "LP", "NLP", "QCP")

        Returns:
            List of ModelEntry objects matching the type
        """
        return [m for m in self.models if m.gamslib_type == gamslib_type]

    def get_models_by_status(self, download_status: str) -> list[ModelEntry]:
        """Get all models with a specific download status.

        Args:
            download_status: Status to filter by (pending, downloaded, failed, excluded)

        Returns:
            List of ModelEntry objects matching the status
        """
        return [m for m in self.models if m.download_status == download_status]

    def get_model_by_id(self, model_id: str) -> ModelEntry | None:
        """Get a model by its ID.

        Args:
            model_id: Model ID to find (e.g., "trnsport")

        Returns:
            ModelEntry if found, None otherwise
        """
        for m in self.models:
            if m.model_id == model_id:
                return m
        return None

    def add_model(self, model: ModelEntry) -> None:
        """Add a model to the catalog.

        Args:
            model: ModelEntry to add

        Raises:
            ValueError: If a model with the same ID already exists
        """
        if self.get_model_by_id(model.model_id) is not None:
            raise ValueError(f"Model with ID '{model.model_id}' already exists")
        self.models.append(model)

    def update_model(self, model_id: str, **kwargs: Any) -> ModelEntry | None:
        """Update a model's attributes.

        Args:
            model_id: Model ID to update
            **kwargs: Attributes to update

        Returns:
            Updated ModelEntry if found, None otherwise
        """
        model = self.get_model_by_id(model_id)
        if model is None:
            return None

        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)

        return model
