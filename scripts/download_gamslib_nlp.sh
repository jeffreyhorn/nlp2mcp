#!/bin/bash
# Download GAMS Model Library NLP models for Sprint 6 testing
#
# Usage:
#   ./scripts/download_gamslib_nlp.sh           # Download all Tier 1 models
#   ./scripts/download_gamslib_nlp.sh --help    # Show help
#   ./scripts/download_gamslib_nlp.sh --clean   # Remove all downloaded files
#
# Models are downloaded from GAMS Model Library and stored in tests/fixtures/gamslib/

set -euo pipefail

# Configuration
# Using "latest" version since specific versions (like 47.6) may not be available
# GAMS updates their library structure, so "latest" is the most reliable
GAMSLIB_VERSION="latest"
GAMSLIB_BASE_URL="https://www.gams.com/${GAMSLIB_VERSION}/gamslib_ml"
TARGET_DIR="tests/fixtures/gamslib"
LOG_FILE="${TARGET_DIR}/download.log"
MANIFEST_FILE="${TARGET_DIR}/manifest.csv"

# Tier 1 models (from GAMSLIB_NLP_CATALOG.md - Sprint 6 target set)
# Format: "name:seq:description"
# seq = sequence number in GAMSLib (used in download URL)
declare -a TIER1_MODELS=(
    "trig:261:Simple Trigonometric Example"
    "rbrock:83:Rosenbrock Test Function"
    "himmel16:36:Area of Hexagon Test Problem"
    "hs62:264:Hock-Schittkowski Problem 62"
    "mhw4d:84:Nonlinear Test Problem"
    "mhw4dx:267:MHW4D with Additional Tests"
    "circle:201:Circle Enclosing Points - SNOPT Example"
    "maxmin:263:Max Min Location of Points in Unit Square"
    "mathopt1:255:MathOptimizer Example 1"
    "mingamma:299:Minimal y of GAMMA(x)"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters for summary
TOTAL_MODELS=${#TIER1_MODELS[@]}
SUCCESS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to show help
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Download GAMS Model Library NLP models for Sprint 6 testing.

OPTIONS:
    --help          Show this help message
    --clean         Remove all downloaded files and logs
    --dry-run       Show what would be downloaded without downloading
    --force         Force re-download even if files exist

DESCRIPTION:
    Downloads Tier 1 NLP models from GAMS Model Library (10 models).
    Models are stored in: ${TARGET_DIR}

    Downloaded files:
    - <model>.gms       GAMS source file
    - manifest.csv      Download manifest with metadata
    - download.log      Download log with timestamps

EXAMPLES:
    # Download all Tier 1 models
    $0

    # See what would be downloaded
    $0 --dry-run

    # Force re-download all models
    $0 --force

    # Clean up downloaded files
    $0 --clean

EOF
}

# Function to clean downloaded files
clean_downloads() {
    print_info "Cleaning downloaded files..."
    if [ -d "$TARGET_DIR" ]; then
        # Remove .gms files, manifest, and log, but keep README.md
        find "$TARGET_DIR" -type f -name "*.gms" -delete
        rm -f "$LOG_FILE" "$MANIFEST_FILE"
        print_success "Cleaned downloaded files (kept README.md)"
    else
        print_info "No files to clean (directory doesn't exist)"
    fi
}

# Function to validate .gms file format
validate_gms_file() {
    local file="$1"

    # Check if file exists and is not empty
    if [ ! -f "$file" ] || [ ! -s "$file" ]; then
        return 1
    fi

    # Check if file contains GAMS keywords (basic validation)
    # Look for at least one of: Variable, Equation, Model, Solve
    if grep -qi -E '\b(Variable|Equation|Model|Solve)\b' "$file"; then
        return 0
    else
        return 1
    fi
}

# Function to download a single model with retry logic
download_model() {
    local model_name="$1"
    local seq_num="$2"
    local description="$3"
    local force_download="${4:-false}"

    local gms_file="${TARGET_DIR}/${model_name}.gms"

    # GAMS library uses sequence numbers for file downloads
    # Format: https://www.gams.com/latest/gamslib_ml/modelname.seqnum
    local gms_download_url="${GAMSLIB_BASE_URL}/${model_name}.${seq_num}"

    print_info "Downloading: ${model_name} (seq ${seq_num}) - ${description}"

    # Check if file already exists and skip if not forcing
    if [ "$force_download" = false ] && [ -f "$gms_file" ]; then
        if validate_gms_file "$gms_file"; then
            print_warning "Already exists (use --force to re-download): ${model_name}"
            echo "$(date -u +%Y-%m-%dT%H:%M:%SZ),${model_name},SKIPPED,Already exists,0" >> "$LOG_FILE"
            ((SKIP_COUNT++))
            return 0
        else
            print_warning "Existing file is invalid, re-downloading: ${model_name}"
        fi
    fi

    # Download .gms file with retry logic
    local max_retries=3
    local retry_count=0
    local download_success=false
    local start_time=$(date +%s)

    while [ $retry_count -lt $max_retries ]; do
        if curl -f -s -S -o "$gms_file" "$gms_download_url" 2>/dev/null; then
            # Validate downloaded file
            if validate_gms_file "$gms_file"; then
                download_success=true
                break
            else
                print_error "Invalid .gms file format: ${model_name} (attempt $((retry_count + 1))/$max_retries)"
                rm -f "$gms_file"
            fi
        else
            print_error "Download failed: ${model_name} (attempt $((retry_count + 1))/$max_retries)"
        fi

        ((retry_count++))
        if [ $retry_count -lt $max_retries ]; then
            sleep 2  # Wait before retry
        fi
    done

    if [ "$download_success" = false ]; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_error "Failed to download after $max_retries attempts: ${model_name}"
        echo "$(date -u +%Y-%m-%dT%H:%M:%SZ),${model_name},FAILED,Download failed after $max_retries attempts,$duration" >> "$LOG_FILE"
        ((FAIL_COUNT++))
        return 1
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    print_success "Downloaded: ${model_name} (${duration}s)"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ),${model_name},SUCCESS,Downloaded successfully,$duration" >> "$LOG_FILE"
    ((SUCCESS_COUNT++))

    return 0
}

