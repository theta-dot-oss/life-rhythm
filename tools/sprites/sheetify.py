"""Turn a generated pose sheet (white/plain background, poses laid out in a grid) into
app-ready sprite sheets: transparent background, every pose at the same scale, feet on
the same baseline, 320px cells with 40px gaps.

  python3 sheetify.py INPUT.png OUTDIR [--order 1,2,1,3,4,4] [--name work-thinking]
                      [--state work] [--name-ja ひらめき] [--seconds 1.5] [--pingpong]
                      [--cell 320] [--gap 40] [--baseline 0.93] [--fill 0.88]

Without --order it writes one sheet with all poses in reading order, plus every pose
as a separate PNG in OUTDIR/frames/.
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageFilter

def border_connected(mask):
    """Pixels of `mask` reachable from the image border (4-connected flood fill, numpy)."""
    reach = np.zeros_like(mask)
    reach[0, :], reach[-1, :], reach[:, 0], reach[:, -1] = mask[0, :], mask[-1, :], mask[:, 0], mask[:, -1]
    while True:
        grow = reach.copy()
        grow[1:, :] |= reach[:-1, :]; grow[:-1, :] |= reach[1:, :]
        grow[:, 1:] |= reach[:, :-1]; grow[:, :-1] |= reach[:, 1:]
        grow &= mask
        if np.array_equal(grow, reach):
            return reach
        reach = grow

def to_rgba(im):
    """Background -> transparent, with soft edges. If the image already has a transparent
    border (RGBA from the generator), its alpha is used as is. Otherwise the background
    colour is read from the border (usually white) and only pixels of that colour that
    are connected to the border are removed, so white areas inside the drawing (face,
    belly, paper) stay opaque."""
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        rgba = np.asarray(im.convert("RGBA"))
        border = np.concatenate([rgba[0, :, 3], rgba[-1, :, 3], rgba[:, 0, 3], rgba[:, -1, 3]])
        if border.mean() < 8:
            return Image.fromarray(rgba, "RGBA")
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    border_px = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bgc = np.median(border_px, axis=0)
    d = np.sqrt(((bgc - rgb) ** 2).sum(axis=2))      # distance from the background colour
    bg = border_connected(d < 58)                     # candidate background pixels
    # soft alpha only in the background region and a 1px fringe around it
    fringe = bg.copy()
    fringe[1:, :] |= bg[:-1, :]; fringe[:-1, :] |= bg[1:, :]; fringe[:, 1:] |= bg[:, :-1]; fringe[:, :-1] |= bg[:, 1:]
    alpha = np.where(fringe, np.clip((d - 18) / 40.0, 0, 1), 1.0)
    alpha[bg & (d < 18)] = 0
    # un-premultiply the white fringe so semi-transparent edge pixels keep their colour
    a = alpha[..., None]
    col = np.where((a > 0.02) & (a < 1), np.clip((rgb - 255 * (1 - a)) / np.maximum(a, 0.02), 0, 255), rgb)
    out = np.dstack([col, alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")

def runs_1d(mask, axis):
    """Raw 1-D runs of 'something here' along axis."""
    proj = mask.any(axis=axis)
    runs, start = [], None
    for i, v in enumerate(proj):
        if v and start is None:
            start = i
        elif not v and start is not None:
            runs.append([start, i]); start = None
    if start is not None:
        runs.append([start, len(proj)])
    return runs

def bands(mask, axis, small_frac=0.35):
    """Runs along axis, where fragments much narrower than a typical pose (effects such as
    motion lines, rays or sparkles that fell into a gap) are merged into the nearest run.
    Big runs stay separate even when the gap between them is only a few pixels."""
    runs = runs_1d(mask, axis)
    if not runs:
        return []
    widths = sorted(r[1] - r[0] for r in runs)
    big = [w for w in widths if w >= 0.5 * widths[-1]]
    typical = big[len(big) // 2]
    small = typical * small_frac
    bigs = [i for i, r in enumerate(runs) if r[1] - r[0] >= small]
    if not bigs:
        return [[runs[0][0], runs[-1][1]]]
    out = [list(runs[i]) for i in bigs]
    for i, r in enumerate(runs):
        if i in bigs:
            continue
        # attach the fragment to the nearer big run
        best = min(range(len(bigs)), key=lambda k: min(abs(r[0] - runs[bigs[k]][1]), abs(runs[bigs[k]][0] - r[1])))
        out[best][0] = min(out[best][0], r[0]); out[best][1] = max(out[best][1], r[1])
    return [r for r in out if r[1] - r[0] >= 8]

def tight(a, x0, y0, x1, y1):
    sub = a[y0:y1, x0:x1]
    ys, xs = np.where(sub)
    if len(xs) == 0:
        return None
    return (x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1)

def find_cells(rgba, count=None):
    a = np.asarray(rgba)[..., 3] > 40
    cells = []
    for y0, y1 in bands(a, axis=1):
        for x0, x1 in bands(a[y0:y1], axis=0):
            c = tight(a, x0, y0, x1, y1)
            if c:
                cells.append(c)
    # Poses that touch each other (pompoms, wide props) come out as one wide cell. When the
    # expected count is known, split the widest cells at their emptiest column until we
    # have that many.
    while count and len(cells) < count:
        i = max(range(len(cells)), key=lambda k: cells[k][2] - cells[k][0])
        x0, y0, x1, y1 = cells[i]
        w = x1 - x0
        occ = a[y0:y1, x0:x1].sum(axis=0)
        lo, hi = int(w * 0.3), int(w * 0.7)
        cut = x0 + lo + int(np.argmin(occ[lo:hi]))
        parts = [tight(a, x0, y0, cut, y1), tight(a, cut, y0, x1, y1)]
        cells[i:i + 1] = [p for p in parts if p]
        if len(parts) < 2:
            break
    # reading order: group into rows by the bottom edge (effects above the head would
    # otherwise push a pose into a different row), then left to right
    if cells:
        h = float(np.median([c[3] - c[1] for c in cells]))
        rows = []
        for c in sorted(cells, key=lambda c: c[3]):
            if rows and abs(c[3] - rows[-1][-1][3]) < h * 0.5:
                rows[-1].append(c)
            else:
                rows.append([c])
        cells = [c for row in rows for c in sorted(row, key=lambda c: c[0])]
    return cells

def body_bottom(frame):
    """Baseline = lowest row that has strongly opaque, not-too-light pixels (feet),
    ignoring the faint drop shadow underneath."""
    arr = np.asarray(frame).astype(int)
    a = arr[..., 3] > 200
    lum = arr[..., :3].mean(axis=2)
    solid = a & (lum < 235)
    rows = np.where(solid.any(axis=1))[0]
    return rows.max() + 1 if len(rows) else frame.height

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input"); ap.add_argument("outdir")
    ap.add_argument("--order", help="1-based pose indices for the animation, e.g. 1,2,1,3,4,4")
    ap.add_argument("--name", default=None); ap.add_argument("--state", default="any")
    ap.add_argument("--name-ja", default=None); ap.add_argument("--fps", type=int, default=None)
    ap.add_argument("--seconds", type=float, default=1.5, help="seconds per frame in the app (1-3 recommended)")
    ap.add_argument("--pingpong", action="store_true")
    ap.add_argument("--cell", type=int, default=320); ap.add_argument("--gap", type=int, default=40)
    ap.add_argument("--pad", type=int, default=20)
    ap.add_argument("--baseline", type=float, default=0.93, help="feet baseline as a fraction of the cell height")
    ap.add_argument("--fill", type=float, default=0.88, help="tallest pose height as a fraction of the cell")
    ap.add_argument("--version", type=int, default=1)
    ap.add_argument("--count", type=int, default=None, help="expected number of poses (warns if different)")
    args = ap.parse_args()

    os.makedirs(os.path.join(args.outdir, "frames"), exist_ok=True)
    rgba = to_rgba(Image.open(args.input))
    cells = find_cells(rgba, args.count)
    if not cells:
        sys.exit("no poses found")
    frames = [rgba.crop(c) for c in cells]
    if args.count and len(cells) != args.count:
        print(f"WARNING: expected {args.count} poses, found {len(cells)}", file=sys.stderr)

    # one common scale for every pose: based on the median pose height (feet to top of head,
    # effects like rays or bulbs above the head are included, so use the median not the max)
    heights = [body_bottom(f) - 0 for f in frames]
    # height from top of drawing to feet baseline
    top_to_feet = [body_bottom(f) for f in frames]
    ref = float(np.median(top_to_feet))
    scale = (args.cell * args.fill) / ref
    base_y = int(args.cell * args.baseline)
    # never let a pose (a jump with rays above it, wide-open arms) run out of the cell:
    # shrink the common scale until the tallest and widest poses fit
    tallest = max(top_to_feet)
    widest = max(f.width for f in frames)
    scale = min(scale, (base_y - 6) / tallest, (args.cell - 8) / widest)

    cell_imgs = []
    for i, f in enumerate(frames):
        w, h = f.size
        f2 = f.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
        feet = round(body_bottom(f) * scale)
        canvas = Image.new("RGBA", (args.cell, args.cell), (0, 0, 0, 0))
        # horizontal centre on the body (opaque pixels with alpha>200), vertical: feet on baseline
        # centre on the dense columns (the body), ignoring thin effects beside it
        occ = (np.asarray(f2)[..., 3] > 200).sum(axis=0)
        xs = np.where(occ >= occ.max() * 0.25)[0] if occ.max() else []
        cx = (xs.min() + xs.max()) / 2 if len(xs) else f2.width / 2
        ox = round(args.cell / 2 - cx)
        oy = base_y - feet
        canvas.paste(f2, (ox, oy), f2)
        cell_imgs.append(canvas)
        canvas.save(os.path.join(args.outdir, "frames", f"pose-{i+1:02d}.png"))

    order = [int(x) - 1 for x in args.order.split(",")] if args.order else list(range(len(cell_imgs)))
    seq = [cell_imgs[i] for i in order]
    n = len(seq)
    W = args.pad * 2 + n * args.cell + (n - 1) * args.gap
    sheet = Image.new("RGBA", (W, args.cell + args.pad * 2), (0, 0, 0, 0))
    for i, im in enumerate(seq):
        sheet.paste(im, (args.pad + i * (args.cell + args.gap), args.pad), im)
    name = args.name or os.path.splitext(os.path.basename(args.input))[0]
    out = os.path.join(args.outdir, f"{name}.png")
    sheet.save(out, optimize=True)
    entry = {"name": name, "name_ja": args.name_ja or name, "file": f"{name}.png", "state": args.state,
             "frames": n, "frame_size": args.cell, "gap": args.gap, "seconds": args.seconds, "pingpong": args.pingpong, "version": args.version}
    if args.fps:
        entry["fps"] = args.fps
    json.dump(entry, open(os.path.join(args.outdir, f"{name}.manifest.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{len(frames)} poses found -> {out} ({n} frames); scale={scale:.3f}")

if __name__ == "__main__":
    main()
