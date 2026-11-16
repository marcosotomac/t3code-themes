"""Genera la 'carátula' pixel art de la pantalla vacía: T3 grande + icono + rótulo."""
import base64, io
from PIL import Image

BIG = {  # 5x7
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    '3': ['11110', '00001', '00001', '01110', '00001', '00001', '11110'],
}
SMALL = {  # 3x5
 'A': '010101111101101', 'B': '110101110101110', 'C': '011100100100011', 'D': '110101101101110',
 'E': '111100110100111', 'F': '111100110100100', 'G': '011100101101011', 'H': '101101111101101',
 'I': '111010010010111', 'L': '100100100100111', 'M': '101111111101101', 'N': '110101101101101',
 'O': '010101101101010', 'P': '110101110100100', 'R': '110101110101101', 'S': '011100010001110',
 'T': '111010010010010', 'U': '101101101101111', 'V': '101101101101010', 'Z': '111001010100111',
 'Í': '010000010010010', ' ': '000000000000000',
}
ICONS = {
    'moon': ['..####.', '.###...', '###....', '###....', '###....', '.###...', '..####.'],
    'spark': ['...#...', '...#...', '..###..', '###*###', '..###..', '...#...', '...#...'],
    'star4': ['...#...', '..###..', '.#####.', '###*###', '.#####.', '..###..', '...#...'],
    'ring': ['..###..', '.#...#.', '#.....#', '#..*..#', '#.....#', '.#...#.', '..###..'],
}

def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

def mark(caption, icon, top, bottom, shadow, cap, icon_col, icon_core, scale=3):
    """Devuelve (data_url, ancho, alto) en pixeles de imagen."""
    gw = (5 + 1 + 5) * scale
    gh = 7 * scale
    iw = 7
    capw = len(caption) * 4 - 1
    w = max(gw + iw + 3, capw) + 2
    h = gh + 1 + 4 + 5 + 1
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    x0 = (w - (gw + iw + 3)) // 2
    t0, b0 = hexc(top), hexc(bottom)
    def put(x, y, c):
        if 0 <= x < w and 0 <= y < h: px[x, y] = c
    # sombra (1 px abajo-derecha) y luego el glifo con degradado vertical por filas
    for pass_ in ('shadow', 'fill'):
        cx = x0
        for ch in 'T3':
            for r, row in enumerate(BIG[ch]):
                for c, bit in enumerate(row):
                    if bit != '1': continue
                    for sy in range(scale):
                        for sx in range(scale):
                            y = r * scale + sy; x = cx + c * scale + sx
                            if pass_ == 'shadow':
                                put(x + 1, y + 1, hexc(shadow))
                            else:
                                t = y / (gh - 1)
                                t = round(t * 3) / 3  # 4 bandas, como pixel art de verdad
                                col = tuple(int(t0[i] * (1 - t) + b0[i] * t) for i in range(3)) + (255,)
                                put(x, y, col)
            cx += 6 * scale
    # icono a la derecha, alineado arriba
    ix = x0 + gw + 3
    for r, row in enumerate(ICONS[icon]):
        for c, ch in enumerate(row):
            if ch == '#': put(ix + c, r, hexc(icon_col))
            elif ch == '*': put(ix + c, r, hexc(icon_core))
    # rótulo
    cx = (w - capw) // 2; cy = gh + 5
    for ch in caption.upper():
        g = SMALL.get(ch, SMALL[' '])
        for i, bit in enumerate(g):
            if bit == '1': put(cx + i % 3, cy + i // 3, hexc(cap))
        cx += 4
    buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode(), w, h, im
