"""Genera fondos pixel art 480x270, 16 colores, para temas de T3."""
import base64, io, json, os, sys
import numpy as np
from PIL import Image

W, H = 480, 270
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'backgrounds')
Y, X = np.mgrid[0:H, 0:W].astype(float)

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], float)

def vgrad(stops, y0=0, y1=H):
    """stops: [(t, '#hex'), ...] vertical gradient over full canvas."""
    t = np.clip((Y - y0) / (y1 - y0), 0, 1)
    img = np.zeros((H, W, 3))
    ts = [s[0] for s in stops]; cs = [hexc(s[1]) for s in stops]
    for c in range(3):
        img[..., c] = np.interp(t, ts, [k[c] for k in cs])
    return img

def noise1d(n, seed, octaves=5, base=6):
    rng = np.random.default_rng(seed); out = np.zeros(n); amp = 1; tot = 0
    for o in range(octaves):
        k = base * 2 ** o
        pts = rng.random(k + 2)
        xs = np.linspace(0, k, n)
        i = xs.astype(int); f = xs - i; f = f * f * (3 - 2 * f)
        out += amp * (pts[i] * (1 - f) + pts[i + 1] * f); tot += amp; amp *= 0.5
    return out / tot

def noise2d(seed, scale=40, octaves=4):
    rng = np.random.default_rng(seed); out = np.zeros((H, W)); amp = 1; tot = 0
    for o in range(octaves):
        s = scale / 2 ** o
        gh, gw = int(H / s) + 3, int(W / s) + 3
        g = rng.random((gh, gw))
        yy, xx = Y / s, X / s
        y0, x0 = yy.astype(int), xx.astype(int)
        fy, fx = yy - y0, xx - x0
        fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
        a = g[y0, x0] * (1 - fx) + g[y0, x0 + 1] * fx
        b = g[y0 + 1, x0] * (1 - fx) + g[y0 + 1, x0 + 1] * fx
        out += amp * (a * (1 - fy) + b * fy); tot += amp; amp *= 0.5
    return out / tot

def fill(img, mask, color, alpha=1.0):
    c = hexc(color) if isinstance(color, str) else color
    m = mask.astype(float)[..., None] * alpha
    img[:] = img * (1 - m) + c * m

def ridge(img, seed, base, amp, color, octaves=5, freq=4):
    h = base - amp * noise1d(W, seed, octaves, freq)
    fill(img, Y >= h[None, :], color)
    return h

def stars(img, seed, density, region=None, colors=('#ffffff',)):
    rng = np.random.default_rng(seed)
    m = rng.random((H, W)) < density
    if region is not None: m &= region
    for i, c in enumerate(colors):
        sub = m & (rng.random((H, W)) < 1 / (len(colors) - i))
        fill(img, sub, c); m &= ~sub

def disc(cx, cy, r): return (X - cx) ** 2 + (Y - cy) ** 2 <= r * r

# ---------------------------------------------------------------- escenas
def synthwave():
    img = vgrad([(0, '#14062e'), (.35, '#4a0d5e'), (.55, '#b8306a'), (.62, '#ff8a4c')], 0, 170)
    stars(img, 1, .004, Y < 90, ('#ffd6f0', '#9b7bff'))
    sun = disc(330, 150, 62) & (Y < 168)
    sg = vgrad([(0, '#fff27a'), (1, '#ff3d7f')], 88, 168)
    gaps = np.zeros_like(sun)
    for k, yy in enumerate(range(120, 168, 9)):
        gaps |= (Y >= yy) & (Y < yy + 2 + k)
    m = sun & ~gaps
    img[m] = sg[m]
    ridge(img, 3, 168, 34, '#2a0b3d', 4, 3)
    ridge(img, 4, 170, 14, '#1a0629', 5, 6)
    floor = Y >= 170
    fill(img, floor, '#0d0318')
    lines = np.zeros_like(floor)
    d = Y - 168
    for z in range(1, 14):  # horizontal lines with perspective
        yy = 170 + 100 / z ** 1.1
        lines |= np.abs(Y - yy) < .6
    lines |= np.abs(Y - 171) < .6
    xs = (X - 330) / np.maximum(d, 1)
    for k in range(-24, 25):  # rayos desde el punto de fuga
        for y in range(175, H):
            x = int(round(330 + k * 22 * (y - 168) / 30))
            if 0 <= x < W: lines[y, x] = True
    fill(img, floor & lines, '#ff3fb4')
    fill(img, floor & (Y < 176) & lines, '#ffb0e0')
    return img

