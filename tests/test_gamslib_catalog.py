"""Tests for GAMSLIB catalog dataclasses."""

import json
import tempfile
from pathlib import Path

import pytest

from scripts.gamslib.catalog import (
    VALID_DOWNLOAD_STATUS,
    VALID_MODEL_TYPES,
    GamslibCatalog,
    ModelEntry,
)


class TestModelEntry:
    """Tests for ModelEntry dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating a ModelEntry with minimal required fields."""
        entry = ModelEntry(
            model_id="trnsport",
            sequence_number=1,
            model_name="A Transportation Problem",
            gamslib_type="LP",
            source_url="https://www.gams.com/latest/gamslib_ml/trnsport.1",
        )
        assert entry.model_id == "trnsport"
        assert entry.sequence_number == 1
        assert entry.model_name == "A Transportation Problem"
        assert entry.gamslib_type == "LP"
        assert entry.download_status == "pending"
        assert entry.keywords == []
        assert entry.notes == ""

    def test_create_with_all_fields(self) -> None:
        """Test creating a ModelEntry with all fields."""
        entry = ModelEntry(
            model_id="circle",
            sequence_number=201,
            model_name="Circle Enclosing Points",
            gamslib_type="NLP",
            source_url="https://www.gams.com/latest/gamslib_ml/circle.201",
            web_page_url="https://www.gams.com/latest/gamslib_ml/libhtml/gamslib_circle.html",
            description="Find smallest circle enclosing points",
            keywords=["nonlinear programming", "geometry"],
            download_status="downloaded",
            download_date="2025-12-31T10:00:00Z",
            file_path="data/gamslib/raw/circle.gms",
            file_size_bytes=1297,
            notes="Convex NLP",
        )
        assert entry.model_id == "circle"
        assert entry.gamslib_type == "NLP"
        assert entry.download_status == "downloaded"
        assert entry.keywords == ["nonlinear programming", "geometry"]
        assert entry.file_size_bytes == 1297

    def test_invalid_gamslib_type(self) -> None:
        """Test that invalid gamslib_type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid gamslib_type"):
            ModelEntry(
                model_id="test",
                sequence_number=1,
                model_name="Test",
                gamslib_type="INVALID",
                source_url="https://example.com",
            )

    def test_invalid_download_status(self) -> None:
        """Test that invalid download_status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid download_status"):
            ModelEntry(
                model_id="test",
                sequence_number=1,
                model_name="Test",
                gamslib_type="LP",
                source_url="https://example.com",
                download_status="invalid_status",
            )

    def test_to_dict(self) -> None:
        """Test serializing ModelEntry to dictionary."""
        entry = ModelEntry(
            model_id="trnsport",
            sequence_number=1,
            model_name="A Transportation Problem",
            gamslib_type="LP",
            source_url="https://www.gams.com/latest/gamslib_ml/trnsport.1",
            keywords=["linear programming"],
        )
        d = entry.to_dict()
        assert d["model_id"] == "trnsport"
        assert d["sequence_number"] == 1
        assert d["gamslib_type"] == "LP"
        assert d["keywords"] == ["linear programming"]
        assert d["download_status"] == "pending"

    def test_from_dict(self) -> None:
        """Test deserializing ModelEntry from dictionary."""
        data = {
            "model_id": "blend",
            "sequence_number": 2,
            "model_name": "Blending Problem",
            "gamslib_type": "LP",
            "source_url": "https://www.gams.com/latest/gamslib_ml/blend.2",
            "keywords": ["blending"],
            "download_status": "pending",
            "download_date": None,
            "file_path": None,
            "file_size_bytes": None,
            "notes": "",
        }
        entry = ModelEntry.from_dict(data)
        assert entry.model_id == "blend"
        assert entry.gamslib_type == "LP"
        assert entry.keywords == ["blending"]

    def test_valid_model_types(self) -> None:
        """Test that all valid model types are accepted."""
        for model_type in VALID_MODEL_TYPES:
            entry = ModelEntry(
                model_id="test",
                sequence_number=1,
                model_name="Test",
                gamslib_type=model_type,
                source_url="https://example.com",
            )
            assert entry.gamslib_type == model_type

    def test_valid_download_statuses(self) -> None:
        """Test that all valid download statuses are accepted."""
        for status in VALID_DOWNLOAD_STATUS:
            entry = ModelEntry(
                model_id="test",
                sequence_number=1,
                model_name="Test",
                gamslib_type="LP",
                source_url="https://example.com",
                download_status=status,
            )
            assert entry.download_status == status


