 #!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""
make_grid.py — Generate pixel-perfect ruler/UV grid images for Blender (and print).

Key features:
- 10x10 (default) major squares; each major square subdivided (default 12) for a fine minor grid
- Colored or black/white backgrounds
- Spreadsheet-like labels (A1..Z99, AA1 etc.) with selectable alignment and scaling
- Outputs one or more formats: PNG (raster), SVG/PDF (vector)
- Windows-safe auto-suffix for existing files: -000, -001, ...
- Pixel-perfect PNG snapping: size is reduced to the nearest multiple of (major * minor)
"""

# ----------------------------- IMPORTS ----------------------------------------
# argparse:   parse command line options like --size 3600
# os:         check for existing files so we can auto-suffix filenames
# sys:        print errors and exit non-zero on failure
# string:     for ASCII uppercase letters (A..Z) used in column labels
# matplotlib: plotting and vector/raster export backend we use to draw the grid
import argparse
import os
import sys
import string
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# ---------------------------- LABEL HELPERS -----------------------------------
def col_label(n: int) -> str:
    """
    Convert a 1-based column index to Excel-style letters.

    Examples:
        1  -> 'A'
        26 -> 'Z'
        27 -> 'AA'
        52 -> 'AZ'
        53 -> 'BA'

    Why 1-based: Excel columns are 1-based conceptually, so we mirror that.
    Implementation detail:
        - We repeatedly "divide" the index space by 26, adjusting by -1 so that
          1..26 maps to A..Z cleanly (instead of 0..25).
    """
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)  # subtract 1 before divmod to map 1..26 -> 0..25
        s = string.ascii_uppercase[r] + s
    return s


# Alignment map:
# - We expose user-friendly names like "UpperLeft", "MiddleCenter", etc.
# - Each maps to matplotlib's horizontal/vertical alignment keywords and also
#   a small fractional offset so labels don't kiss the border lines.
ALIGN_MAP = {
    "UpperLeft":    ("left",   "top",    (0.04,  0.04)),
    "UpperCenter":  ("center", "top",    (0.00,  0.04)),
    "UpperRight":   ("right",  "top",    (-0.04, 0.04)),
    "MiddleLeft":   ("left",   "center", (0.04,  0.00)),
    "MiddleCenter": ("center", "center", (0.00,  0.00)),
    "MiddleRight":  ("right",  "center", (-0.04, 0.00)),
    "LowerLeft":    ("left",   "bottom", (0.04, -0.04)),
    "LowerCenter":  ("center", "bottom", (0.00, -0.04)),
    "LowerRight":   ("right",  "bottom", (-0.04,-0.04)),
}


# --------------------------- RENDERING HELPERS --------------------------------
def perceived_luminance(rgb):
    """
    Compute a simple perceived luminance for an RGB triple (each 0..1).
    We use this to choose black/white text for contrast over the colored squares.
    Formula is the classic Rec.601 luma approximation.
    """
    r, g, b = rgb
    return 0.299*r + 0.587*g + 0.114*b


def hsv_to_rgb(h, s, v):
    """
    Convert HSV to RGB using matplotlib's utility.
    Input/Output are triples in 0..1.
    """
    return matplotlib.colors.hsv_to_rgb([h, s, v])


def build_colors(major_div):
    """
    Create a pleasing set of  major_div * major_div  colors.
    Strategy:
      - Sweep hue mostly across columns (so adjacent squares differ),
        with a small row-based drift so rows don't repeat exactly.
      - Keep saturation/value moderate so labels remain readable.
    """
    colors = []
    for r in range(major_div):
        for c in range(major_div):
            h = ((c * 0.1) + (r * 0.03)) % 1.0
            s = 0.6
            v = 0.85
            colors.append(hsv_to_rgb(h, s, v))
    return colors


def make_figure(size):
    """
    Create a full-bleed figure of exact pixel size 'size'x'size'.

    Why dpi=100?
      - We set the figure inches to size/100 by size/100, so dpi=100 yields
        exactly 'size' pixels on save, with no extra margins.
    Why add_axes([0,0,1,1])?
      - Use the entire canvas; no axes margins/ticks. We want pure pixels.
    """
    dpi = 100
    fig = plt.figure(figsize=(size / dpi, size / dpi), dpi=dpi)
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    ax.set_aspect('equal')   # preserve square pixels
    ax.axis('off')           # no ticks, frames, or labels
    return fig, ax


def draw_grid(ax, size, major, minor, color, label_alignment, label_scale, opacity):
    """
    Render the grid + labels into an existing axes.

    - 'size'         : final canvas size (pixels each side)
    - 'major'        : number of major squares across one axis
    - 'minor'        : number of minor subdivisions per major square
    - 'color'        : True for colored squares; False for white background
    - 'label_alignment': one of ALIGN_MAP keys defining label anchoring
    - 'label_scale'  : fraction of major square height used for font size
    - 'opacity'      : 0..1 alpha used for both fills and labels
    """

    # Major step: width/height of each major square in pixels.
    # Minor step: width/height of each minor square in pixels.
    # NOTE: We only call this after ensuring PNG size is divisible as needed,
    #       so these divisions are exact and lines will align.
    major_step = size // major
    minor_step = major_step // minor

    # Decide per-cell colors:
    #  - If 'color' is False, we use pure white for every cell (print-friendly).
    #  - Otherwise, we paint each major square with a distinct pastel-like color.
    colors = build_colors(major) if color else [(1.0, 1.0, 1.0)] * (major * major)

    # Fill the background major squares first, so grid lines draw over them later.
    idx = 0
    for row in range(major):
        for col in range(major):
            ax.add_patch(Rectangle(
                (col * major_step, row * major_step),  # lower-left corner of this cell
                major_step,                            # width
                major_step,                            # height
                facecolor=colors[idx],                 # cell color
                edgecolor='none',                      # no outline (we draw grid lines separately)
                alpha=opacity                          # allow semi-transparency if requested
            ))
            idx += 1

    # Draw the fine (minor) grid first, in a light gray:
    #  - Lines every 'minor_step' pixels both horizontally and vertically
    #  - Slight alpha to keep the grid present but not overpowering labels/colors
    for i in range(0, size + 1, minor_step):
        ax.add_line(plt.Line2D([0, size], [i, i], linewidth=0.5, color=(0, 0, 0, 0.3), antialiased=False))
        ax.add_line(plt.Line2D([i, i], [0, size], linewidth=0.5, color=(0, 0, 0, 0.3), antialiased=False))

    # Draw the bold (major) grid on top, in solid black for clarity.
    for i in range(0, size + 1, major_step):
        ax.add_line(plt.Line2D([0, size], [i, i], linewidth=2.0, color="black", antialiased=False))
        ax.add_line(plt.Line2D([i, i], [0, size], linewidth=2.0, color="black", antialiased=False))

    # Prepare label positioning: resolve alignment keywords + small fractional offsets.
    ha, va, (ox_frac, oy_frac) = ALIGN_MAP[label_alignment]

    # Compute font size as a fraction of the major cell height.
    # Default 0.20 means "20% of the major square height" -> works for 2–3 character labels (e.g., 'Z99').
    fontsize = int(major_step * label_scale)

    # Place one label inside each major square: 'A1', 'B1', ... 'J10', etc.
    # We choose black or white text based on cell luminance to keep labels legible over colors.
    idx = 0
    for row in range(major):       # rows are 0..major-1; display as 1..major
        for col in range(major):   # cols are 0..major-1; display as A..?
            label = f"{col_label(col + 1)}{row + 1}"

            # Contrast-aware text color for colored mode; always black in B&W mode.
            bg = colors[idx]
            text_color = 'black' if perceived_luminance(bg) > 0.6 else 'white'
            if not color:
                text_color = 'black'

            # Compute the base anchor position (lower-left of cell),
            # then adjust to left/center/right and bottom/center/top as requested,
            # and finally add small insets so text isn't glued to the border.
            x0 = col * major_step
            y0 = row * major_step

            x = x0 + (major_step / 2 if ha == "center" else major_step if ha == "right" else 0)
            y = y0 + (major_step / 2 if va == "center" else major_step if va == "top"   else 0)

            # Convert fractional offsets (like 0.04 of the cell) into pixel padding.
            x += int(ox_frac * major_step)
            y += int(oy_frac * major_step)

            ax.text(
                x, y, label,
                ha=ha, va=va,
                fontsize=fontsize, fontweight='bold',
                color=text_color,
                alpha=opacity
            )
            idx += 1


# --------------------------- FILENAME HANDLING --------------------------------
def unique_filename(base_without_ext: str, ext_with_dot: str) -> str:
    """
    Windows-safe unique filename creator.

    Behavior:
      - We *always* append a serial with a dash and 3 digits: -000, -001, ...
      - We never add extra periods; 'ext_with_dot' is the only dot we use.
      - If 'base-000.ext' exists, we try 'base-001.ext', then 'base-002.ext', etc.

    Rationale:
      - Avoids accidental overwrites.
      - Avoids Windows issues with multiple dots in filenames (e.g., foo.v1.2.png).
    """
    candidate = f"{base_without_ext}-000{ext_with_dot}"  # start with -000 for the first
    counter = 0
    while os.path.exists(candidate):
        counter += 1
        candidate = f"{base_without_ext}-{counter:03d}{ext_with_dot}"
    return candidate


# ------------------------------- DRIVER ---------------------------------------
def generate(size, major, minor, color, label_alignment, label_scale, opacity, formats, outbase):
    """
    Top-level orchestrator:
      - Ensure pixel-perfect PNG sizes (snap down to multiple of major*minor).
      - For each requested format (png/svg/pdf), draw and save an image.
      - Use Windows-safe, auto-suffixed filenames to avoid clobbering.
    """
    total_minor = major * minor  # total minor divisions per axis (e.g., 10*12 = 120)

    # PNG: Snap size for exact pixel alignment so lines land on whole pixels.
    # Vectors (SVG/PDF) don't need snapping, but we keep the same snapped size
    # so all outputs match 1:1 if generated together.
    snapped_size = size
    if "png" in formats and (size % total_minor != 0):
        snapped_size = (size // total_minor) * total_minor
        print(f"[info] PNG: size {size} not divisible by {total_minor}; snapping to {snapped_size}")
        if snapped_size <= 0:
            raise ValueError("Image size too small after snapping for PNG.")
    size = snapped_size

    # Create each requested format independently to avoid cross-format state issues.
    for fmt in formats:
        fig, ax = make_figure(size)
        draw_grid(ax, size, major, minor, color, label_alignment, label_scale, opacity)
        ext = "." + fmt
        outpath = unique_filename(outbase, ext)  # Windows-safe -000 suffixing
        fig.savefig(outpath, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        print(f"[ok] wrote {outpath} ({size}x{size}, {fmt})")


def main():
    """
    Parse CLI arguments, build a default descriptive output name if none is
    provided, and kick off generation.
    """
    parser = argparse.ArgumentParser(
        description="Generate pixel-perfect ruler/UV grid images (PNG/SVG/PDF)."
    )

    # Core geometry parameters:
    parser.add_argument("--size", type=int, default=3600,
                        help="Image size in pixels (square). Default: 3600")
    parser.add_argument("--major", type=int, default=10,
                        help="Major squares per axis. Default: 10")
    parser.add_argument("--minor", type=int, default=12,
                        help="Minor subdivisions per major square. Default: 12")

    # Color/background choices:
    parser.add_argument("--color", dest="color", action="store_true",
                        help="Enable colored major squares (default).")
    parser.add_argument("--no-color", dest="color", action="store_false",
                        help="Disable colors (white background).")
    parser.set_defaults(color=True)

    # Label placement and size:
    parser.add_argument("--label-alignment",
                        choices=list(ALIGN_MAP.keys()),
                        default="UpperLeft",
                        help="Label anchor position. Default: UpperLeft")
    parser.add_argument("--label-scale", type=float, default=0.20,
                        help="Label height as a fraction of major square height. Default: 0.20")

    # Global opacity (fills + labels):
    parser.add_argument("--opacity", type=float, default=1.0,
                        help="Opacity (0..1) for fills and labels. Default: 1.0")

    # Output formats and base name:
    parser.add_argument("--format", nargs="+", choices=["png", "svg", "pdf"], default=["png"],
                        help="One or more output formats. Default: png")
    parser.add_argument("-o", "--out", default=None,
                        help="Output base filename (without extension). "
                             "If omitted, a descriptive name is created.")

    args = parser.parse_args()

    # If user didn't provide -o/--out, build a descriptive base name.
    # We avoid extra dots; the only dot is the extension added later.
    if args.out:
        outbase = args.out
    else:
        outbase = (
            f"grid_{args.size}_major{args.major}_minor{args.minor}_"
            f"{'color' if args.color else 'bw'}_"
            f"{args.label_alignment.lower()}_"
            f"scale{args.label_scale}_"
            f"opacity{args.opacity}"
        )

    # Run the generator; on failure, print and exit with non-zero status.
    try:
        generate(args.size, args.major, args.minor, args.color,
                 args.label_alignment, args.label_scale, args.opacity,
                 args.format, outbase)
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)


# Standard "script entry point" guard so imports won't auto-run generation.
if __name__ == "__main__":
    main()

