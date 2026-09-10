# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow", "scikit-image", "shapely"]
# ///
"""Trace the torn-paper silhouette of success_not_guaranteed.png into the SVG
clip path behind the home hero, layouts/_partials/tearout-clip.html.

`just tear` runs it. The image's alpha channel is the paper (the rule box
and text inside it sit on paper, so they do not affect the outline). The
outline is simplified to about 1px at the image's 1764px width, which is
under half a pixel at the hero's size, and written in bounding-box units so
the same path stretches over the ad whatever its size.
"""

import pathlib

import numpy as np
from PIL import Image
from shapely.geometry import Polygon
from skimage import measure

HERE = pathlib.Path(__file__).resolve().parent
SOURCE = HERE / "success_not_guaranteed.png"
TARGET = HERE.parents[1] / "layouts" / "_partials" / "tearout-clip.html"
TOLERANCE = 1.0

TEMPLATE = """{{{{- /* The torn-newsprint silhouette behind the home hero, traced from the
     original "Success Not Guaranteed" tear-out image by tools/tearout
     (`just tear`). Bounding-box units, so the same path stretches over the
     ad whatever its size; .tearout in main.css clips to it. */ -}}}}
<svg width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute">
  <clipPath id="tear" clipPathUnits="objectBoundingBox">
    <path d="{d}"/>
  </clipPath>
</svg>
"""


def number(value):
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return text or "0"


def main():
    alpha = np.array(Image.open(SOURCE).convert("LA"))[..., 1]
    height, width = alpha.shape
    contours = sorted(measure.find_contours(alpha > 128, 0.5), key=len, reverse=True)
    outline = Polygon([(x, y) for y, x in contours[0]]).simplify(TOLERANCE, preserve_topology=True)
    points = list(outline.exterior.coords)[:-1]
    d = "M" + "L".join(f"{number(x / width)} {number(y / height)}" for x, y in points) + "Z"
    TARGET.write_text(TEMPLATE.format(d=d))
    print(f"{len(points)} points -> {TARGET.relative_to(HERE.parents[1])}")


if __name__ == "__main__":
    main()
