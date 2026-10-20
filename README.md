<p align="center">
  <img src="docs/DTAtoCSV-preview.png?v=1.0.1" width="128" height="128" alt="DTA → CSV app icon">
</p>

<h1 align="center">DTA → CSV</h1>

<p align="center">
  Turn Stata datasets into CSV files with a simple drag and drop.<br>
  A native macOS app. No Stata or Python installation required.
</p>

<p align="center">
  <a href="https://github.com/sunfhs/dta-to-csv-mac/releases/latest"><img src="https://img.shields.io/github/v/release/sunfhs/dta-to-csv-mac?style=flat-square&amp;label=release" alt="Latest release"></a>
  <img src="https://img.shields.io/badge/macOS-12%2B-222222?style=flat-square" alt="macOS 12 or later">
  <img src="https://img.shields.io/badge/Apple_Silicon-arm64-007AFF?style=flat-square" alt="Apple Silicon">
</p>

<p align="center">
  <strong><a href="https://github.com/sunfhs/dta-to-csv-mac/releases/latest/download/DTA-to-CSV-AppleSilicon.zip">Download for Mac · Apple Silicon</a></strong>
</p>

---

## From dataset to spreadsheet

- **Drop files or folders.** Convert one dataset or a whole folder, including subfolders.
- **Follow the progress.** See which file is being converted in the app window.
- **Keep everything local.** Conversion happens on your Mac, without uploading your data.
- **Open the results.** The output location opens in Finder when conversion finishes.

## Get started

1. [Download the latest release](https://github.com/sunfhs/dta-to-csv-mac/releases/latest/download/DTA-to-CSV-AppleSilicon.zip) and unzip it.
2. Move **DTA → CSV.app** to **Applications**, then open it.
3. Drop `.dta` files or folders into the window, or click **Choose Files…**.

| What you drop | Where the CSV files go |
| --- | --- |
| A `.dta` file | Next to the original file, with a `.csv` extension |
| A folder | A sibling folder named `<original>_CSV`, preserving subfolders |

> Existing CSV files at the same output paths are replaced. Keep a copy if you need them.

CSV files use UTF-8 with a BOM for spreadsheet compatibility. Stata value labels are exported as their underlying values.

<details>
<summary><strong>First launch: macOS security warning</strong></summary>

The app is locally signed and has not been notarized by Apple. macOS may block the first launch.

1. Dismiss the warning with **Done**.
2. Open **System Settings → Privacy & Security**.
3. Under **Security**, click **Open Anyway** and confirm.

Requires **macOS 12 or later** on an **Apple Silicon Mac**. An Intel build is not currently provided.

</details>

## Build from source

Requires Python 3.10+, the Xcode Command Line Tools, and an Apple Silicon Mac.

```bash
git clone https://github.com/sunfhs/dta-to-csv-mac.git
cd dta-to-csv-mac
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 self_check.py
python3 progress_check.py
./build_release.sh
```

The build includes the converter, generates the app icon from `docs/DTAtoCSV-preview.png`, and checks the bundle and archive. The release is written to `dist/DTA-to-CSV-AppleSilicon.zip`.
