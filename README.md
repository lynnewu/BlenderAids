# BlenderAids
BlendAids - various resources like layout maps, etc. for use in Blender (or other image editors where layout grids might be useful)

# make_grid.py

A Python script to generate pixel-perfect ruler / UV test grids for Blender, printing, or general reference.
It supports PNG (raster), SVG, and PDF (vector) output with customizable colors, labels, and alignment.

---

## Quick Start

1. Install dependencies:

    pip install -r requirements.txt

2. Run the script:

    python make_grid.py

   This generates:
   - grid_3600_major10_minor12_color_upperleft_scale0.2_opacity1-000.png

   A 3600×3600 colored PNG with 10×10 major squares, each subdivided 12×12, labels in the upper-left.

---

## Features

- Customizable grid geometry
  - Major squares (--major, default 10)
  - Minor subdivisions (--minor, default 12)
  - Image size in pixels (--size, default 3600)

- Colors
  - Colored major squares (--color, default)
  - White/black print-friendly mode (--no-color)

- Labels
  - Spreadsheet-style labels (A1..Z99, AA1..)
  - Configurable alignment (--label-alignment UpperLeft|MiddleCenter|...)
  - Label scale (--label-scale 0.20 means 20% of major square height)
  - Automatic black/white text for legibility over colored backgrounds

- Opacity
  - Control transparency of both fills and labels with --opacity 0.0–1.0

- Output
  - Raster: PNG (snaps to nearest multiple of major * minor for perfect pixel alignment)
  - Vector: SVG, PDF (infinite scalability, no snapping required)
  - Multiple formats at once: --format png svg pdf
  - Auto-descriptive filenames (unless --out specified)
  - Windows-safe auto-suffixing: if file exists, new ones become ...-000.png, ...-001.png, etc.

---

## Installation

Requires Python 3.9+ and matplotlib.

    pip install -r requirements.txt

Minimal requirements.txt:

    matplotlib>=3.7

---

## Usage

### Basic

    python make_grid.py

Generates a 3600×3600 PNG with 10×10 major squares, 12×12 subdivisions each, colored background, labels in upper-left.

### Common Options

- Custom size & formats:

      python make_grid.py --size 7200 --format png svg

- Print-friendly B/W vector PDF:

      python make_grid.py --no-color --format pdf

- Labels centered & smaller:

      python make_grid.py --label-alignment MiddleCenter --label-scale 0.18

- Semi-transparent overlay PNG:

      python make_grid.py --opacity 0.5

- Explicit output base name:

      python make_grid.py -o my_custom_grid --format png svg

  Produces files like: my_custom_grid-000.png, my_custom_grid-000.svg

---

## Examples

- grid_7200_major10_minor12_color_upperleft_scale0.2_opacity1-000.png
- grid_3600_major10_minor12_bw_middlecenter_scale0.18_opacity0.5-000.pdf

---

## Demo

Here are three common output styles:

![Demo Grids](https://github.com/lynnewu/BlenderAids/raw/main/make_grid_demo_fixed.png)

- Left: Colored PNG (default)
- Middle: B/W print-friendly PDF
- Right: Semi-transparent overlay (50% opacity)

---

## Advanced Usage

- Generate all three formats at once:

      python make_grid.py --size 6000 --format png svg pdf

- Use a custom output base name:

      python make_grid.py --size 4800 -o ruler_grid

  Produces: ruler_grid-000.png, ruler_grid-000.pdf, etc.

- Test very fine subdivisions (e.g., 20×20 majors, 8×8 minors):

      python make_grid.py --major 20 --minor 8 --size 8000

- Create transparent overlay grids for Blender background images:

      python make_grid.py --size 7200 --opacity 0.5 --format png

---

## Notes

- PNG snapping: If --size isn’t divisible by (major × minor), PNGs are automatically snapped down to the nearest multiple for exact line alignment. SVG/PDF are unaffected but match the snapped size for consistency.
- Leading zeros: Output numbering always uses -000, -001, etc., to keep filenames neat.
- Performance: Very large grids (≥ 7200 px) may take several seconds to generate.

---

## License

MIT License — free to use, modify, and distribute.
