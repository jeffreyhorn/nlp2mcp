#!/bin/bash
#
# Sprint 10 Mid-Sprint Checkpoint Script
#
# This script validates Sprint 10 progress at the Day 5 checkpoint.
# It measures the current parse rate and compares it to projections
# to determine if the sprint is on track.
#
# Usage:
#   ./scripts/sprint10_checkpoint.sh
#
# Exit codes:
#   0: On track or ahead of schedule
#   1: Behind schedule (action required)

set -euo pipefail

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Sprint 10 metrics
BASELINE_RATE=60        # Starting parse rate (6/10 models)
BASELINE_COUNT=6
TARGET_RATE=90          # Sprint 10 goal (9/10 models - defer maxmin.gms)
TARGET_COUNT=9
DAY5_MINIMUM_RATE=70    # Minimum expected by Day 5 (7/10 models)
DAY5_MINIMUM_COUNT=7
TOTAL_MODELS=10

echo "=========================================="
echo "Sprint 10 Day 5 Checkpoint"
echo "=========================================="
echo ""

# Display baseline and targets
echo -e "${BLUE}Baseline (Day 0):${NC} ${BASELINE_COUNT}/${TOTAL_MODELS} models (${BASELINE_RATE}%)"
echo -e "${BLUE}Day 5 Target:${NC}     ${DAY5_MINIMUM_COUNT}/${TOTAL_MODELS} models (${DAY5_MINIMUM_RATE}%)"
echo -e "${BLUE}Sprint Goal:${NC}      ${TARGET_COUNT}/${TOTAL_MODELS} models (${TARGET_RATE}%)"
echo ""

# Run parse rate measurement
echo "Measuring current parse rate..."
echo ""

# Capture both stdout and exit code
set +e
OUTPUT=$(python scripts/measure_parse_rate.py --verbose 2>&1)
PARSE_EXIT_CODE=$?
set -e

echo "$OUTPUT"
echo ""

# Extract parse rate from output
# Format: "Parse Rate: X/10 models (Y.Y%)"
set +e
CURRENT_COUNT=$(echo "$OUTPUT" | grep "Parse Rate:" | sed -E 's/.*Parse Rate: ([0-9]+)\/[0-9]+ models.*/\1/')
CURRENT_RATE=$(echo "$OUTPUT" | grep "Parse Rate:" | sed -E 's/.*\(([0-9.]+)%\).*/\1/' | cut -d'.' -f1)
set -e

if [ -z "$CURRENT_COUNT" ] || [ -z "$CURRENT_RATE" ]; then
    echo -e "${RED}❌ ERROR: Could not parse output from measure_parse_rate.py (exit code: ${PARSE_EXIT_CODE})${NC}"
    exit 1
fi

# Display current status
echo "=========================================="
echo "Checkpoint Results"
echo "=========================================="
echo ""
echo -e "Current parse rate: ${CURRENT_COUNT}/${TOTAL_MODELS} models (${CURRENT_RATE}%)"
echo ""

# Compare to Day 5 minimum
if [ "$CURRENT_COUNT" -ge "$DAY5_MINIMUM_COUNT" ]; then
    echo -e "${GREEN}✅ STATUS: ON TRACK${NC}"
    echo ""
    echo "Parse rate meets or exceeds Day 5 minimum target."
    echo ""

    if [ "$CURRENT_COUNT" -ge "$TARGET_COUNT" ]; then
        echo -e "${GREEN}🎉 AHEAD OF SCHEDULE!${NC}"
        echo "Sprint 10 goal already achieved! Consider:"
        echo "  - Tackling stretch goal (maxmin.gms)"
        echo "  - Starting Sprint 11 prep early"
        echo "  - Extra testing and documentation"
    else
        MODELS_REMAINING=$((TARGET_COUNT - CURRENT_COUNT))
        echo "Next steps:"
        echo "  - Continue implementing planned features"
        echo "  - ${MODELS_REMAINING} more model(s) needed to reach sprint goal"
        echo "  - Stay on current trajectory"
    fi

    exit 0
else
    echo -e "${RED}⚠️  STATUS: BEHIND SCHEDULE${NC}"
    echo ""
    MODELS_SHORT=$((DAY5_MINIMUM_COUNT - CURRENT_COUNT))
    echo "Parse rate is ${MODELS_SHORT} model(s) behind Day 5 projection."
    echo ""
    echo -e "${YELLOW}ACTION REQUIRED:${NC}"
    echo ""
    echo "1. Review failure analysis:"
    echo "   - Which models are failing?"
    echo "   - Are failures due to planned features or unexpected issues?"
    echo ""
    echo "2. Assess root causes:"
    echo "   - Implementation bugs in planned features?"
    echo "   - Unexpected blockers discovered?"
    echo "   - Estimation errors in feature complexity?"
    echo ""
    echo "3. Decide on strategy:"
    echo ""
    echo "   Option A: Debug and fix current features"
    echo "   - If failures are due to bugs in implemented features"
    echo "   - Estimate time to fix vs. remaining sprint days"
    echo ""
    echo "   Option B: Pivot to different models"
    echo "   - If current blockers are more complex than estimated"
    echo "   - Identify easier wins among remaining models"
    echo "   - Update sprint plan to target different models"
    echo ""
    echo "   Option C: Reduce scope"
    echo "   - If remaining time is insufficient"
    echo "   - Defer some models to Sprint 11"
    echo "   - Focus on achievable subset"
    echo ""
    echo "4. Update sprint plan:"
    echo "   - Document decision in sprint retrospective"
    echo "   - Adjust Day 10 targets if needed"
    echo "   - Communicate scope changes"
    echo ""
    echo "See docs/planning/EPIC_2/SPRINT_10/CHECKPOINT.md for details."
    echo ""

    exit 1
fi
