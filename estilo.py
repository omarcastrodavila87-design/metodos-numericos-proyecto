"""Estilo visual de SignalLab Numérico: fondo y banner de la FIEE-UNMSM.

Fondo: si en el repositorio hay una imagen `fondo_fiee.jpg` (o .jpeg / .png) se usa como fondo;
si no, se usa un fondo de circuitos y ondas generado por código.
Logo: si hay un `logo_fiee.png`, aparece en el banner."""
import base64
import math
import random
import re
from pathlib import Path

import streamlit as st

CARPETA = Path(__file__).parent
COLOR_BANNER = "#0b2a5b"   # azul del banner y de las líneas del fondo (cámbialo si quieres)
COLOR_ACENTO = "#c8102e"   # franja de acento del banner
OPACIDAD_PANEL = 0.90      # opacidad del recuadro blanco del contenido (más bajo = se ve más el fondo)
ANCHO_MAX = "1200px"       # ancho máximo del contenido; a los lados se ve el fondo
MAX_BYTES = 1_500_000      # una imagen más pesada se ignora para que la página cargue rápido
MIMES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}


def _archivo(nombres):
    for n in nombres:
        ruta = CARPETA / n
        if ruta.exists() and ruta.stat().st_size <= MAX_BYTES:
            return ruta
    return None


def _uri(ruta):
    return f"data:{MIMES[ruta.suffix.lower()]};base64," + base64.b64encode(ruta.read_bytes()).decode()


def _svg_fondo(color):
    """Fondo propio: degradado azul con ondas senoidales y pistas de circuito claras, y marca de agua FIEE · UNMSM."""
    w, h = 1600, 900
    s = [f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{color}"/>'
         '<stop offset="1" stop-color="#1c5fb4"/></linearGradient></defs>',
         f'<rect width="{w}" height="{h}" fill="url(#g)"/>']
    for amp, fase, y0, op in [(60, 0, 170, .38), (40, 1.3, 330, .26), (85, 2.1, 640, .32), (35, .6, 790, .24)]:
        pts = " ".join(f"{x},{y0 + amp * math.sin(x / 90 + fase):.1f}" for x in range(0, w + 1, 20))
        s.append(f'<polyline points="{pts}" fill="none" stroke="#ffffff" stroke-width="3" opacity="{op}"/>')
    rng = random.Random(7)
    for _ in range(30):
        x, y = rng.randrange(0, w, 50), rng.randrange(0, h, 50)
        pts = [(x, y)]
        for _ in range(rng.randint(2, 4)):
            if rng.random() < .5:
                x += rng.choice([-1, 1]) * rng.randrange(50, 250, 50)
            else:
                y += rng.choice([-1, 1]) * rng.randrange(50, 200, 50)
            pts.append((x, y))
        d = " ".join(f"{a},{b}" for a, b in pts)
        s.append(f'<polyline points="{d}" fill="none" stroke="#ffffff" stroke-width="2.5" opacity=".30"/>')
        s.append(f'<circle cx="{pts[-1][0]}" cy="{pts[-1][1]}" r="7" fill="none" stroke="#ffffff" stroke-width="2.5" opacity=".45"/>')
    s.append(f'<text x="{w - 40}" y="{h - 45}" text-anchor="end" font-family="Georgia, serif" font-size="130" '
             'font-weight="bold" fill="#ffffff" opacity=".12">FIEE · UNMSM</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice">{"".join(s)}</svg>'
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


@st.cache_data(show_spinner=False)
def _css():
    foto = _archivo(["fondo_fiee.jpg", "fondo_fiee.jpeg", "fondo_fiee.png"])
    imagen = _uri(foto) if foto else _svg_fondo(COLOR_BANNER)
    velo, velo_osc = (".20", ".40") if foto else ("0", "0")     # una foto lleva un velo leve; el diseño propio, ninguno
    css = """
    :root { --img: url("__IMG__"); --velo: rgba(255,255,255,__VELO__); --panel: rgba(255,255,255,__PANEL__); }
    @media (prefers-color-scheme: dark) { :root { --velo: rgba(0,0,0,__VELOOSC__); --panel: rgba(14,17,23,__PANEL__); } }
    .stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
      background-image: linear-gradient(var(--velo), var(--velo)), var(--img) !important;
      background-size: cover !important; background-position: center !important;
      background-repeat: no-repeat !important; background-attachment: fixed !important; }
    [data-testid="stHeader"], [data-testid="stMain"], section.main { background: transparent !important; }
    .stApp .block-container, [data-testid="stMainBlockContainer"] {
      background: var(--panel) !important; border-radius: 14px; max-width: __ANCHO__ !important;
      padding: 1.2rem 2rem 2rem !important; margin: 1rem auto !important; }
    [data-testid="stSidebar"] { background: var(--panel) !important; }
    [data-testid="stSidebar"] > div:first-child { background: transparent !important; }
    .fiee-banner { display: flex; align-items: center; gap: 1.1rem; padding: 1rem 1.4rem; margin-bottom: .8rem;
                   border-radius: 14px; border-left: 8px solid __ACENTO__; color: #fff;
                   background: linear-gradient(100deg, __BANNER__, #14468f); box-shadow: 0 4px 14px rgba(0,0,0,.25); }
    .fiee-banner img { height: 76px; border-radius: 8px; background: #fff; padding: 4px; }
    .fiee-uni { font-size: .82rem; letter-spacing: .03em; opacity: .9; }
    .fiee-fac { font-size: 1.05rem; font-weight: 600; }
    .fiee-titulo { font-size: 2rem; font-weight: 800; line-height: 1.15; margin-top: .25rem; }
    .fiee-sub { font-size: .95rem; opacity: .92; }
    """
    css = css.replace("__IMG__", imagen).replace("__VELO__", velo).replace("__VELOOSC__", velo_osc).replace("__PANEL__", str(OPACIDAD_PANEL)).replace("__ANCHO__", ANCHO_MAX).replace("__ACENTO__", COLOR_ACENTO).replace("__BANNER__", COLOR_BANNER)
    return "<style>" + re.sub(r"\s+", " ", css) + "</style>"


def aplicar_fondo():
    st.markdown(_css(), unsafe_allow_html=True)


def banner(titulo, subtitulo):
    logo = _archivo(["logo_fiee.png"])
    img = f'<img src="{_uri(logo)}" alt="FIEE">' if logo else ""
    st.markdown(
        f'<div class="fiee-banner">{img}<div>'
        '<div class="fiee-uni">Universidad Nacional Mayor de San Marcos · Universidad del Perú, Decana de América</div>'
        '<div class="fiee-fac">Facultad de Ingeniería Electrónica y Eléctrica (FIEE)</div>'
        f'<div class="fiee-titulo">{titulo}</div><div class="fiee-sub">{subtitulo}</div>'
        '</div></div>', unsafe_allow_html=True)
