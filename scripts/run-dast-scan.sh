#!/bin/bash
# =============================================================================
# DAST Security Scan Trigger Script
# =============================================================================
# To trigger DAST scans from command line using GitHub CLI
#
# Prerequisites:
#   - GitHub CLI installed: brew install gh
#   - Authenticated: gh auth login
#
# Usage:
#   ./run-dast-scan.sh                    # Interactive mode
#   ./run-dast-scan.sh baseline staging   # Quick baseline scan on staging
#   ./run-dast-scan.sh full production    # Full scan on production
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
REPO="WSO2-G02/salon-booking-backend-dev"
WORKFLOW="security-dast.yml"

# Domain mapping
STAGING_URL="https://staging.aurora-glam.com"
PRODUCTION_URL="https://aurora-glam.com"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   DAST Security Scan Trigger${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install with: brew install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Parse arguments or interactive mode
if [ $# -ge 2 ]; then
    SCAN_TYPE=$1
    ENVIRONMENT=$2
else
    # Interactive mode
    echo -e "${YELLOW}Select scan type:${NC}"
    echo "  1) baseline - Quick passive scan (1-2 min)"
    echo "  2) api      - API/OpenAPI scan"
    echo "  3) full     - Deep active scan (15-30 min)"
    read -p "Enter choice [1-3]: " SCAN_CHOICE
    
    case $SCAN_CHOICE in
        1) SCAN_TYPE="baseline" ;;
        2) SCAN_TYPE="api" ;;
        3) SCAN_TYPE="full" ;;
        *) echo -e "${RED}Invalid choice${NC}"; exit 1 ;;
    esac
    
    echo ""
    echo -e "${YELLOW}Select environment:${NC}"
    echo "  1) staging    - $STAGING_URL"
    echo "  2) production - $PRODUCTION_URL"
    read -p "Enter choice [1-2]: " ENV_CHOICE
    
    case $ENV_CHOICE in
        1) ENVIRONMENT="staging" ;;
        2) ENVIRONMENT="production" ;;
        *) echo -e "${RED}Invalid choice${NC}"; exit 1 ;;
    esac
fi

# Set URL based on environment
if [ "$ENVIRONMENT" == "staging" ]; then
    TARGET_URL="$STAGING_URL"
elif [ "$ENVIRONMENT" == "production" ]; then
    TARGET_URL="$PRODUCTION_URL"
else
    echo -e "${RED}Invalid environment: $ENVIRONMENT${NC}"
    exit 1
fi

# Validate scan type
if [[ ! "$SCAN_TYPE" =~ ^(baseline|api|full)$ ]]; then
    echo -e "${RED}Invalid scan type: $SCAN_TYPE${NC}"
    echo "Valid types: baseline, api, full"
    exit 1
fi

echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Scan Type:   $SCAN_TYPE"
echo "  Environment: $ENVIRONMENT"
echo "  Target URL:  $TARGET_URL"
echo ""

# Confirm for production full scan
if [ "$ENVIRONMENT" == "production" ] && [ "$SCAN_TYPE" == "full" ]; then
    echo -e "${RED}⚠️  WARNING: Full scan on production may trigger security alerts!${NC}"
    read -p "Are you sure? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi
fi

# Trigger the workflow
echo -e "${YELLOW}Triggering DAST scan...${NC}"
gh workflow run "$WORKFLOW" \
    --repo "$REPO" \
    -f target_url="$TARGET_URL" \
    -f scan_type="$SCAN_TYPE"

echo ""
echo -e "${GREEN}✅ DAST scan triggered successfully!${NC}"
echo ""
echo "View progress at:"
echo "  https://github.com/$REPO/actions/workflows/$WORKFLOW"
echo ""

# Option to watch
read -p "Watch workflow progress? (y/n): " WATCH
if [ "$WATCH" == "y" ]; then
    echo "Waiting for workflow to start..."
    sleep 5
    gh run watch --repo "$REPO"
fi