# Main download function
download_all_models() {
    local force_download="${1:-false}"
    local dry_run="${2:-false}"

    print_info "=== GAMS Model Library Download Script ==="
    print_info "Version: ${GAMSLIB_VERSION}"
    print_info "Target directory: ${TARGET_DIR}"
    print_info "Models to download: ${TOTAL_MODELS} (Tier 1)"
    echo ""

    if [ "$dry_run" = true ]; then
        print_info "DRY RUN - No files will be downloaded"
        echo ""
    fi

    # Create target directory
    mkdir -p "$TARGET_DIR"

    # Initialize log file
    if [ "$dry_run" = false ]; then
        echo "timestamp,model,status,message,duration_seconds" > "$LOG_FILE"
        echo "# Download started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG_FILE"
    fi

    # Download each model
    local start_total=$(date +%s)

    for model_entry in "${TIER1_MODELS[@]}"; do
        IFS=: read -r name seq description <<< "$model_entry"

        if [ "$dry_run" = true ]; then
            print_info "[DRY RUN] Would download: ${name} (seq ${seq}) - ${description}"
        else
            download_model "$name" "$seq" "$description" "$force_download"
        fi
    done

    local end_total=$(date +%s)
    local total_duration=$((end_total - start_total))

    # Print summary
    echo ""
    print_info "=== Download Summary ==="
    print_info "Total models: ${TOTAL_MODELS}"

    if [ "$dry_run" = false ]; then
        print_success "Successfully downloaded: ${SUCCESS_COUNT}"
        if [ $SKIP_COUNT -gt 0 ]; then
            print_warning "Skipped (already exist): ${SKIP_COUNT}"
        fi
        if [ $FAIL_COUNT -gt 0 ]; then
            print_error "Failed: ${FAIL_COUNT}"
        fi
        print_info "Total time: ${total_duration}s"
        print_info "Log file: ${LOG_FILE}"

        # Create manifest
        create_manifest

        # Check if under time limit (5 minutes = 300 seconds)
        if [ $total_duration -lt 300 ]; then
            print_success "✓ Download completed within 5-minute target"
        else
            print_warning "⚠ Download took longer than 5-minute target"
        fi

        # Overall status
        if [ $FAIL_COUNT -eq 0 ]; then
            print_success "✓ All downloads completed successfully!"
            return 0
        else
            print_error "✗ Some downloads failed. Check ${LOG_FILE} for details."
            return 1
        fi
    fi
}

# Function to create manifest file
create_manifest() {
    print_info "Creating manifest..."

    echo "name,description,gms_file,gms_size_bytes,download_status" > "$MANIFEST_FILE"

    for model_entry in "${TIER1_MODELS[@]}"; do
        IFS=: read -r name seq description <<< "$model_entry"

        local gms_file="${TARGET_DIR}/${name}.gms"
        local gms_exists="false"
        local gms_size=0
        local status="NOT_DOWNLOADED"

        if [ -f "$gms_file" ]; then
            gms_exists="true"
            gms_size=$(stat -f%z "$gms_file" 2>/dev/null || stat -c%s "$gms_file" 2>/dev/null || echo "0")
            if validate_gms_file "$gms_file"; then
                status="SUCCESS"
            else
                status="INVALID"
            fi
        fi

        echo "${name},\"${description}\",${gms_exists},${gms_size},${status}" >> "$MANIFEST_FILE"
    done

    print_success "Manifest created: ${MANIFEST_FILE}"
}

# Parse command line arguments
FORCE_DOWNLOAD=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_help
            exit 0
            ;;
        --clean)
            clean_downloads
            exit 0
            ;;
        --force)
            FORCE_DOWNLOAD=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main download
download_all_models "$FORCE_DOWNLOAD" "$DRY_RUN"