class TestGamslibCatalog:
    """Tests for GamslibCatalog dataclass."""

    def test_create_empty_catalog(self) -> None:
        """Test creating an empty catalog."""
        catalog = GamslibCatalog()
        assert catalog.schema_version == "1.0.0"
        assert catalog.total_models == 0
        assert catalog.models == []
        assert catalog.gams_version is None

    def test_create_catalog_with_version(self) -> None:
        """Test creating a catalog with GAMS version."""
        catalog = GamslibCatalog(gams_version="51.3.0")
        assert catalog.gams_version == "51.3.0"

    def test_total_models_property(self) -> None:
        """Test that total_models reflects actual model count."""
        catalog = GamslibCatalog()
        assert catalog.total_models == 0

        catalog.models.append(
            ModelEntry(
                model_id="trnsport",
                sequence_number=1,
                model_name="Transport",
                gamslib_type="LP",
                source_url="https://example.com",
            )
        )
        assert catalog.total_models == 1

        catalog.models.append(
            ModelEntry(
                model_id="circle",
                sequence_number=201,
                model_name="Circle",
                gamslib_type="NLP",
                source_url="https://example.com",
            )
        )
        assert catalog.total_models == 2

    def test_to_dict(self) -> None:
        """Test serializing catalog to dictionary."""
        catalog = GamslibCatalog(gams_version="51.3.0")
        catalog.models.append(
            ModelEntry(
                model_id="trnsport",
                sequence_number=1,
                model_name="Transport",
                gamslib_type="LP",
                source_url="https://example.com",
            )
        )
        d = catalog.to_dict()
        assert d["schema_version"] == "1.0.0"
        assert d["gams_version"] == "51.3.0"
        assert d["total_models"] == 1
        assert len(d["models"]) == 1
        assert d["models"][0]["model_id"] == "trnsport"

    def test_save_and_load(self) -> None:
        """Test saving and loading catalog from file."""
        catalog = GamslibCatalog(gams_version="51.3.0")
        catalog.models.append(
            ModelEntry(
                model_id="trnsport",
                sequence_number=1,
                model_name="A Transportation Problem",
                gamslib_type="LP",
                source_url="https://www.gams.com/latest/gamslib_ml/trnsport.1",
                keywords=["linear programming"],
            )
        )

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            catalog.save(temp_path)

            # Verify file contents
            with open(temp_path) as f:
                data = json.load(f)
            assert data["total_models"] == 1
            assert data["models"][0]["model_id"] == "trnsport"

            # Load and verify
            loaded = GamslibCatalog.load(temp_path)
            assert loaded.gams_version == "51.3.0"
            assert loaded.total_models == 1
            assert loaded.models[0].model_id == "trnsport"
            assert loaded.models[0].keywords == ["linear programming"]
        finally:
            temp_path.unlink()

    def test_get_models_by_type(self) -> None:
        """Test filtering models by type."""
        catalog = GamslibCatalog()
        catalog.models.extend(
            [
                ModelEntry(
                    model_id="trnsport",
                    sequence_number=1,
                    model_name="Transport",
                    gamslib_type="LP",
                    source_url="https://example.com",
                ),
                ModelEntry(
                    model_id="blend",
                    sequence_number=2,
                    model_name="Blend",
                    gamslib_type="LP",
                    source_url="https://example.com",
                ),
                ModelEntry(
                    model_id="circle",
                    sequence_number=201,
                    model_name="Circle",
                    gamslib_type="NLP",
                    source_url="https://example.com",
                ),
            ]
        )

        lp_models = catalog.get_models_by_type("LP")
        assert len(lp_models) == 2
        assert all(m.gamslib_type == "LP" for m in lp_models)

        nlp_models = catalog.get_models_by_type("NLP")
        assert len(nlp_models) == 1
        assert nlp_models[0].model_id == "circle"

        qcp_models = catalog.get_models_by_type("QCP")
        assert len(qcp_models) == 0

    def test_get_models_by_status(self) -> None:
        """Test filtering models by download status."""
        catalog = GamslibCatalog()
        catalog.models.extend(
            [
                ModelEntry(
                    model_id="trnsport",
                    sequence_number=1,
                    model_name="Transport",
                    gamslib_type="LP",
                    source_url="https://example.com",
                    download_status="downloaded",
                ),
                ModelEntry(
                    model_id="blend",
                    sequence_number=2,
                    model_name="Blend",
                    gamslib_type="LP",
                    source_url="https://example.com",
                    download_status="pending",
                ),
                ModelEntry(
                    model_id="weapons",
                    sequence_number=19,
                    model_name="Weapons",
                    gamslib_type="MIP",
                    source_url="https://example.com",
                    download_status="excluded",
                ),
            ]
        )

        pending = catalog.get_models_by_status("pending")
        assert len(pending) == 1
        assert pending[0].model_id == "blend"

        downloaded = catalog.get_models_by_status("downloaded")
        assert len(downloaded) == 1
        assert downloaded[0].model_id == "trnsport"

        excluded = catalog.get_models_by_status("excluded")
        assert len(excluded) == 1
        assert excluded[0].model_id == "weapons"

    def test_get_model_by_id(self) -> None:
        """Test getting a model by ID."""
        catalog = GamslibCatalog()
        catalog.models.append(
            ModelEntry(
                model_id="trnsport",
                sequence_number=1,
                model_name="Transport",
                gamslib_type="LP",
                source_url="https://example.com",
            )
        )

        model = catalog.get_model_by_id("trnsport")
        assert model is not None
        assert model.model_id == "trnsport"

        missing = catalog.get_model_by_id("nonexistent")
        assert missing is None

    def test_add_model(self) -> None:
        """Test adding a model to catalog."""
        catalog = GamslibCatalog()
        model = ModelEntry(
            model_id="trnsport",
            sequence_number=1,
            model_name="Transport",
            gamslib_type="LP",
            source_url="https://example.com",
        )
        catalog.add_model(model)
        assert catalog.total_models == 1
        assert catalog.get_model_by_id("trnsport") is not None

    def test_add_duplicate_model_raises(self) -> None:
        """Test that adding duplicate model raises ValueError."""
        catalog = GamslibCatalog()
        model = ModelEntry(
            model_id="trnsport",
            sequence_number=1,
            model_name="Transport",
            gamslib_type="LP",
            source_url="https://example.com",
        )
        catalog.add_model(model)

        with pytest.raises(ValueError, match="already exists"):
            catalog.add_model(model)

    def test_update_model(self) -> None:
        """Test updating model attributes."""
        catalog = GamslibCatalog()
        catalog.models.append(
            ModelEntry(
                model_id="trnsport",
                sequence_number=1,
                model_name="Transport",
                gamslib_type="LP",
                source_url="https://example.com",
                download_status="pending",
            )
        )

        updated = catalog.update_model(
            "trnsport",
            download_status="downloaded",
            download_date="2025-12-31T10:00:00Z",
            file_path="data/gamslib/raw/trnsport.gms",
            file_size_bytes=1751,
        )

        assert updated is not None
        assert updated.download_status == "downloaded"
        assert updated.download_date == "2025-12-31T10:00:00Z"
        assert updated.file_path == "data/gamslib/raw/trnsport.gms"
        assert updated.file_size_bytes == 1751

    def test_update_nonexistent_model(self) -> None:
        """Test that updating nonexistent model returns None."""
        catalog = GamslibCatalog()
        result = catalog.update_model("nonexistent", download_status="downloaded")
        assert result is None

    def test_load_empty_catalog(self) -> None:
        """Test loading an empty catalog."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump(
                {
                    "schema_version": "1.0.0",
                    "created_date": "2025-12-31T00:00:00Z",
                    "updated_date": "2025-12-31T00:00:00Z",
                    "gams_version": "51.3.0",
                    "total_models": 0,
                    "models": [],
                },
                f,
            )
            temp_path = Path(f.name)

        try:
            catalog = GamslibCatalog.load(temp_path)
            assert catalog.total_models == 0
            assert catalog.models == []
        finally:
            temp_path.unlink()

    def test_load_with_missing_optional_fields(self) -> None:
        """Test loading catalog where models have minimal fields."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump(
                {
                    "schema_version": "1.0.0",
                    "created_date": "2025-12-31T00:00:00Z",
                    "updated_date": "2025-12-31T00:00:00Z",
                    "total_models": 1,
                    "models": [
                        {
                            "model_id": "trnsport",
                            "sequence_number": 1,
                            "model_name": "Transport",
                            "gamslib_type": "LP",
                            "source_url": "https://example.com",
                            "web_page_url": None,
                            "description": None,
                            "keywords": [],
                            "download_status": "pending",
                            "download_date": None,
                            "file_path": None,
                            "file_size_bytes": None,
                            "notes": "",
                        }
                    ],
                },
                f,
            )
            temp_path = Path(f.name)

        try:
            catalog = GamslibCatalog.load(temp_path)
            assert catalog.total_models == 1
            assert catalog.models[0].model_id == "trnsport"
            assert catalog.models[0].web_page_url is None
            assert catalog.gams_version is None
        finally:
            temp_path.unlink()
