#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

python3 -m PyInstaller DTAtoCSVCore.spec --clean
python3 make_icon.py

SDK="$(xcrun --sdk macosx --show-sdk-path)"
swiftc -sdk "$SDK" -target arm64-apple-macos12.0 DTAtoCSVApp.swift -o build/DTAtoCSV -framework AppKit

APP="dist/DTA → CSV.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp Info.plist "$APP/Contents/Info.plist"
cp build/DTAtoCSV "$APP/Contents/MacOS/DTAtoCSV"
cp dist/DTAtoCSVCore "$APP/Contents/Resources/DTAtoCSVCore"
cp build/DTAtoCSV.icns "$APP/Contents/Resources/DTAtoCSV.icns"

codesign --force --deep --sign - "$APP"

rm -f dist/DTA-to-CSV-AppleSilicon.zip
python3 -m zipfile -c dist/DTA-to-CSV-AppleSilicon.zip "$APP"

python3 app_check.py "$APP"
python3 package_check.py "$APP" "dist/DTA-to-CSV-AppleSilicon.zip"
