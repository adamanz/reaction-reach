#!/bin/bash

# ReactionReach Exa Intelligence Enhancement Runner
# Usage: ./run_exa_enrichment.sh [EXA_API_KEY]

echo "🚀 ReactionReach Exa Intelligence Enhancement"
echo "============================================="

# Check if API key provided as argument
if [ ! -z "$1" ]; then
    export EXA_API_KEY="$1"
    echo "✅ Using provided API key"
elif [ ! -z "$EXA_API_KEY" ]; then
    echo "✅ Using environment API key"
else
    echo "❌ No Exa API key provided!"
    echo ""
    echo "Usage options:"
    echo "  1. Pass as argument: ./run_exa_enrichment.sh YOUR_API_KEY"
    echo "  2. Set environment: export EXA_API_KEY='YOUR_API_KEY' && ./run_exa_enrichment.sh"
    echo ""
    echo "Get your API key at: https://dashboard.exa.ai/api"
    exit 1
fi

# Verify Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Please install Node.js first."
    exit 1
fi

# Verify exa-js is installed
if [ ! -d "node_modules/exa-js" ]; then
    echo "📦 Installing exa-js dependency..."
    npm install exa-js
fi

echo "🔍 Starting Exa intelligence enrichment..."
echo ""

# Run the enrichment script
node exa_enrichment.js

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "🎉 Enrichment completed successfully!"
    echo "📁 Check the ReactionReach directory for:"
    echo "   - exa_enrichment_results_*.json (raw data)"
    echo "   - *_exa_enhanced.md (enhanced report)"
else
    echo ""
    echo "❌ Enrichment failed with exit code: $exit_code"
    exit $exit_code
fi