#!/bin/bash

# Script to create a clean zip of the notification system project
# Excludes built files, dependencies, cache, and temporary files

PROJECT_NAME="notification-system"
ZIP_NAME="${PROJECT_NAME}-source-$(date +%Y%m%d-%H%M%S).zip"

echo "Creating clean zip archive: $ZIP_NAME"
echo "Excluding built files, dependencies, and temporary files..."

# Create zip excluding common build/cache/dependency directories and files
zip -r "$ZIP_NAME" . \
  -x "*.git*" \
  -x "*node_modules*" \
  -x "*__pycache__*" \
  -x "*.pyc" \
  -x "*build/*" \
  -x "*dist/*" \
  -x "*.DS_Store*" \
  -x "*package-lock.json" \
  -x "*yarn.lock" \
  -x "*.log" \
  -x "*tmp/*" \
  -x "*temp/*" \
  -x "*.env.local" \
  -x "*.env.production" \
  -x "*coverage/*" \
  -x "*.nyc_output*" \
  -x "*test_env/*" \
  -x "*/venv/*" \
  -x "*/env/*" \
  -x "*.egg-info*" \
  -x "*pytest_cache*" \
  -x "*.tox*" \
  -x "*thumbs.db" \
  -x "*.swp" \
  -x "*.swo" \
  -x "*~" \
  -x "*.bak" \
  -x "*.orig"

if [ $? -eq 0 ]; then
    echo "✅ Successfully created: $ZIP_NAME"
    echo "📦 Archive size: $(du -h "$ZIP_NAME" | cut -f1)"
    echo ""
    echo "📋 Contents included:"
    echo "   • Source code (all .js, .py, .html, .css files)"
    echo "   • Configuration files (package.json, requirements.txt, etc.)"
    echo "   • Documentation (README.md, CHANGELOG.md, etc.)"
    echo "   • Docker configuration"
    echo "   • Shell scripts"
    echo ""
    echo "🚫 Excluded:"
    echo "   • Git history (.git/)"
    echo "   • Node modules (node_modules/)"
    echo "   • Python cache (__pycache__/, *.pyc)"
    echo "   • Virtual environments (test_env/, venv/, env/)"
    echo "   • Build artifacts (build/, dist/)"
    echo "   • Lock files (package-lock.json, yarn.lock)"
    echo "   • Log files (*.log)"
    echo "   • OS files (.DS_Store, thumbs.db)"
    echo "   • Editor files (*.swp, *.swo, *~)"
else
    echo "❌ Failed to create zip archive"
    exit 1
fi
