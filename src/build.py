"""Construye 4 temas de T3 Code, uno por cada cielo pixel art."""
import base64, io, json, math, os, sys
from string import Template
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, '..', 'backgrounds')
OUT = os.path.join(HERE, '..', 'themes')
DBG = os.path.join(HERE, 'build'); os.makedirs(DBG, exist_ok=True)  # CSS legible de cada tema, para revisar

def ok2rgb(L, C, Hh):
    h = math.radians(Hh); a, b = C * math.cos(h), C * math.sin(h)
    l = (L + .3963377774 * a + .2158037573 * b) ** 3; m = (L - .1055613458 * a - .0638541728 * b) ** 3
    s = (L - .0894841775 * a - 1.291485548 * b) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + .2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - .3413193965 * s
    bb = -.0041960863 * l - .7034186147 * m + 1.707614701 * s
    enc = lambda x: 12.92 * x if x <= .0031308 else 1.055 * x ** (1 / 2.4) - .055
    return tuple(round(min(1, max(0, enc(max(0, x)))) * 255) for x in (r, g, bb))

def trip(L, C, Hh): return ' '.join(map(str, ok2rgb(L, C, Hh)))
def hx(L, C, Hh): return '#%02x%02x%02x' % ok2rgb(L, C, Hh)
def o(L, C, Hh): return f'oklch({L:g} {C:g} {Hh:g})'

def roles(t):
    h, a, aL, aC = t['bg_h'], t['acc_h'], t['acc_L'], t['acc_C']
    ah = t['act_h']; s = t.get('spark_h', 80)
    return {
        'canvas': o(.10, .028, h), 'chrome': o(.10, .028, h), 'toolbar': o(.10, .028, h),
        'toolbarForeground': o(.96, .012, h), 'toolbarBorder': o(.25, .03, h),
        'toolbarControl': o(.21, .04, h), 'toolbarControlForeground': o(.86, .035, a),
        'toolbarControlHover': o(.27, .055, h),
        'surface': o(.155, .035, h), 'surfaceRaised': o(.18, .042, h), 'surfaceOverlay': o(.195, .046, h),
        'text': o(.96, .012, h), 'textMuted': o(.79, .035, h), 'border': o(.29, .04, h),
        'input': o(.31, .055, h), 'focus': o(min(aL + .04, .86), aC, a),
        'accent': o(aL, aC, a), 'accentForeground': o(.17, .045, h),
        'secondary': o(.21, .05, h), 'secondaryForeground': o(.94, .018, a),
        'muted': o(.22, .045, h), 'mutedForeground': o(.75, .04, h),
        'placeholder': o(.69, .04, h), 'secondaryLabel': o(.75, .04, h), 'iconMuted': o(.77, .04, h),
        'error': o(.70, .17, 15), 'errorForeground': o(.90, .06, 15), 'errorSurface': o(.25, .06, 15),
        'warning': o(.80, .145, s), 'warningForeground': o(.87, .12, s), 'warningSurface': o(.27, .05, s),
        'update': o(aL, aC, a), 'updateForeground': o(.84, .09, a), 'updateSurface': o(.22, .055, a),
        'accentSurface': o(.29, .075, a), 'accentSurfaceForeground': o(.96, .015, a),
        'messageSurface': o(.25, .07, ah), 'messageForeground': o(.96, .015, a),
        'messageAction': o(.52, .14, ah), 'messageActionForeground': o(1, 0, 0),
        'messageActionHover': o(.57, .14, ah),
        'codeBackground': o(.13, .035, h), 'codeForeground': o(.87, .05, a),
        'searchMatchBackground': o(.46, .09, s), 'searchMatchForeground': o(.98, 0, 0),
        'searchMatchActiveBackground': o(.80, .14, s), 'searchMatchActiveForeground': o(.21, .03, s),
        'sidebar': o(.10, .028, h), 'sidebarForeground': o(.95, .01, h),
        'sidebarMutedForeground': o(.73, .04, h), 'sidebarControlSurface': o(.10, .028, h),
        'sidebarRowHover': o(.18, .035, h), 'sidebarRowActive': o(.22, .05, h),
        'sidebarRowSelected': o(.26, .07, a), 'sidebarBorder': o(.21, .03, h),
        'terminalBackground': o(.125, .035, h), 'terminalForeground': o(.95, .012, h),
        'terminalCursor': o(aL, aC, t.get('cursor_h', a)) if 'cursor' not in t else t['cursor'],
        'terminalSelection': o(.31, .08, a),
        'terminalScrollbar': o(.27, .035, h), 'terminalScrollbarHover': o(.36, .05, h),
    }

CSS = Template(open(os.path.join(HERE, 'template.css')).read())

