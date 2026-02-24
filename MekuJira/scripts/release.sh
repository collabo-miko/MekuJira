#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TAURI_CONF="$PROJECT_DIR/src-tauri/tauri.conf.json"

# バージョン読み取り
VERSION=$(grep -o '"version": *"[^"]*"' "$TAURI_CONF" | head -1 | sed 's/.*"\([^"]*\)"/\1/')
if [ -z "$VERSION" ]; then
  echo "ERROR: tauri.conf.json からバージョンを読み取れませんでした"
  exit 1
fi
echo "==> Version: $VERSION"

# 署名鍵チェック
if [ -z "${TAURI_SIGNING_PRIVATE_KEY:-}" ]; then
  echo "ERROR: TAURI_SIGNING_PRIVATE_KEY が設定されていません"
  echo ""
  echo "  鍵を生成するには:"
  echo "    npx tauri signer generate -w ~/.tauri/mekujira.key"
  echo ""
  echo "  環境変数を設定するには:"
  echo "    export TAURI_SIGNING_PRIVATE_KEY=\$(cat ~/.tauri/mekujira.key)"
  echo "    export TAURI_SIGNING_PRIVATE_KEY_PASSWORD='your-password'"
  exit 1
fi

# ビルド実行
echo "==> Building MekuJira v$VERSION ..."
cd "$PROJECT_DIR"
npm run tauri build

# ビルド成果物の場所を特定
BUNDLE_DIR="$PROJECT_DIR/src-tauri/target/release/bundle"
DMG=$(find "$BUNDLE_DIR/dmg" -name "*.dmg" 2>/dev/null | head -1)
TAR_GZ=$(find "$BUNDLE_DIR/macos" -name "*.tar.gz" 2>/dev/null | head -1)
SIG=$(find "$BUNDLE_DIR/macos" -name "*.tar.gz.sig" 2>/dev/null | head -1)

if [ -z "$TAR_GZ" ] || [ -z "$SIG" ]; then
  echo "ERROR: ビルド成果物が見つかりませんでした"
  echo "  .tar.gz: $TAR_GZ"
  echo "  .sig: $SIG"
  exit 1
fi

# 署名を読み取り
SIGNATURE=$(cat "$SIG")

# latest.json 生成
REPO="collabo-miko/MekuJira"
TAR_GZ_FILENAME=$(basename "$TAR_GZ")
PUB_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

LATEST_JSON="$BUNDLE_DIR/latest.json"
cat > "$LATEST_JSON" <<EOF
{
  "version": "$VERSION",
  "notes": "Release v$VERSION",
  "pub_date": "$PUB_DATE",
  "platforms": {
    "darwin-aarch64": {
      "url": "https://github.com/$REPO/releases/download/v$VERSION/$TAR_GZ_FILENAME",
      "signature": "$SIGNATURE"
    }
  }
}
EOF

echo ""
echo "==> Build complete!"
echo ""
echo "==> Upload files:"
[ -n "$DMG" ] && echo "  DMG:         $DMG"
echo "  tar.gz:      $TAR_GZ"
echo "  sig:         $SIG"
echo "  latest.json: $LATEST_JSON"
echo ""

# GitHub Releases にアップロード
read -p "==> GitHub Releases に v$VERSION を作成してアップロードしますか？ [y/N] " CONFIRM
if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
  if ! command -v gh &> /dev/null; then
    echo "ERROR: gh (GitHub CLI) がインストールされていません"
    echo "  brew install gh && gh auth login"
    exit 1
  fi

  cd "$PROJECT_DIR/.."
  git tag "v$VERSION" && git push --tags

  UPLOAD_FILES=("$TAR_GZ" "$SIG" "$LATEST_JSON")
  [ -n "$DMG" ] && UPLOAD_FILES+=("$DMG")

  gh release create "v$VERSION" "${UPLOAD_FILES[@]}" \
    --title "v$VERSION" \
    --notes "Release v$VERSION"

  echo ""
  echo "==> v$VERSION を GitHub Releases にアップロードしました！"
else
  echo "==> スキップしました。手動でアップロードする場合:"
  echo "  1. git tag v$VERSION && git push --tags"
  echo "  2. gh release create v$VERSION \\"
  [ -n "$DMG" ] && echo "       $DMG \\"
  echo "       $TAR_GZ \\"
  echo "       $SIG \\"
  echo "       $LATEST_JSON \\"
  echo "       --title \"v$VERSION\" --notes \"Release v$VERSION\""
fi
