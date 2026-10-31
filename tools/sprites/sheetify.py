"""Turn a generated pose sheet (white/plain background, poses laid out in a grid) into
app-ready sprite sheets: transparent background, every pose at the same scale, feet on
the same baseline, 320px cells with 40px gaps.

  python3 sheetify.py INPUT.png OUTDIR [--order 1,2,1,3,4,4] [--name work-thinking]
                      [--state work] [--name-ja ひらめき] [--fps 2] [--pingpong]
                      [--cell 320] [--gap 40] [--baseline 0.93] [--fill 0.88]

Without --order it writes one sheet with all poses in reading order, plus every pose
as a separate PNG in OUTDIR/frames/.
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageFilter

def to_rgba(im):
    """White (or near-white) background -> transparent, with soft edges."""
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    # distance from pure white, 0..441
    d = np.sqrt(((255 - rgb) ** 2).sum(axis=2))
    alpha = np.clip((d - 18) / 40.0, 0, 1)  # <18: bg, >58: fully opaque
    # un-premultiply the white fringe so semi-transparent edge pixels keep their colour
    a = alpha[..., None]
    col = np.where(a > 0.02, np.clip((rgb - 255 * (1 - a)) / np.maximum(a, 0.02), 0, 255), rgb)
    out = np.dstack([col, alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")

def bands(mask, axis, min_gap, min_size=8):
    """1-D runs of 'something here' along axis, merging gaps smaller than min_gap."""
    proj = mask.any(axis=axis)
    runs, start = [], None
    for i, v in enumerate(proj):
        if v and start is None:
            start = i
        elif not v and start is not None:
            runs.append([start, i]); start = None
    if start is not None:
        runs.append([start, len(proj)])
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < min_gap:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [r for r in merged if r[1] - r[0] >= min_size]

def find_cells(rgba, min_gap_frac=0.01):
    a = np.asarray(rgba)[..., 3] > 40
    H, W = a.shape
    cells = []
    for y0, y1 in bands(a, axis=1, min_gap=int(H * min_gap_frac)):
        for x0, x1 in bands(a[y0:y1], axis=0, min_gap=int(W * min_gap_frac)):
            sub = a[y0:y1, x0:x1]
            ys, xs = np.where(sub)
            cells.append((x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1))
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
    ap.add_argument("--name-ja", default=None); ap.add_argument("--fps", type=int, default=2)
    ap.add_argument("--pingpong", action="store_true")
    ap.add_argument("--cell", type=int, default=320); ap.add_argument("--gap", type=int, default=40)
    ap.add_argument("--pad", type=int, default=20)
    ap.add_argument("--baseline", type=float, default=0.93, help="feet baseline as a fraction of the cell height")
    ap.add_argument("--fill", type=float, default=0.88, help="tallest pose height as a fraction of the cell")
    ap.add_argument("--version", type=int, default=1)
    args = ap.parse_args()

    os.makedirs(os.path.join(args.outdir, "frames"), exist_ok=True)
    rgba = to_rgba(Image.open(args.input))
    cells = find_cells(rgba)
    if not cells:
        sys.exit("no poses found")
    frames = [rgba.crop(c) for c in cells]

    # one common scale for every pose: based on the median pose height (feet to top of head,
    # effects like rays or bulbs above the head are included, so use the median not the max)
    heights = [body_bottom(f) - 0 for f in frames]
    # height from top of drawing to feet baseline
    top_to_feet = [body_bottom(f) for f in frames]
    ref = float(np.median(top_to_feet))
    scale = (args.cell * args.fill) / ref
    base_y = int(args.cell * args.baseline)

    cell_imgs = []
    for i, f in enumerate(frames):
        w, h = f.size
        f2 = f.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
        feet = round(body_bottom(f) * scale)
        canvas = Image.new("RGBA", (args.cell, args.cell), (0, 0, 0, 0))
        # horizontal centre on the body (opaque pixels with alpha>200), vertical: feet on baseline
        arr = np.asarray(f2)[..., 3] > 200
        xs = np.where(arr.any(axis=0))[0]
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
             "frames": n, "frame_size": args.cell, "gap": args.gap, "fps": args.fps, "pingpong": args.pingpong, "version": args.version}
    json.dump(entry, open(os.path.join(args.outdir, f"{name}.manifest.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{len(frames)} poses found -> {out} ({n} frames); scale={scale:.3f}")

if __name__ == "__main__":
    main()