from urllib.parse import quote
def dither(hexcol, op=.2):
    r = lambda x, y: f"<rect x='{x}' y='{y}' width='2' height='2' fill='{hexcol}' fill-opacity='{op}'/>"
    pat = lambda i, w, h, cells: f"<pattern id='{i}' width='{w}' height='{h}' patternUnits='userSpaceOnUse'>" + ''.join(r(x, y) for x, y in cells) + "</pattern>"
    s = ("<svg xmlns='http://www.w3.org/2000/svg' width='100%' height='100%' shape-rendering='crispEdges'><defs>"
         + pat('a', 4, 4, [(0, 0), (2, 0), (0, 2)]) + pat('b', 4, 4, [(0, 0), (2, 2)])
         + pat('c', 4, 4, [(0, 0)]) + pat('d', 8, 8, [(0, 0), (4, 4)])
         + f"</defs><rect width='22%' height='100%' fill='{hexcol}' fill-opacity='{op}'/>"
         "<rect x='22%' width='18%' height='100%' fill='url(#a)'/><rect x='40%' width='18%' height='100%' fill='url(#b)'/>"
         "<rect x='58%' width='18%' height='100%' fill='url(#c)'/><rect x='76%' width='18%' height='100%' fill='url(#d)'/></svg>")
    return 'data:image/svg+xml,' + quote(s, safe="/:=' ")

def horizon(hexcol, op=.15):
    r = lambda x, y: f"<rect x='{x}' y='{y}' width='2' height='2' fill='{hexcol}' fill-opacity='{op}'/>"
    pat = lambda i, w, h, cells: f"<pattern id='{i}' width='{w}' height='{h}' patternUnits='userSpaceOnUse'>" + ''.join(r(x, y) for x, y in cells) + "</pattern>"
    s = ("<svg xmlns='http://www.w3.org/2000/svg' width='100%' height='100%' shape-rendering='crispEdges'><defs>"
         + pat('a', 4, 4, [(0, 0), (2, 0), (0, 2)]) + pat('b', 4, 4, [(0, 0), (2, 2)])
         + pat('c', 4, 4, [(0, 0)]) + pat('d', 8, 8, [(0, 0), (4, 4)])
         + f"</defs><rect y='86%' width='100%' height='14%' fill='{hexcol}' fill-opacity='{op}'/>"
         "<rect y='74%' width='100%' height='12%' fill='url(#a)'/><rect y='62%' width='100%' height='12%' fill='url(#b)'/>"
         "<rect y='50%' width='100%' height='12%' fill='url(#c)'/><rect y='38%' width='100%' height='12%' fill='url(#d)'/></svg>")
    return 'data:image/svg+xml,' + quote(s, safe="/:=' ")

def card_horizon(hexcol, op=.09):
    r = lambda x, y: f"<rect x='{x}' y='{y}' width='2' height='2' fill='{hexcol}' fill-opacity='{op}'/>"
    pat = lambda i, w, h, cells: f"<pattern id='{i}' width='{w}' height='{h}' patternUnits='userSpaceOnUse'>" + ''.join(r(x, y) for x, y in cells) + "</pattern>"
    s = ("<svg xmlns='http://www.w3.org/2000/svg' width='100%' height='100%' shape-rendering='crispEdges'><defs>"
         + pat('a', 4, 4, [(0, 0), (2, 0), (0, 2)]) + pat('b', 4, 4, [(0, 0), (2, 2)])
         + pat('c', 4, 4, [(0, 0)]) + pat('d', 8, 8, [(0, 0), (4, 4)])
         + f"</defs><rect y='94%' width='100%' height='6%' fill='{hexcol}' fill-opacity='{op}'/>"
         "<rect y='88%' width='100%' height='6%' fill='url(#a)'/><rect y='82%' width='100%' height='6%' fill='url(#b)'/>"
         "<rect y='76%' width='100%' height='6%' fill='url(#c)'/><rect y='70%' width='100%' height='6%' fill='url(#d)'/></svg>")
    return 'data:image/svg+xml,' + quote(s, safe="/:=' ")

def card_stars(hexcol):
    # franja baja (12 px) para que las estrellas vivan en el margen superior y no choquen con iconos
    def plus(x, y, o=1):
        return (f"<rect x='{x}' y='{y}' width='2' height='2' fill='{hexcol}' fill-opacity='{o}'/>"
                + ''.join(f"<rect x='{x+dx}' y='{y+dy}' width='2' height='2' fill='{hexcol}' fill-opacity='{o*.45:.2f}'/>"
                          for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2))))
    dot = lambda x, y, o: f"<rect x='{x}' y='{y}' width='2' height='2' fill='{hexcol}' fill-opacity='{o}'/>"
    s = ("<svg xmlns='http://www.w3.org/2000/svg' width='160' height='12' shape-rendering='crispEdges'>"
         + plus(140, 4) + plus(84, 6, .7) + dot(112, 2, .8) + dot(152, 8, .55) + dot(60, 4, .5) + dot(30, 8, .35) + dot(124, 9, .45)
         + "</svg>")
    return 'data:image/svg+xml,' + quote(s, safe="/:=' ")

