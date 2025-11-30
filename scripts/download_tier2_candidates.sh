#!/bin/bash
# Download Tier 2 candidate models for Sprint 12 Prep Task 3
#
# Usage:
#   ./scripts/download_tier2_candidates.sh
#
# Models are downloaded from GAMS Model Library and stored in tests/fixtures/tier2_candidates/

set -euo pipefail

# Configuration
GAMSLIB_VERSION="latest"
GAMSLIB_BASE_URL="https://www.gams.com/${GAMSLIB_VERSION}/gamslib_ml"
TARGET_DIR="tests/fixtures/tier2_candidates"
LOG_FILE="${TARGET_DIR}/download.log"

# Tier 2 candidate models (18 models for evaluation)
# Format: "name:seq:description"
declare -a TIER2_CANDIDATES=(
    "process:20:Alkylation Process Optimization"
    "chem:21:Chemical Equilibrium Problem"
    "least:24:Nonlinear Regression Problem"
    "like:25:Maximum Likelihood Estimation"
    "chenery:33:Substitution and Structural Change"
    "water:68:Design of a Water Distribution Network"
    "house:99:House Plan Design"
    "bearing:202:Hydrostatic Thrust Bearing Design"
    "haverly:214:Haverly's pooling problem"
    "gastrans:217:Gas Transmission Problem - Belgium"
    "polygon:229:Largest small polygon COPS 2.0"
    "elec:230:Distribution of electrons on a sphere"
    "chain:231:Hanging Chain COPS 2.0"
    "gasoil:240:Catalytic cracking of gas oil"
    "jbearing:244:Journal bearing COPS 2.0"
    "pool:254:Pooling problem"
    "fct:265:LGO Interface Example"
    "inscribedsquare:425:Inscribed Square Problem"
)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Downloading ${#TIER2_CANDIDATES[@]} Tier 2 candidate models...${NC}"

# Create target directory
mkdir -p "$TARGET_DIR"
echo "timestamp,model,status" > "$LOG_FILE"

# Download each model
for model_entry in "${TIER2_CANDIDATES[@]}"; do
    IFS=: read -r name seq description <<< "$model_entry"

    gms_file="${TARGET_DIR}/${name}.gms"
    download_url="${GAMSLIB_BASE_URL}/${name}.${seq}"

    echo "Downloading: ${name} (seq ${seq})..."

    if curl -f -s -S -o "$gms_file" "$download_url" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} ${name}"
        echo "$(date -u +%Y-%m-%dT%H:%M:%SZ),${name},SUCCESS" >> "$LOG_FILE"
    else
        echo "✗ ${name} (download failed)"
        echo "$(date -u +%Y-%m-%dT%H:%M:%SZ),${name},FAILED" >> "$LOG_FILE"
    fi
done

echo -e "${GREEN}Download complete!${NC} Files in: ${TARGET_DIR}"
