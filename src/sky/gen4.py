"""Cielos estrellados planos azul noche, al estilo de Nyx (gradiente suave + tramado + estrellas)."""
import base64, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import *  # noqa

BG0, BG1 = hexc('#02040d'), hexc('#071433')

def base(bottom='#0a1a40', top='#02040b'):
    t = (Y / H) ** 1.4
    return hexc(top) * (1 - t[..., None]) + hexc(bottom) * t[..., None]

def glow(img, field, color, strength):
    img += np.clip(field, 0, 1)[..., None] * (hexc(color) - img) * strength

def starfield(img, seed, n_small=900, n_mid=60, n_big=10):
    rng = np.random.default_rng(seed)
    for _ in range(n_small):
        x, y = rng.integers(0, W), rng.integers(0, H)
        b = rng.random()
        img[y, x] = img[y, x] + (hexc('#9db4ff') - img[y, x]) * (.35 + .5 * b)
    for _ in range(n_mid):
        x, y = rng.integers(1, W - 1), rng.integers(1, H - 1)
        img[y, x] = hexc(rng.choice(['#ffffff', '#cfdcff', '#a8c4ff']))
    for _ in range(n_big):  # destellos en cruz
        x, y = rng.integers(3, W - 3), rng.integers(3, H - 3)
        img[y, x] = hexc('#ffffff')
        for d in (1, 2):
            c = '#b8ccff' if d == 1 else '#4a64a8'
            img[y, x - d] = img[y, x + d] = img[y - d, x] = img[y + d, x] = hexc(c)

def deepen(img):
    # más oscuro y más azul: baja luminancia y quita verde/rojo
    out = img * 0.55
    out[..., 0] *= .7; out[..., 1] *= .8
    return out

def smooth(seed, scale): return noise2d(seed, scale, 3)

def plano():
    img = base('#0b1b44')
    img[:] = deepen(img)
    starfield(img, 1)
    return img

def via_lactea():
    img = base('#081638')
    d = (Y - (H * .95 - .55 * X)) / 70
    band = np.exp(-d ** 2) * (0.55 + 0.9 * (smooth(3, 60) - .4))
    band *= 0.75 + 0.5 * (smooth(4, 30) - .5)
    glow(img, band, '#1c3570', .85)
    glow(img, np.clip(band - .35, 0, 1) * 1.5, '#3a5aa0', .55)
    glow(img, np.clip(band - .65, 0, 1) * 2, '#8aa4dc', .3)
    img[:] = deepen(img)
    starfield(img, 2, 1100, 80, 12)
    rng = np.random.default_rng(5)
    for _ in range(700):  # estrellas extra dentro de la banda
        x, y = rng.integers(0, W), rng.integers(0, H)
        if band[y, x] > .4: img[y, x] = hexc('#dfe8ff')
    return img

def aurora():
    img = base('#06112c')
    xs = X / W
    cy = H * (.62 - .38 * xs) + 18 * np.sin(xs * 9) + 8 * np.sin(xs * 23)
    d = (Y - cy)
    ribbon = np.exp(-(d / 30) ** 2) * (0.5 + 0.6 * smooth(7, 40))
    curtain = np.where(d > 0, np.exp(-d / 55) * (1 - np.exp(-np.maximum(d, 0) / 10)), 0) * (0.6 + 0.4 * np.sin(X / 2.2 + 6 * smooth(8, 30))) * .6
    f = np.clip(ribbon + curtain * (0.4 + 0.6 * smooth(9, 50)), 0, 1.4)
    edge = 1 - xs * .2
    glow(img, f * .9 * edge, '#163a80', .8)
    glow(img, np.clip(f - .4, 0, 1) * 1.4, '#2f6cc0', .5)
    glow(img, np.clip(f - .75, 0, 1) * 2, '#7fc8f0', .3)
    img[:] = deepen(img)
    starfield(img, 3, 800, 50, 8)
    return img

def nebulosa():
    img = base('#07122e')
    n = smooth(11, 90)
    r = np.sqrt(((X - W * .78) / (W * .45)) ** 2 + ((Y - H * .7) / (H * .6)) ** 2)
    f = np.clip(1 - r, 0, 1) ** 1.2 * (0.5 + n)
    glow(img, f, '#16296a', .85)
    glow(img, np.clip(f - .4, 0, 1) * 1.6, '#2c4a98', .5)
    glow(img, np.clip(f - .7, 0, 1) * 2.2, '#6a8ad0', .3)
    img[:] = deepen(img)
    starfield(img, 4, 1000, 70, 11)
    return img

SC = [('cielo-plano', 'Cielo plano', plano), ('cielo-via-lactea', 'Vía láctea tenue', via_lactea),
      ('cielo-aurora', 'Aurora azul', aurora), ('cielo-nebulosa', 'Nebulosa en la esquina', nebulosa)]

if __name__ == '__main__':
    meta = []
    for slug, name, fn in SC:
        im = finish(fn(), colors=24, dither=16, accents=['#ffffff', '#cfdcff', '#4a64a8'])
        p = os.path.join(OUT, f'{slug}.png'); im.save(p, optimize=True)
        raw = open(p, 'rb').read()
        meta.append({'slug': slug, 'name': name, 'kb': round(len(raw) / 1024, 1), 'b64': base64.b64encode(raw).decode()})
        print(slug, meta[-1]['kb'], 'KB')
    json.dump(meta, open(os.path.join(OUT, 'meta4.json'), 'w'))
