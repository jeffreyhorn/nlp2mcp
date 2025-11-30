#!/bin/bash
#
# update_baselines.sh - Update baseline files for regression testing
#
# Usage:
#   ./scripts/update_baselines.sh [OPTIONS]
#
# Options:
#   --simplification SPRINT     Update simplification baseline for specified sprint (e.g., sprint12)
#   --multi-metric SPRINT       Update multi-metric baseline for specified sprint (e.g., sprint12)
#   --all SPRINT                Update all baselines for specified sprint
#   --dry-run                   Show what would be updated without making changes
#   --help                      Show this help message
#
# Examples:
#   # Update simplification baseline for Sprint 12
#   ./scripts/update_baselines.sh --simplification sprint12
#
#   # Update multi-metric baseline for Sprint 12
#   ./scripts/update_baselines.sh --multi-metric sprint12
#
#   # Update all baselines for Sprint 12
#   ./scripts/update_baselines.sh --all sprint12
#
#   # Dry run to preview changes
#   ./scripts/update_baselines.sh --all sprint12 --dry-run
#
# Description:
#   This script updates baseline JSON files used for regression testing.
#
#   For simplification baselines:
#     - Runs simplification analysis on tier1 models
#     - Collects metrics: ops/terms before/after, reduction percentages, execution time
#     - Updates baselines/simplification/baseline_<sprint>.json
#     - Requires: pytest with simplification tests
#
#   For multi-metric baselines:
#     - Runs conversion on tier1 models
#     - Collects metrics: parse rate, convert rate, performance
#     - Updates baselines/multi_metric/baseline_<sprint>.json
#     - Requires: scripts/measure_parse_rate.py
#
# Prerequisites:
#   - Python environment with pytest, nlp2mcp package installed
#   - tier1 model set available
#   - Git repository (captures commit SHA in baseline metadata)
#
# Exit Codes:
#   0 - Success
#   1 - Invalid arguments or missing prerequisites
#   2 - Baseline collection failed
#   3 - File write failed
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Default options
DRY_RUN=false
UPDATE_SIMPLIFICATION=false
UPDATE_MULTI_METRIC=false
SPRINT=""

#
# Functions
#

show_help() {
    sed -n '2,/^$/p' "$0" | sed 's/^# \?//'
    exit 0
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

check_prerequisites() {
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        return 1
    fi

    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        log_error "python3 not found"
        return 1
    fi

    # Check if pytest is available (for simplification baselines)
    if [ "$UPDATE_SIMPLIFICATION" = true ] && ! python3 -m pytest --version &> /dev/null; then
        log_error "pytest not found (required for simplification baselines)"
        return 1
    fi

    # Check if measure_parse_rate.py exists (for multi-metric baselines)
    if [ "$UPDATE_MULTI_METRIC" = true ] && [ ! -f "${SCRIPT_DIR}/measure_parse_rate.py" ]; then
        log_error "measure_parse_rate.py not found (required for multi-metric baselines)"
        return 1
    fi

    return 0
}

update_simplification_baseline() {
    local sprint="$1"
    local output_file="${PROJECT_ROOT}/baselines/simplification/baseline_${sprint}.json"

    log_info "Updating simplification baseline for ${sprint}..."

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would update: ${output_file}"
        return 0
    fi

    # TODO: Implement simplification baseline collection
    # This will be implemented during Sprint 12 Day 2
    log_warn "Simplification baseline collection not yet implemented"
    log_warn "Placeholder: ${output_file}"

    return 0
}

update_multi_metric_baseline() {
    local sprint="$1"
    local output_file="${PROJECT_ROOT}/baselines/multi_metric/baseline_${sprint}.json"

    log_info "Updating multi-metric baseline for ${sprint}..."

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would update: ${output_file}"
        return 0
    fi

    # TODO: Implement multi-metric baseline collection
    # This will be implemented during Sprint 12 Day 6
    log_warn "Multi-metric baseline collection not yet implemented"
    log_warn "Placeholder: ${output_file}"

    return 0
}

#
# Main
#

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --simplification)
            if [ -z "${2:-}" ]; then
                log_error "Missing SPRINT argument for --simplification"
                exit 1
            fi
            UPDATE_SIMPLIFICATION=true
            SPRINT="$2"
            shift 2
            ;;
        --multi-metric)
            if [ -z "${2:-}" ]; then
                log_error "Missing SPRINT argument for --multi-metric"
                exit 1
            fi
            UPDATE_MULTI_METRIC=true
            SPRINT="$2"
            shift 2
            ;;
        --all)
            if [ -z "${2:-}" ]; then
                log_error "Missing SPRINT argument for --all"
                exit 1
            fi
            UPDATE_SIMPLIFICATION=true
            UPDATE_MULTI_METRIC=true
            SPRINT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate arguments
if [ -z "$SPRINT" ]; then
    log_error "Sprint not specified"
    echo "Use --help for usage information"
    exit 1
fi

if [ "$UPDATE_SIMPLIFICATION" = false ] && [ "$UPDATE_MULTI_METRIC" = false ]; then
    log_error "No baseline type specified (use --simplification, --multi-metric, or --all)"
    echo "Use --help for usage information"
    exit 1
fi

# Check prerequisites
if ! check_prerequisites; then
    exit 1
fi

# Update baselines
if [ "$UPDATE_SIMPLIFICATION" = true ]; then
    if ! update_simplification_baseline "$SPRINT"; then
        log_error "Failed to update simplification baseline"
        exit 2
    fi
fi

if [ "$UPDATE_MULTI_METRIC" = true ]; then
    if ! update_multi_metric_baseline "$SPRINT"; then
        log_error "Failed to update multi-metric baseline"
        exit 2
    fi
fi

log_info "Baseline update complete"
exit 0
