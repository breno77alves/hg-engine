#!/usr/bin/env python3
"""Convert pinned PokeAPI/Smogon Gen 9 sprites to hg-engine battle sheets.

The input directory must contain four 96x96 PNGs per National Dex number:
``<id>-front-normal.png``, ``<id>-front-shiny.png``,
``<id>-back-normal.png`` and ``<id>-back-shiny.png``. The files used for
v2.2.1 come from PokeAPI/sprites commit
``c10459b9b0129eaca5c5d9b1cac65336debb1d08``.

HGSS stores normal and shiny palettes separately while sharing indexed battle
art. This converter clusters normal/shiny colour pairs together, then writes a
normal-palette front sheet and a shiny-palette back sheet. Each static source
frame is duplicated to satisfy hg-engine's 160x80 two-frame layout without
fabricating animation.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import shutil

from PIL import Image


SOURCE_COMMIT = "c10459b9b0129eaca5c5d9b1cac65336debb1d08"
SPECIES = {
    933: "naclstack",
    946: "bramblin",
    947: "brambleghast",
    989: "sandy_shocks",
    991: "iron_bundle",
    992: "iron_hands",
    1010: "iron_leaves",
    1015: "munkidori",
    1023: "iron_crown",
    1024: "terapagos",
}
BOTH_SEXES = {933, 946, 947, 1024}
CANVAS_SIZE = 80
MAX_ART_SIZE = 72
MAX_COLOURS = 15  # palette index zero is reserved for transparency


def squared_distance(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return sum((a - b) ** 2 for a, b in zip(left, right))


def paired_palette(
    colour_pairs: Counter[tuple[int, int, int, int, int, int]],
) -> list[tuple[int, int, int, int, int, int]]:
    """Return deterministic weighted k-means centroids in normal/shiny RGB."""
    points = sorted(colour_pairs)
    target = min(MAX_COLOURS, len(points))
    first = max(points, key=lambda point: (colour_pairs[point], point))
    centroids: list[tuple[float, ...]] = [tuple(float(v) for v in first)]

    while len(centroids) < target:
        candidate = max(
            points,
            key=lambda point: (
                min(squared_distance(point, centroid) for centroid in centroids)
                * colour_pairs[point],
                point,
            ),
        )
        centroids.append(tuple(float(v) for v in candidate))

    for _ in range(64):
        buckets: list[list[tuple[tuple[int, ...], int]]] = [[] for _ in centroids]
        for point in points:
            index = min(
                range(len(centroids)),
                key=lambda item: (squared_distance(point, centroids[item]), item),
            )
            buckets[index].append((point, colour_pairs[point]))

        updated: list[tuple[float, ...]] = []
        for index, bucket in enumerate(buckets):
            if not bucket:
                updated.append(centroids[index])
                continue
            weight = sum(count for _, count in bucket)
            updated.append(
                tuple(
                    sum(point[channel] * count for point, count in bucket) / weight
                    for channel in range(6)
                )
            )
        if all(squared_distance(a, b) < 0.01 for a, b in zip(centroids, updated)):
            centroids = updated
            break
        centroids = updated

    return [tuple(round(value) for value in centroid) for centroid in centroids]


def normalized_pair(normal_path: Path, shiny_path: Path) -> tuple[Image.Image, Image.Image]:
    normal = Image.open(normal_path).convert("RGBA")
    shiny = Image.open(shiny_path).convert("RGBA")
    normal_box = normal.getbbox()
    shiny_box = shiny.getbbox()
    if normal_box is None or shiny_box is None:
        raise ValueError(f"empty source sprite: {normal_path} or {shiny_path}")

    normal = normal.crop(normal_box)
    shiny = shiny.crop(shiny_box)
    scale = min(1.0, MAX_ART_SIZE / max(normal.width, normal.height))
    size = (max(1, round(normal.width * scale)), max(1, round(normal.height * scale)))
    normal = normal.resize(size, Image.Resampling.NEAREST)
    shiny = shiny.resize(size, Image.Resampling.NEAREST)

    normal_canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE))
    shiny_canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE))
    offset = ((CANVAS_SIZE - size[0]) // 2, (CANVAS_SIZE - size[1]) // 2)
    normal_canvas.alpha_composite(normal, offset)
    shiny_canvas.alpha_composite(shiny, offset)
    return normal_canvas, shiny_canvas


def palette_index(
    normal_pixel: tuple[int, int, int, int],
    shiny_pixel: tuple[int, int, int, int],
    centroids: list[tuple[int, ...]],
) -> int:
    pair = normal_pixel[:3] + shiny_pixel[:3]
    return 1 + min(
        range(len(centroids)),
        key=lambda item: (squared_distance(pair, centroids[item]), item),
    )


def make_sheet(
    normal: Image.Image,
    shiny: Image.Image,
    centroids: list[tuple[int, ...]],
    use_shiny_palette: bool,
) -> Image.Image:
    frame = Image.new("P", (CANVAS_SIZE, CANVAS_SIZE), 0)
    indices: list[int] = []
    for normal_pixel, shiny_pixel in zip(
        normal.get_flattened_data(), shiny.get_flattened_data()
    ):
        if normal_pixel[3] == 0:
            indices.append(0)
        else:
            indices.append(palette_index(normal_pixel, shiny_pixel, centroids))
    frame.putdata(indices)

    palette = [0, 0, 0]
    start = 3 if use_shiny_palette else 0
    for centroid in centroids:
        palette.extend(centroid[start : start + 3])
    palette.extend([0] * (768 - len(palette)))
    frame.putpalette(palette)
    frame.info["transparency"] = 0

    sheet = Image.new("P", (CANVAS_SIZE * 2, CANVAS_SIZE), 0)
    sheet.putpalette(palette)
    sheet.paste(frame, (0, 0))
    sheet.paste(frame, (CANVAS_SIZE, 0))
    sheet.info["transparency"] = 0
    return sheet


def convert_species(source_dir: Path, sprite_root: Path, national_id: int, name: str) -> None:
    views: dict[str, tuple[Image.Image, Image.Image]] = {}
    colours: Counter[tuple[int, int, int, int, int, int]] = Counter()
    for view in ("front", "back"):
        normal, shiny = normalized_pair(
            source_dir / f"{national_id}-{view}-normal.png",
            source_dir / f"{national_id}-{view}-shiny.png",
        )
        views[view] = (normal, shiny)
        for normal_pixel, shiny_pixel in zip(
            normal.get_flattened_data(), shiny.get_flattened_data()
        ):
            if normal_pixel[3] != 0:
                colours[normal_pixel[:3] + shiny_pixel[:3]] += 1

    centroids = paired_palette(colours)
    front = make_sheet(*views["front"], centroids, use_shiny_palette=False)
    back = make_sheet(*views["back"], centroids, use_shiny_palette=True)

    species_dir = sprite_root / name
    genders = ("male", "female") if national_id in BOTH_SEXES else ("male",)
    for gender in genders:
        gender_dir = species_dir / gender
        gender_dir.mkdir(parents=True, exist_ok=True)
        front_path = gender_dir / "front.png"
        back_path = gender_dir / "back.png"
        front.save(front_path, optimize=False, bits=4)
        back.save(back_path, optimize=False, bits=4)

        # All 160x80 scan-front-to-back sheets use the same nitrogfx scan key.
        # Preserve the repository's existing key; copy the male key only when a
        # previously empty female slot did not have one.
        for path in (front_path, back_path):
            key = path.with_suffix(path.suffix + ".key")
            male_key = species_dir / "male" / key.name
            if not key.exists() and male_key.exists():
                shutil.copyfile(male_key, key)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument(
        "--sprite-root",
        type=Path,
        default=Path("data/graphics/sprites"),
    )
    args = parser.parse_args()

    for national_id, name in SPECIES.items():
        convert_species(args.source_dir, args.sprite_root, national_id, name)
        print(f"converted #{national_id} {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