def moonsea():
    img = vgrad([(0, '#050a1f'), (.6, '#13265a'), (1, '#2f4f8f')], 0, 180)
    stars(img, 7, .006, Y < 170, ('#ffffff', '#a9c4ff', '#6f8fd8'))
    halo = np.sqrt((X - 340) ** 2 + (Y - 70) ** 2)
    fill(img, halo < 52, '#1f3a78', .6); fill(img, halo < 40, '#2c4f95', .6)
    fill(img, disc(340, 70, 26), '#f4f1dc')
    fill(img, disc(333, 64, 6) | disc(350, 78, 4) | disc(346, 60, 3), '#d8d3b4')
    ridge(img, 9, 182, 10, '#0b1638', 4, 5)
    sea = Y >= 182
    fill(img, sea, '#081536')
    fill(img, sea & (Y > 220), '#060f29')
    rng = np.random.default_rng(11)
    for _ in range(900):
        y = rng.integers(184, H); spread = 6 + (y - 182) * .9
        x = int(rng.normal(340, spread)); L = rng.integers(3, 14)
        c = '#f4f1dc' if abs(x - 340) < spread * .5 and rng.random() < .6 else '#3d63b0'
        if 0 <= x < W: img[y, x:x + L] = hexc(c)
    for _ in range(260):
        y = rng.integers(186, H); x = rng.integers(0, W)
        img[y, x:x + rng.integers(4, 18)] = hexc('#14295e')
    return img

def ranges():
    img = vgrad([(0, '#2b1b4a'), (.4, '#8c4a6b'), (.7, '#f2a07b'), (1, '#ffd9a0')], 0, 150)
    fill(img, disc(150, 118, 18), '#fff1c9')
    layers = [('#c9708a', 120, 50), ('#9a4f7d', 150, 55), ('#6b376f', 180, 50),
              ('#43265c', 212, 45), ('#25183f', 244, 40), ('#140d26', 270, 30)]
    for i, (c, b, a) in enumerate(layers):
        ridge(img, 20 + i, b, a, c, 6, 3 + i)
    rng = np.random.default_rng(5)  # birds
    for _ in range(7):
        x, y = rng.integers(60, 260), rng.integers(40, 90)
        for dx, dy in ((-2, -1), (-1, 0), (0, 0), (1, 0), (2, -1)):
            img[y + dy, x + dx] = hexc('#3a1f45')
    return img

def dunes():
    img = vgrad([(0, '#03030c'), (.7, '#1a1238'), (1, '#4a2a52')], 0, 190)
    band = np.abs((Y - 0.42 * X) - 10) / 60
    neb = noise2d(31, 50)
    glow = np.clip(1 - band, 0, 1) * neb
    fill(img, glow > .35, '#2a1f5a', .7); fill(img, glow > .5, '#5a3f86', .7)
    fill(img, glow > .62, '#c7a6d9', .6)
    stars(img, 33, .012, Y < 190, ('#ffffff', '#ffe7b8', '#a7a0ff'))
    stars(img, 34, .03, (glow > .45) & (Y < 190), ('#ffffff',))
    cols = ['#5a3346', '#3f2236', '#2a1626', '#170b16']
    for i, c in enumerate(cols):
        x = np.arange(W)
        h = 175 + i * 22 - 26 * np.sin(x / (70 + 25 * i) + i * 1.7) - 10 * noise1d(W, 40 + i, 3, 2)
        top = Y >= h[None, :]
        fill(img, top, c)
        fill(img, top & (Y < h[None, :] + 1.5), '#b0726a' if i == 0 else '#6e3d50')
    return img

def planet():
    img = np.zeros((H, W, 3)); img[:] = hexc('#04030d')
    n = noise2d(51, 70); n2 = noise2d(52, 35)
    fill(img, n > .55, '#1b0f3a', .9); fill(img, n > .64, '#3a1a5e', .8)
    fill(img, (n2 > .62) & (n > .5), '#0f4c6b', .8); fill(img, (n > .72), '#b04a8a', .55)
    stars(img, 53, .007, None, ('#ffffff', '#9fd7ff', '#ffc4e6'))
    cx, cy, r = 320, 140, 70
    dx, dy = X - cx, Y - cy
    ring = lambda a, b: ((dx * .97 + dy * .26) / a) ** 2 + ((-dx * .26 + dy * .97) / b) ** 2
    ro, ri = ring(150, 30), ring(100, 18)
    ringm = (ro <= 1) & (ri > 1)
    behind = ringm & (-dx * .26 + dy * .97 < 0)
    front = ringm & ~behind
    fill(img, behind, '#8a6a9e')
    body = disc(cx, cy, r)
    shade = (dx * -.6 + dy * -.8) / r
    bands = np.sin((dy + 6 * np.sin(dx / 18)) / 7)
    base = np.where(bands > .3, 1, 0)
    pcol = np.zeros_like(img)
    for (m, c) in [(shade > .35, '#ffd3a8'), (shade > -.1, '#e88a6a'), (shade > -.5, '#9c4a6a'), (shade <= -.5, '#3b1d45')]:
        pcol[m & (pcol.sum(-1) == 0)] = hexc(c)
    pcol[(base == 1) & (shade > -.5)] *= .82
    img[body] = pcol[body]
    fill(img, front, '#d9b8e0'); fill(img, front & (ro > .82), '#8a6a9e')
    fill(img, ringm & (ri < 1.35) & (ri > 1), '#4c3560')
    fill(img, disc(110, 210, 12), '#7b8fb8'); fill(img, disc(106, 206, 11) & disc(110, 210, 12), '#b9c7e6')
    return img

