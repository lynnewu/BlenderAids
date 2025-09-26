# BlenderAids
BlendAids - various resources like layout maps, etc. 

# make_grid.py

A Python script to generate **pixel-perfect ruler / UV test grids** for Blender, printing, or general reference.  
It supports **PNG (raster), SVG, and PDF (vector)** output with customizable colors, labels, and alignment.

---

## Features

- **Customizable grid geometry**
  - Major squares (`--major`, default `10`)
  - Minor subdivisions (`--minor`, default `12`)
  - Image size in pixels (`--size`, default `3600`)

- **Colors**
  - Colored major squares (`--color`, default)
  - White/black print-friendly mode (`--no-color`)

- **Labels**
  - Spreadsheet-style labels (`A1..Z99, AA1..`)  
  - Configurable alignment (`--label-alignment UpperLeft|MiddleCenter|...`)  
  - Label scale (`--label-scale 0.20` means 20% of major square height)  
  - Automatic black/white text for legibility over colored backgrounds  

- **Opacity**
  - Control transparency of both fills and labels with `--opacity 0.0–1.0`

- **Output**
  - Raster: PNG (snaps to nearest multiple of `major * minor` for perfect pixel alignment)
  - Vector: SVG, PDF (infinite scalability, no snapping required)
  - Multiple formats at once: `--format png svg pdf`
  - Auto-descriptive filenames (unless `--out` specified)
  - **Windows-safe auto-suffixing**: if file exists, new ones become `...-000.png`, `...-001.png`, etc.

---

## Installation

Requires Python 3.9+ and `matplotlib`.

```bash
pip install -r requirements.txt
