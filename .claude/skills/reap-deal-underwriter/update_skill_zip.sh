#!/bin/bash
# Rebuild reap-deal-underwriter-updated.zip for re-upload to claude.ai's
# Skills settings, after pulling any changes made in this repo.
set -e
cd "$(dirname "$0")/.."
rm -rf reap-deal-underwriter-updated.zip reap-deal-underwriter/scripts/__pycache__ reap-deal-underwriter/.cache
zip -r reap-deal-underwriter-updated.zip reap-deal-underwriter -x "*.pyc"
echo ""
echo "Ready to upload: $(pwd)/reap-deal-underwriter-updated.zip"