def stars(hexcol):
    def plus(x, y, o=1):
        return (f"<rect x='{x}' y='{y}' width='2' height='2' fill='{hexcol}' fill-opacity='{o}'/>"
                + ''.join(f"<rect x='{x+dx}' y='{y+dy}' width='2' height='2' fill='{hexcol}' fill-opacity='{o*.45:.2f}'/>"
                          for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2))))
    dot = lambda x, y, o: f"<rect x='{x}' y='{y}' width='2' height='2' fill='{hexcol}' fill-opacity='{o}'/>"
    s = ("<svg xmlns='http://www.w3.org/2000/svg' width='120' height='40' shape-rendering='crispEdges'>"
         + plus(102, 8) + plus(64, 24, .7) + dot(84, 14, .8) + dot(114, 28, .6) + dot(48, 8, .5) + dot(92, 32, .45) + dot(30, 18, .35)
         + "</svg>")
    return 'data:image/svg+xml,' + quote(s, safe="/:=' ")

def build(t):
    art = base64.b64encode(open(os.path.join(ART, t['art'] + '.png'), 'rb').read()).decode()
    a, b = t['acc_h'], t['b_h']
    v = dict(
        name=t['name'], tagline=t['tagline'],
        A=trip(t['acc_L'], t['acc_C'], a), B=trip(t['b_L'], t['b_C'], b),
        L=trip(.86, .05, a), Hh=trip(.88, .07, a), K=trip(.14, .04, t['bg_h']), D=trip(.07, .025, t['bg_h']),
        S=t['spark'], ART=art, WM1=t['wm'][0], WM2=t['wm'][1], WM3=t['wm'][2],
        BAR1=hx(.36, .09, a), BAR2=hx(.58, .14, a), BAR3=hx(.78, .10, a),
        EXTRA=t.get('extra', ''), CARD_STARS=card_stars('#%02x%02x%02x' % tuple(map(int, t['spark'].split()))), CARD_HORIZON=card_horizon(hx(t['acc_L'], t['acc_C'], a)), HORIZON=horizon(hx(t['acc_L'], t['acc_C'], a), .14), HORIZON_FOCUS=horizon(hx(t['acc_L'], t['acc_C'], a), .2), STARS=stars('#%02x%02x%02x' % tuple(map(int, t['spark'].split()))), DITHER=dither(t.get('row_hex') or hx(t['acc_L'], t['acc_C'], a), t.get('row_op', .2)),
    )
    css = CSS.substitute(v)
    theme = {'version': 1, 'id': t['id'], 'name': t['name'], 'appearance': 'dark', 'colors': roles(t), 'css': css}
    p = os.path.join(OUT, t['id'] + '.json')
    json.dump(theme, open(p, 'w'), ensure_ascii=False, indent=1)
    open(os.path.join(DBG, t['id'] + '.css'), 'w').write(css)
    print(f"{t['id']:12s} css {len(css):6d} chars  (límite 50000)")

THEMES = [
 dict(id='medianoche', name='Medianoche', art='cielo-plano', tagline='cielo plano, luna de hielo',
      bg_h=262, acc_h=252, acc_L=.78, acc_C=.10, act_h=258, b_h=270, b_L=.62, b_C=.12, spark='238 244 255',
      wm=('#f2f6ff', '#7fa6f0', '#4a68c0'),
      extra=open(os.path.join(HERE, 'x-medianoche.css')).read()),
 dict(id='via-lactea', name='Vía Láctea', art='cielo-via-lactea', tagline='polvo de estrellas plateado',
      bg_h=268, acc_h=278, acc_L=.80, acc_C=.085, act_h=276, b_h=255, b_L=.70, b_C=.08, spark='255 255 255',
      wm=('#ffffff', '#a6b0f0', '#6a72c8'),
      extra=open(os.path.join(HERE, 'x-via-lactea.css')).read()),
 dict(id='aurora-azul', name='Aurora Azul', art='cielo-aurora', tagline='cortinas de luz cian',
      bg_h=255, acc_h=212, acc_L=.80, acc_C=.115, act_h=238, b_h=258, b_L=.62, b_C=.17, spark='159 236 255',
      wm=('#d4f8ff', '#52d1e9', '#3f7fe8'),
      extra=open(os.path.join(HERE, 'x-aurora.css')).read()),
 dict(id='nebulosa', name='Nebulosa', art='cielo-nebulosa', tagline='índigo con una estrella dorada',
      bg_h=272, acc_h=284, acc_L=.73, acc_C=.13, act_h=282, b_h=262, b_L=.55, b_C=.14, spark='255 212 128',
      spark_h=82, cursor=o(.85, .12, 82),
      wm=('#ece6ff', '#8c7cf0', '#5a4ac8'),
      extra=open(os.path.join(HERE, 'x-nebulosa.css')).read()),
]

if __name__ == '__main__':
    for t in THEMES: build(t)
