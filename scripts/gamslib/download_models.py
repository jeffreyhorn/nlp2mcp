#!/usr/bin/env python3
"""Download GAMSLIB models to the local filesystem.

This script uses the `gamslib` command to extract models to `data/gamslib/raw/`.
It supports idempotent downloads (skipping existing files), error handling,
and catalog status updates.

Usage:
    python scripts/gamslib/download_models.py --all           # Download all pending models
    python scripts/gamslib/download_models.py --model trnsport  # Download specific model
    python scripts/gamslib/download_models.py --all --force   # Re-download all models
    python scripts/gamslib/download_models.py --dry-run       # Show what would be downloaded

Options:
    --model MODEL   Download a specific model by ID
    --all           Download all pending models from catalog
    --force         Re-download even if file exists
    --dry-run       Show what would be downloaded without downloading
    --verbose       Show detailed progress information
    --batch-size N  Save catalog after every N downloads (default: 10)
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.gamslib.catalog import GamslibCatalog, ModelEntry

# Paths
CATALOG_PATH = PROJECT_ROOT / "data" / "gamslib" / "catalog.json"
RAW_DIR = PROJECT_ROOT / "data" / "gamslib" / "raw"
ERROR_LOG_PATH = PROJECT_ROOT / "data" / "gamslib" / "download_errors.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class DownloadResult:
    """Results from a download operation."""

    total_attempted: int = 0
    successful: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[tuple[str, str]] = field(default_factory=list)  # (model_id, error)

    def add_success(self) -> None:
        self.total_attempted += 1
        self.successful += 1

    def add_skip(self) -> None:
        self.total_attempted += 1
        self.skipped += 1

    def add_failure(self, model_id: str, error: str) -> None:
        self.total_attempted += 1
        self.failed += 1
        self.errors.append((model_id, error))


def get_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def download_model(
    model: ModelEntry,
    target_dir: Path,
) -> tuple[bool, str | None]:
    """Download a single model using the gamslib command.

    Args:
        model: ModelEntry to download
        target_dir: Directory to extract the model to

    Returns:
        Tuple of (success, error_message). Success is True if the model was
        downloaded successfully. The caller should check file existence before
        calling this function if skip behavior is desired.
    """
    gms_file = target_dir / f"{model.model_id}.gms"

    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)

    # Run gamslib command to extract the model
    try:
        result = subprocess.run(
            ["gamslib", model.model_id],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
            return False, f"gamslib command failed: {error_msg}"

        # Verify the file was created
        if not gms_file.exists():
            # gamslib might create a file with different name, check for any .gms
            gms_files = list(target_dir.glob(f"{model.model_id}*.gms"))
            if gms_files:
                # Rename to expected name if needed
                if gms_files[0] != gms_file:
                    gms_files[0].rename(gms_file)
            else:
                return False, "gamslib completed but no .gms file created"

        return True, None

    except subprocess.TimeoutExpired:
        return False, "gamslib command timed out (60s)"
    except FileNotFoundError:
        return False, "gamslib command not found - is GAMS installed and on PATH?"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def update_model_status(
    model: ModelEntry,
    success: bool,
    target_dir: Path,
) -> None:
    """Update model entry with download result.

    Args:
        model: ModelEntry to update
        success: Whether download was successful
        target_dir: Directory where model was downloaded
    """
    if success:
        gms_file = target_dir / f"{model.model_id}.gms"
        model.download_status = "downloaded"
        model.download_date = get_utc_timestamp()
        # Store path relative to project root when possible
        try:
            model.file_path = str(gms_file.relative_to(PROJECT_ROOT))
        except ValueError:
            # Fallback to absolute path if not under PROJECT_ROOT
            model.file_path = str(gms_file)
        if gms_file.exists():
            model.file_size_bytes = gms_file.stat().st_size
        else:
            logger.warning(
                f"Expected file '{gms_file}' for model '{model.model_id}' to exist "
                "during status update, but it was missing."
            )
    else:
        model.download_status = "failed"
        model.download_date = get_utc_timestamp()


def download_models(
    catalog: GamslibCatalog,
    model_ids: list[str] | None = None,
    all_pending: bool = False,
    force: bool = False,
    dry_run: bool = False,
    batch_size: int = 10,
    verbose: bool = False,
) -> DownloadResult:
    """Download models from GAMSLIB.

    Args:
        catalog: GamslibCatalog instance
        model_ids: Specific model IDs to download (or None for --all)
        all_pending: If True, download all pending models
        force: If True, re-download even if files exist
        dry_run: If True, show what would be downloaded without downloading
        batch_size: Save catalog after every N downloads
        verbose: If True, show detailed progress

    Returns:
        DownloadResult with download statistics
    """
    result = DownloadResult()

    # Determine which models to download
    if model_ids:
        models_to_download = []
        for model_id in model_ids:
            model = catalog.get_model_by_id(model_id)
            if model is None:
                logger.warning(f"Model '{model_id}' not found in catalog")
            else:
                models_to_download.append(model)
    elif all_pending:
        if force:
            # Download all models (including already downloaded)
            models_to_download = catalog.models.copy()
        else:
            # Only pending models
            models_to_download = catalog.get_models_by_status("pending")
    else:
        logger.error("Must specify --model or --all")
        return result

    if not models_to_download:
        logger.info("No models to download")
        return result

    logger.info(f"Models to download: {len(models_to_download)}")

    if dry_run:
        logger.info("[DRY RUN] Would download the following models:")
        for model in models_to_download:
            status = "FORCE" if force else model.download_status
            logger.info(f"  - {model.model_id} ({model.gamslib_type}) [{status}]")
        return result

    # Download each model
    downloads_since_save = 0
    for i, model in enumerate(models_to_download, 1):
        # Check if we should skip (already downloaded and not forcing)
        gms_file = RAW_DIR / f"{model.model_id}.gms"
        if gms_file.exists() and not force:
            if verbose:
                logger.info(
                    f"[{i}/{len(models_to_download)}] Skipping {model.model_id} (already exists)"
                )
            result.add_skip()
            # Ensure catalog reflects that the file is already present on disk
            update_model_status(model, success=True, target_dir=RAW_DIR)
            downloads_since_save += 1
            # Save catalog periodically even when skipping existing files
            if downloads_since_save >= batch_size:
                saved_count = downloads_since_save
                catalog.save(CATALOG_PATH)
                downloads_since_save = 0
                if verbose:
                    logger.info(f"Catalog saved (batch checkpoint after {saved_count} updates)")
            continue

        # Download the model
        if verbose:
            logger.info(f"[{i}/{len(models_to_download)}] Downloading {model.model_id}...")
        else:
            # Progress every 10 models
            if i % 10 == 0 or i == len(models_to_download):
                logger.info(f"Progress: {i}/{len(models_to_download)} models processed")

        success, error = download_model(model, RAW_DIR)

        if success:
            result.add_success()
            update_model_status(model, success=True, target_dir=RAW_DIR)
            downloads_since_save += 1
        else:
            result.add_failure(model.model_id, error or "Unknown error")
            update_model_status(model, success=False, target_dir=RAW_DIR)
            logger.error(f"Failed to download {model.model_id}: {error}")
            downloads_since_save += 1

        # Save catalog periodically
        if downloads_since_save >= batch_size:
            saved_count = downloads_since_save
            catalog.save(CATALOG_PATH)
            downloads_since_save = 0
            if verbose:
                logger.info(f"Catalog saved (batch checkpoint after {saved_count} downloads)")

    # Final save
    if downloads_since_save > 0:
        catalog.save(CATALOG_PATH)

    return result


def write_error_log(result: DownloadResult) -> None:
    """Write download errors to a log file."""
    if not result.errors:
        return

    with open(ERROR_LOG_PATH, "a") as f:
        f.write(f"\n--- Download Errors {get_utc_timestamp()} ---\n")
        for model_id, error in result.errors:
            f.write(f"{model_id}: {error}\n")

    logger.info(f"Error log written to {ERROR_LOG_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download GAMSLIB models to local filesystem",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Download all pending models
    python scripts/gamslib/download_models.py --all

    # Download a specific model
    python scripts/gamslib/download_models.py --model trnsport

    # Force re-download of all models
    python scripts/gamslib/download_models.py --all --force

    # Preview what would be downloaded
    python scripts/gamslib/download_models.py --all --dry-run
        """,
    )
    parser.add_argument(
        "--model",
        "-m",
        action="append",
        dest="models",
        metavar="MODEL_ID",
        help="Download specific model(s) by ID (can be repeated)",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        dest="all_pending",
        help="Download all pending models from catalog",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Re-download even if file already exists",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be downloaded without downloading",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress information",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        metavar="N",
        help="Save catalog after every N downloads (default: 10)",
    )
    args = parser.parse_args()

    # Validate arguments
    if not args.models and not args.all_pending:
        parser.error("Must specify --model MODEL_ID or --all")

    if args.batch_size < 1:
        parser.error("--batch-size must be a positive integer")

    # Load catalog
    if not CATALOG_PATH.exists():
        logger.error(f"Catalog not found at {CATALOG_PATH}")
        logger.error("Run discover_models.py first to populate the catalog")
        sys.exit(1)

    catalog = GamslibCatalog.load(CATALOG_PATH)
    logger.info(f"Loaded catalog with {catalog.total_models} models")

    # Count current status
    pending = len(catalog.get_models_by_status("pending"))
    downloaded = len(catalog.get_models_by_status("downloaded"))
    failed = len(catalog.get_models_by_status("failed"))
    logger.info(f"Status: {pending} pending, {downloaded} downloaded, {failed} failed")

    # Perform downloads
    result = download_models(
        catalog=catalog,
        model_ids=args.models,
        all_pending=args.all_pending,
        force=args.force,
        dry_run=args.dry_run,
        batch_size=args.batch_size,
        verbose=args.verbose,
    )

    # Print summary
    if not args.dry_run:
        logger.info("=" * 50)
        logger.info("Download Summary:")
        logger.info(f"  Total attempted: {result.total_attempted}")
        logger.info(f"  Successful: {result.successful}")
        logger.info(f"  Skipped (existing): {result.skipped}")
        logger.info(f"  Failed: {result.failed}")

        if result.errors:
            write_error_log(result)
            logger.warning(f"  {len(result.errors)} errors logged to {ERROR_LOG_PATH}")

        # Final status
        pending = len(catalog.get_models_by_status("pending"))
        downloaded = len(catalog.get_models_by_status("downloaded"))
        failed = len(catalog.get_models_by_status("failed"))
        logger.info(f"Final status: {pending} pending, {downloaded} downloaded, {failed} failed")

        if result.failed > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
