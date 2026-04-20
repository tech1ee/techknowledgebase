#!/bin/bash
# Update all DESIGN.md files from getdesign.md
# Run: bash ~/Documents/tech/500-craft/design-references/update.sh

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

BRANDS=(
  linear.app notion vercel stripe claude figma apple supabase
  spotify airbnb superhuman raycast cursor uber tesla framer
)

for brand in "${BRANDS[@]}"; do
  echo "Updating $brand..."
  npx getdesign@latest add "$brand" --out "./$brand/DESIGN.md" --force 2>&1
done

echo "Done. Updated ${#BRANDS[@]} DESIGN.md files."