def forest():
    img = vgrad([(0, '#0d1f24'), (.5, '#2d5a5a'), (1, '#a9cdb8')], 0, 200)
    fill(img, disc(360, 70, 22), '#e9f5dc', .9)
    rng = np.random.default_rng(61)
    layers = [('#5f8f84', 150, 140), ('#3f6e68', 185, 110), ('#26504d', 220, 90), ('#123432', 262, 60)]
    for li, (c, base, count) in enumerate(layers):
        ground = base + 8 * noise1d(W, 70 + li, 3, 3)
        fill(img, Y >= ground[None, :], c)
        for _ in range(count):
            x = rng.integers(-10, W + 10); hgt = rng.integers(28, 60) * (1 + li * .35)
            w = hgt * .28; g = ground[np.clip(x, 0, W - 1)]
            top = g - hgt
            t = (Y - top) / hgt
            tri = (t >= 0) & (Y <= g) & (np.abs(X - x) <= w * t * (0.75 + 0.25 * ((t * 6) % 1)))
            fill(img, tri, c)
        if li < 3:
            fog = (Y > base - 22) & (Y < base + 6)
            fill(img, fog, '#cfe5d6', .12)
    return img

def reef():
    img = vgrad([(0, '#2fb3c9'), (.35, '#11709a'), (.75, '#06315a'), (1, '#03142b')])
    for x0, w in ((120, 18), (200, 10), (300, 26), (390, 14), (440, 8)):
        ray = np.abs(X - x0 - (Y * .35)) < w * (1 - Y / 300)
        fill(img, ray & (Y < 230), '#8fe6f0', .18)
    fill(img, Y >= 235 + 10 * noise1d(W, 91, 4, 3)[None, :], '#1b2a3a')
    rng = np.random.default_rng(93)
    for _ in range(14):  # kelp
        x = rng.integers(0, W); hgt = rng.integers(60, 170); ph = rng.random() * 6
        for y in range(H - 1, H - hgt, -1):
            xx = int(x + 4 * np.sin(y / 14 + ph))
            c = '#1e7a55' if (y // 6) % 2 else '#2f9a62'
            if 0 <= xx < W - 2: img[y, xx:xx + 2] = hexc(c)
            if y % 11 == 0 and 0 <= xx + 2 < W - 4: img[y, xx + 2:xx + 5] = hexc('#3fbf74')
    for _ in range(10):  # corals
        x = rng.integers(0, W); r = rng.integers(6, 14)
        c = rng.choice(['#ff6f7f', '#ffb35c', '#c56cf0'])
        fill(img, disc(x, 250, r) & (Y < 252), c)
    for _ in range(9):  # fish
        x, y = rng.integers(30, W - 30), rng.integers(60, 200)
        c = rng.choice(['#ffd45c', '#ff8a5c', '#7af0ff'])
        fill(img, ((X - x) / 6) ** 2 + ((Y - y) / 3) ** 2 <= 1, c)
        fill(img, (X >= x + 5) & (X <= x + 8) & (np.abs(Y - y) <= (X - x - 5)), c)
    for _ in range(60):
        x, y = rng.integers(0, W), rng.integers(0, 230)
        img[y, x] = hexc('#c9f6ff')
    return img

SCENES = [('synthwave', 'Atardecer synthwave', synthwave), ('luna-mar', 'Luna sobre el mar', moonsea),
          ('cordilleras', 'Cordilleras al ocaso', ranges), ('dunas', 'Dunas y vía láctea', dunes),
          ('planeta', 'Planeta anillado', planet), ('bosque', 'Bosque con niebla', forest),
          ('arrecife', 'Arrecife', reef)]

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - .47

ACCENTS = {'arrecife': ['#ff6f7f', '#ffb35c', '#c56cf0', '#ffd45c', '#7af0ff', '#2f9a62', '#3fbf74']}

def finish(img, colors=24, dither=10, accents=()):
    img = np.clip(img, 0, 255)
    aug = img
    if accents:  # bloque extra para que la paleta reserve los colores de acento
        blk = np.zeros((60, W, 3))
        for i, c in enumerate(accents): blk[:, i * W // len(accents):(i + 1) * W // len(accents)] = hexc(c)
        aug = np.concatenate([img, blk])
    clean = Image.fromarray(aug.astype(np.uint8))
    pal = clean.quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    d = img + BAYER[Y.astype(int) % 4, X.astype(int) % 4][..., None] * dither
    return Image.fromarray(np.clip(d, 0, 255).astype(np.uint8)).quantize(palette=pal, dither=Image.Dither.NONE)

if __name__ == '__main__':
    meta = []
    for slug, name, fn in SCENES:
        im = finish(fn(), accents=ACCENTS.get(slug, ()))
        p = os.path.join(OUT, f'{slug}.png'); im.save(p, optimize=True)
        raw = open(p, 'rb').read()
        meta.append({'slug': slug, 'name': name, 'kb': round(len(raw) / 1024, 1),
                     'b64len': len(base64.b64encode(raw)), 'b64': base64.b64encode(raw).decode()})
        print(slug, meta[-1]['kb'], 'KB', meta[-1]['b64len'], 'chars')
    json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'))
