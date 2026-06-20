import io
import os
import zipfile
import hashlib
import math
import random
from typing import List, Dict, Tuple, Optional

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

# ═══════════════════════════════════════════════════════════════════
# 🔐 SECURITY SETTINGS
# ═══════════════════════════════════════════════════════════════════
APP_PASSWORD = "KDPSTORY2026"
BRAND_NAME = "KDPEasy Studio"
TOOL_NAME = "Story Composer"
WELCOME_MESSAGE = "Welcome, VIP Storyteller!"
# ═══════════════════════════════════════════════════════════════════

MAX_PAGES = 60
PREVIEW_LONG_EDGE = 700

KDP_SIZES: Dict[str, Tuple[float, float]] = {
    "8.5 × 8.5 in (Square — kids classic)":  (8.5, 8.5),
    "8 × 10 in (Picture book)":              (8.0, 10.0),
    "8.5 × 11 in (Letter)":                  (8.5, 11.0),
    "7 × 10 in (Mid picture book)":          (7.0, 10.0),
    "6 × 9 in (Chapter book)":               (6.0, 9.0),
    "A4 (210 × 297 mm)":                     (8.27, 11.69),
    "A5 (148 × 210 mm)":                     (5.83, 8.27),
}

LAYOUTS = {
    "A — Image top, text bottom":         "top",
    "B — Image left, text right":         "left",
    "C — Full-bleed image, text overlay": "fullbleed",
    "D — Oval image, text below":         "oval",
}

# Fairy-tale colors
FRAME_COLOR = (102, 76, 142)       # deep purple
STAR_COLOR  = (245, 200, 80)       # soft gold
TEXT_COLOR  = (45, 35, 70)         # dark indigo
SUBTLE_BG   = (252, 248, 240)      # cream parchment
OVERLAY_TXT = (255, 255, 255)      # white for full-bleed
OVERLAY_BG  = (40, 30, 60, 170)    # semi-transparent dark (legacy default)

OVERLAY_STYLES = {
    "Auto (match the scene)":    "auto",
    "Cool dark (night, ocean)":  "cool",
    "Warm dark (sunny, autumn)": "warm",
    "Cream (light overlay)":     "cream",
    "Forest (green dark)":       "forest",
}

GOOGLE_FONTS = {
    "cinzel":        "https://raw.githubusercontent.com/google/fonts/main/ofl/cinzel/Cinzel%5Bwght%5D.ttf",
    "cormorant":     "https://raw.githubusercontent.com/google/fonts/main/ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf",
    "fredoka":       "https://raw.githubusercontent.com/google/fonts/main/ofl/fredoka/Fredoka%5Bwdth,wght%5D.ttf",
    "quicksand":     "https://raw.githubusercontent.com/google/fonts/main/ofl/quicksand/Quicksand%5Bwght%5D.ttf",
    "caveat":        "https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/Caveat%5Bwght%5D.ttf",
    "lora":          "https://raw.githubusercontent.com/google/fonts/main/ofl/lora/Lora%5Bwght%5D.ttf",
    "bangers":       "https://raw.githubusercontent.com/google/fonts/main/ofl/bangers/Bangers-Regular.ttf",
    "merriweather":  "https://raw.githubusercontent.com/google/fonts/main/ofl/merriweather/Merriweather%5Bopsz,wdth,wght%5D.ttf",
}

THEMES: Dict[str, Dict] = {
    "Classic fairy tale (dragons, magic)": {
        "drop_key": "cinzel",     "drop_weight": 800, "drop_size_mult": 3.4,
        "body_key": "cormorant",  "body_weight": 500,
    },
    "Modern children's book (3–7 yrs)": {
        "drop_key": "fredoka",    "drop_weight": 700, "drop_size_mult": 2.8,
        "body_key": "quicksand",  "body_weight": 500,
    },
    "Whimsical handwritten (bedtime)": {
        "drop_key": "caveat",     "drop_weight": 700, "drop_size_mult": 3.4,
        "body_key": "lora",       "body_weight": 400,
    },
    "Bold adventure (action, quest)": {
        "drop_key": "bangers",    "drop_weight": None, "drop_size_mult": 2.6,
        "body_key": "merriweather","body_weight": 500,
    },
}

st.set_page_config(
    page_title=f"{BRAND_NAME} — {TOOL_NAME}",
    page_icon="📖",
    layout="wide",
)

CUSTOM_CSS = """
<style>
    .main > div { padding-top: 2rem; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf3 100%); }
    .block-container { max-width: 1300px; }
    h1 { color: #1f2937; font-weight: 700; }
    h2, h3 { color: #1f2937; }
    .stButton>button {
        background-color: #4f46e5;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover { background-color: #4338ca; color: white; }
    .stDownloadButton>button {
        background-color: #10b981;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        font-weight: 700;
    }
    .stDownloadButton>button:hover { background-color: #059669; color: white; }
    div[data-testid="stFileUploader"] {
        background-color: white;
        border-radius: 12px;
        padding: 0.5rem;
        border: 2px dashed #cbd5e1;
    }
    .info-card {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #4f46e5;
        margin-bottom: 1rem;
    }
    .warn-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin-bottom: 1rem;
        color: #78350f;
    }
    .login-card {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        max-width: 480px;
        margin: 3rem auto;
        text-align: center;
    }
    .login-card h2 { color: #1f2937; margin-bottom: 0.5rem; }
    .login-card .brand {
        color: #4f46e5;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
    .pagenav {
        background: white;
        padding: 0.6rem 0.8rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #e5e7eb;
    }
    .preview-box {
        background: #ffffff;
        padding: 0.8rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .layout-tag {
        display: inline-block;
        background: #ede9fe;
        color: #4338ca;
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 🔐 Password gate
# ═══════════════════════════════════════════════════════════════════
def check_password() -> bool:
    if st.session_state.get("auth_ok"):
        return True

    st.markdown(
        f"""
        <div class="login-card">
            <div class="brand">{BRAND_NAME}</div>
            <h2>📖 {TOOL_NAME}</h2>
            <p style="color:#6b7280;margin-bottom:1.5rem;">
                Enter your VIP password to continue.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        pw = st.text_input("Password", type="password",
                           label_visibility="collapsed",
                           placeholder="Enter password…")
        ok = st.form_submit_button("🔓 Unlock", use_container_width=True)

    if ok:
        if pw == APP_PASSWORD:
            st.session_state.auth_ok = True
            st.rerun()
        else:
            st.error("❌ Wrong password. Please try again.")
    return False


if not check_password():
    st.stop()


# ═══════════════════════════════════════════════════════════════════
# 📦 Font management — download from Google Fonts and cache
# ═══════════════════════════════════════════════════════════════════
FONTS_DIR = "/tmp/kdpeasy_story_fonts"


@st.cache_resource(show_spinner="Loading fairy-tale fonts…")
def ensure_fonts() -> Dict[str, str]:
    os.makedirs(FONTS_DIR, exist_ok=True)
    paths: Dict[str, str] = {}
    for name, url in GOOGLE_FONTS.items():
        local = os.path.join(FONTS_DIR, f"{name}.ttf")
        if not os.path.exists(local) or os.path.getsize(local) < 1000:
            try:
                r = requests.get(url, timeout=15, allow_redirects=True)
                r.raise_for_status()
                with open(local, "wb") as f:
                    f.write(r.content)
            except Exception as e:
                st.warning(f"Could not download {name}: {e}. Using default font.")
                local = None
        paths[name] = local
    return paths


FONT_PATHS = ensure_fonts()


def load_font(kind: str, size: int,
              weight: Optional[int] = None) -> ImageFont.FreeTypeFont:
    path = FONT_PATHS.get(kind)
    if path and os.path.exists(path):
        try:
            font = ImageFont.truetype(path, size)
            if weight is not None:
                try:
                    font.set_variation_by_axes([weight])
                except Exception:
                    pass
            return font
        except Exception:
            pass
    return ImageFont.load_default()


# ═══════════════════════════════════════════════════════════════════
# 🎨 Drawing helpers
# ═══════════════════════════════════════════════════════════════════
def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def compute_overlay(image: Optional[Image.Image], style: str
                    ) -> Tuple[Optional[Tuple[int, int, int, int]],
                               Tuple[int, int, int]]:
    """Return (overlay_rgba_or_None, text_rgb) for the Full-bleed layout."""
    if style == "warm":
        return (55, 28, 18, 175), (255, 245, 230)
    if style == "cool":
        return (40, 30, 60, 170), (255, 255, 255)
    if style == "cream":
        return (252, 246, 228, 225), (45, 35, 70)
    if style == "forest":
        return (20, 45, 30, 175), (230, 245, 220)

    # "auto" — sample bottom 30% of the image, darken
    if image is None:
        return (40, 30, 60, 170), (255, 255, 255)
    try:
        img = image.convert("RGB")
        w, h = img.size
        crop = img.crop((0, int(h * 0.7), w, h))
        thumb = crop.resize((40, 20))
        pixels = list(thumb.getdata())
        r = sum(p[0] for p in pixels) // len(pixels)
        g = sum(p[1] for p in pixels) // len(pixels)
        b = sum(p[2] for p in pixels) // len(pixels)
        # Brightness of average colour (0..255)
        brightness = (r * 299 + g * 587 + b * 114) // 1000
        if brightness > 170:
            # Bright scene → cream overlay + dark text
            return (252, 246, 228, 220), (45, 35, 70)
        # Otherwise darken the sampled colour for a tinted dark overlay
        darken = 0.28
        dr = max(10, int(r * darken))
        dg = max(10, int(g * darken))
        db = max(10, int(b * darken))
        return (dr, dg, db, 178), (255, 250, 240)
    except Exception:
        return (40, 30, 60, 170), (255, 255, 255)


def text_width(draw: ImageDraw.ImageDraw, text: str,
               font: ImageFont.FreeTypeFont) -> int:
    if not text:
        return 0
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_height(draw: ImageDraw.ImageDraw, text: str,
                font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text or "Ag", font=font)
    return bbox[3] - bbox[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str,
              font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Greedy word wrap respecting newlines in source."""
    if not text:
        return []
    out: List[str] = []
    for paragraph in text.splitlines() or [text]:
        if not paragraph.strip():
            out.append("")
            continue
        words = paragraph.split()
        line = ""
        for w in words:
            trial = (line + " " + w).strip()
            if text_width(draw, trial, font) <= max_width:
                line = trial
            else:
                if line:
                    out.append(line)
                line = w
        if line:
            out.append(line)
    return out


def fit_image(img: Image.Image, box_w: int, box_h: int,
              mode: str = "fit") -> Image.Image:
    """Resize img to fit/fill the box and return."""
    img = ImageOps.exif_transpose(img)
    sw, sh = img.size
    if mode == "fill":
        scale = max(box_w / sw, box_h / sh)
    else:  # fit
        scale = min(box_w / sw, box_h / sh)
    new_w = max(1, int(round(sw * scale)))
    new_h = max(1, int(round(sh * scale)))
    return img.resize((new_w, new_h), Image.LANCZOS)


def paste_centered(canvas: Image.Image, img: Image.Image,
                   box: Tuple[int, int, int, int]):
    """Paste img centered inside box (left,top,right,bottom)."""
    bx, by, bx2, by2 = box
    bw, bh = bx2 - bx, by2 - by
    iw, ih = img.size
    x = bx + (bw - iw) // 2
    y = by + (bh - ih) // 2
    if img.mode == "RGBA":
        canvas.paste(img, (x, y), img)
    else:
        canvas.paste(img, (x, y))


def draw_decorative_frame(canvas: Image.Image, frame_style: str,
                          margin: int, color: Tuple[int, int, int]):
    """Draw a delicate fairy-tale border around the page."""
    if frame_style == "none":
        return
    draw = ImageDraw.Draw(canvas, "RGBA")
    w, h = canvas.size
    inner = margin

    if frame_style in ("thin", "double", "ornate"):
        # outer thin line
        line_w = max(2, int(w / 700))
        draw.rectangle(
            [inner, inner, w - inner, h - inner],
            outline=color + (220,),
            width=line_w,
        )
    if frame_style in ("double", "ornate"):
        gap = max(6, int(w / 180))
        draw.rectangle(
            [inner + gap * 2, inner + gap * 2,
             w - inner - gap * 2, h - inner - gap * 2],
            outline=color + (170,),
            width=max(1, line_w // 2),
        )
    if frame_style == "ornate":
        # corner sparkles
        for corner in [(inner, inner),
                       (w - inner, inner),
                       (inner, h - inner),
                       (w - inner, h - inner)]:
            draw_star(draw, corner, int(w / 60), STAR_COLOR)
        # midpoint accents
        for mid in [(w // 2, inner),
                    (w // 2, h - inner),
                    (inner, h // 2),
                    (w - inner, h // 2)]:
            draw_star(draw, mid, int(w / 110), STAR_COLOR)


def draw_star(draw: ImageDraw.ImageDraw, center: Tuple[int, int],
              size: int, color: Tuple[int, int, int]):
    cx, cy = center
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size / 2.4
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=color + (235,))


def draw_text_block(canvas: Image.Image,
                    text: str,
                    box: Tuple[int, int, int, int],
                    body_font: ImageFont.FreeTypeFont,
                    dropcap_font: Optional[ImageFont.FreeTypeFont],
                    color: Tuple[int, int, int],
                    line_spacing: float = 1.35,
                    use_dropcap: bool = True,
                    align: str = "left") -> int:
    """Render text within box. Returns y position after last line."""
    draw = ImageDraw.Draw(canvas)
    bx, by, bx2, by2 = box
    box_w = bx2 - bx

    if not text.strip():
        return by

    if use_dropcap and dropcap_font is not None and text.strip():
        first = text.strip()[0]
        rest = text.strip()[1:]
    else:
        first = ""
        rest = text.strip()

    # measure dropcap
    dc_w, dc_h = 0, 0
    if first:
        bbox = draw.textbbox((0, 0), first, font=dropcap_font)
        dc_w = bbox[2] - bbox[0]
        dc_h = bbox[3] - bbox[1]

    body_line_h = int(text_height(draw, "Ag", body_font) * line_spacing)
    dropcap_lines = max(1, int(math.ceil(dc_h / body_line_h))) if first else 0
    indent = dc_w + max(10, int(box_w / 60)) if first else 0

    # First wrap rest assuming reduced width for `dropcap_lines` lines,
    # then full width.
    # Strategy: wrap to narrow width, then re-flow leftover lines to full width.
    narrow_w = box_w - indent
    full_lines = wrap_text(draw, rest, body_font, narrow_w)
    head = full_lines[:dropcap_lines]
    tail_text = " ".join(full_lines[dropcap_lines:])
    tail_lines = wrap_text(draw, tail_text, body_font, box_w) if tail_text else []

    # draw dropcap
    if first:
        # Vertical offset so the cap aligns with body cap-height roughly
        body_cap_bbox = draw.textbbox((0, 0), "H", font=body_font)
        body_cap_top = body_cap_bbox[1]
        dc_top = bbox[1]
        # Align tops
        y_dc = by - dc_top + body_cap_top
        draw.text((bx, y_dc), first, fill=color, font=dropcap_font)

    # draw head lines (indented past dropcap)
    y = by
    for ln in head:
        draw.text((bx + indent, y), ln, fill=color, font=body_font)
        y += body_line_h

    # draw tail lines (full width)
    for ln in tail_lines:
        if y + body_line_h > by2:
            break
        draw.text((bx, y), ln, fill=color, font=body_font)
        y += body_line_h

    return y


# ═══════════════════════════════════════════════════════════════════
# 🖼️ Layout renderers
# ═══════════════════════════════════════════════════════════════════
def render_layout_top(canvas: Image.Image, image: Optional[Image.Image],
                      text: str, settings: Dict):
    """Layout A — image top, text bottom."""
    w, h = canvas.size
    m = settings["margin"]
    text_pct = 0.32  # ~1/3 for text

    img_box = (m, m, w - m, int(h * (1 - text_pct)) - m // 2)
    txt_box = (m + settings["text_pad"], int(h * (1 - text_pct)) + m // 2,
               w - m - settings["text_pad"], h - m - settings["text_pad"])

    if image:
        bw = img_box[2] - img_box[0]
        bh = img_box[3] - img_box[1]
        fitted = fit_image(image, bw, bh, "fit")
        paste_centered(canvas, fitted.convert("RGB"), img_box)
    else:
        ImageDraw.Draw(canvas).rectangle(img_box, fill=SUBTLE_BG,
                                          outline=FRAME_COLOR, width=2)

    draw_text_block(canvas, text, txt_box,
                    settings["body_font"], settings["dropcap_font"],
                    TEXT_COLOR, settings["line_spacing"],
                    settings["use_dropcap"])


def render_layout_left(canvas: Image.Image, image: Optional[Image.Image],
                       text: str, settings: Dict):
    """Layout B — image left, text right."""
    w, h = canvas.size
    m = settings["margin"]

    img_box = (m, m, int(w * 0.45), h - m)
    txt_box = (int(w * 0.45) + m // 2 + settings["text_pad"],
               m + settings["text_pad"],
               w - m - settings["text_pad"],
               h - m - settings["text_pad"])

    if image:
        bw = img_box[2] - img_box[0]
        bh = img_box[3] - img_box[1]
        fitted = fit_image(image, bw, bh, "fit")
        paste_centered(canvas, fitted.convert("RGB"), img_box)
    else:
        ImageDraw.Draw(canvas).rectangle(img_box, fill=SUBTLE_BG,
                                          outline=FRAME_COLOR, width=2)

    draw_text_block(canvas, text, txt_box,
                    settings["body_font"], settings["dropcap_font"],
                    TEXT_COLOR, settings["line_spacing"],
                    settings["use_dropcap"])


def render_layout_fullbleed(canvas: Image.Image, image: Optional[Image.Image],
                            text: str, settings: Dict):
    """Layout C — full-bleed image with text overlay at bottom."""
    w, h = canvas.size

    if image:
        fitted = fit_image(image, w, h, "fill")
        paste_centered(canvas, fitted.convert("RGB"), (0, 0, w, h))
    else:
        ImageDraw.Draw(canvas).rectangle((0, 0, w, h), fill=SUBTLE_BG)

    # Text overlay panel
    if text.strip():
        pad = settings["text_pad"]
        overlay_bg = settings.get("overlay_bg", OVERLAY_BG)
        overlay_txt = settings.get("overlay_txt", OVERLAY_TXT)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        # measure text height first
        body_font = settings["body_font"]
        line_h = int(text_height(d, "Ag", body_font) * settings["line_spacing"])
        tmp_lines = wrap_text(d, text, body_font, w - 4 * pad)
        block_h = line_h * (len(tmp_lines) + 1) + pad * 2
        panel_top = h - block_h - settings["margin"]
        d.rectangle([settings["margin"], panel_top,
                     w - settings["margin"], h - settings["margin"]],
                    fill=overlay_bg)
        canvas.paste(overlay, (0, 0), overlay)

        txt_box = (settings["margin"] + pad, panel_top + pad,
                   w - settings["margin"] - pad,
                   h - settings["margin"] - pad)
        draw_text_block(canvas, text, txt_box,
                        body_font, settings["dropcap_font"],
                        overlay_txt, settings["line_spacing"],
                        settings["use_dropcap"])


def render_layout_oval(canvas: Image.Image, image: Optional[Image.Image],
                       text: str, settings: Dict):
    """Layout D — oval image at top, text below."""
    w, h = canvas.size
    m = settings["margin"]
    text_pct = 0.32

    img_area_h = int(h * (1 - text_pct)) - m
    oval_w = int(w * 0.78)
    oval_h = int(img_area_h * 0.92)
    oval_x = (w - oval_w) // 2
    oval_y = m + (img_area_h - oval_h) // 2

    if image:
        fitted = fit_image(image, oval_w, oval_h, "fill")
        # crop center to oval_w × oval_h
        fw, fh = fitted.size
        crop_box = ((fw - oval_w) // 2, (fh - oval_h) // 2,
                    (fw - oval_w) // 2 + oval_w,
                    (fh - oval_h) // 2 + oval_h)
        fitted = fitted.crop(crop_box).convert("RGB")
        # apply oval mask
        mask = Image.new("L", (oval_w, oval_h), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, oval_w, oval_h), fill=255)
        canvas.paste(fitted, (oval_x, oval_y), mask)
        # oval outline
        ImageDraw.Draw(canvas).ellipse(
            (oval_x, oval_y, oval_x + oval_w, oval_y + oval_h),
            outline=FRAME_COLOR, width=max(3, int(w / 300)),
        )
    else:
        ImageDraw.Draw(canvas).ellipse(
            (oval_x, oval_y, oval_x + oval_w, oval_y + oval_h),
            fill=SUBTLE_BG, outline=FRAME_COLOR,
            width=max(3, int(w / 300)),
        )

    # tiny stars around the oval
    d = ImageDraw.Draw(canvas, "RGBA")
    for _ in range(8):
        angle = random.uniform(0, 2 * math.pi)
        rx = oval_w / 2 + random.randint(20, 50)
        ry = oval_h / 2 + random.randint(20, 50)
        cx = int(oval_x + oval_w / 2 + rx * math.cos(angle))
        cy = int(oval_y + oval_h / 2 + ry * math.sin(angle))
        draw_star(d, (cx, cy), max(6, int(w / 160)), STAR_COLOR)

    txt_box = (m + settings["text_pad"],
               oval_y + oval_h + m,
               w - m - settings["text_pad"],
               h - m - settings["text_pad"])
    draw_text_block(canvas, text, txt_box,
                    settings["body_font"], settings["dropcap_font"],
                    TEXT_COLOR, settings["line_spacing"],
                    settings["use_dropcap"])


LAYOUT_RENDERERS = {
    "top":       render_layout_top,
    "left":      render_layout_left,
    "fullbleed": render_layout_fullbleed,
    "oval":      render_layout_oval,
}


# ═══════════════════════════════════════════════════════════════════
# 🏗️ Page composer
# ═══════════════════════════════════════════════════════════════════
def compose_page(page_w_in: float, page_h_in: float, dpi: int,
                 layout: str, image_bytes: Optional[bytes],
                 text: str, frame_style: str,
                 use_dropcap: bool, font_scale: float,
                 line_spacing: float,
                 theme_name: str = "Classic fairy tale (dragons, magic)",
                 overlay_style: str = "auto"
                 ) -> Image.Image:
    w_px = int(round(page_w_in * dpi))
    h_px = int(round(page_h_in * dpi))

    canvas = Image.new("RGB", (w_px, h_px), SUBTLE_BG)

    # Margins scale with page width
    margin = int(w_px * 0.06)
    text_pad = int(w_px * 0.025)

    t = THEMES.get(theme_name, list(THEMES.values())[0])
    base_size = int(w_px * 0.024 * font_scale)
    body_font = load_font(t["body_key"], base_size, weight=t["body_weight"])
    dropcap_font = load_font(t["drop_key"],
                              int(base_size * t["drop_size_mult"]),
                              weight=t["drop_weight"])

    settings = {
        "margin": margin,
        "text_pad": text_pad,
        "body_font": body_font,
        "dropcap_font": dropcap_font,
        "use_dropcap": use_dropcap,
        "line_spacing": line_spacing,
    }

    image = None
    if image_bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes))
        except Exception:
            image = None

    overlay_bg, overlay_txt = compute_overlay(image, overlay_style)
    settings["overlay_bg"] = overlay_bg
    settings["overlay_txt"] = overlay_txt

    renderer = LAYOUT_RENDERERS.get(layout, render_layout_top)
    renderer(canvas, image, text, settings)

    if layout != "fullbleed":
        draw_decorative_frame(canvas, frame_style,
                              max(margin // 2, int(w_px * 0.025)),
                              FRAME_COLOR)

    return canvas


@st.cache_data(show_spinner=False, max_entries=120)
def compose_page_cached(page_w_in: float, page_h_in: float, dpi: int,
                        layout: str, image_bytes: Optional[bytes],
                        text: str, frame_style: str,
                        use_dropcap: bool, font_scale: float,
                        line_spacing: float,
                        theme_name: str = "Classic fairy tale (dragons, magic)",
                        overlay_style: str = "auto",
                        _v: int = 3) -> bytes:
    img = compose_page(page_w_in, page_h_in, dpi, layout, image_bytes,
                       text, frame_style, use_dropcap, font_scale,
                       line_spacing, theme_name, overlay_style)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def make_preview(png_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(png_bytes))
    w, h = img.size
    long_edge = max(w, h)
    if long_edge > PREVIEW_LONG_EDGE:
        scale = PREVIEW_LONG_EDGE / long_edge
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=85)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════
# Header
# ═══════════════════════════════════════════════════════════════════
hl, hr = st.columns([5, 1])
with hl:
    st.markdown(
        f"<h1>📖 {TOOL_NAME}</h1>"
        f"<p style='color:#6b7280;margin-top:-0.5rem;'>"
        f"{BRAND_NAME} — {WELCOME_MESSAGE}</p>",
        unsafe_allow_html=True,
    )
with hr:
    st.write("")
    if st.button("Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# Sidebar — book-wide settings
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 📐 Book settings")
    size_label = st.selectbox("KDP page size", list(KDP_SIZES.keys()), index=0)
    page_w_in, page_h_in = KDP_SIZES[size_label]

    dpi = st.number_input("Output DPI (KDP needs 300)",
                          min_value=200, max_value=600, value=300, step=50)

    st.markdown("### ✨ Style")
    frame_style = st.selectbox(
        "Decorative frame",
        ["ornate", "double", "thin", "none"],
        index=0,
        format_func=lambda s: {
            "ornate": "Ornate — border + stars (recommended)",
            "double": "Double line — elegant",
            "thin":   "Thin line — minimal",
            "none":   "None — clean",
        }[s],
    )

    theme_name = st.selectbox(
        "Font theme",
        list(THEMES.keys()),
        index=0,
        help="Pairs a fancy drop-cap font with a readable body font.",
    )
    theme = THEMES[theme_name]

    st.caption(
        "💡 Drop cap is now set **per-page** below the layout picker — "
        "by convention, only the first page of a story has one."
    )

    font_scale = st.slider("Font size scale", 0.7, 1.6, 1.0, 0.05)
    line_spacing = st.slider("Line spacing", 1.1, 1.8, 1.35, 0.05)

    st.markdown("---")
    book_title = st.text_input("Book title (used in filenames)",
                               value="my-storybook")

    st.markdown(
        '<div class="info-card" style="font-size:0.85rem;">'
        "💡 <b>Next step:</b> after exporting PNGs, drop them into the "
        "<b>KDPEasy PDF Builder</b> to get your KDP-ready PDF."
        "</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════
# Session state — pages
# ═══════════════════════════════════════════════════════════════════
if "pages" not in st.session_state:
    st.session_state.pages = [{
        "text": "",
        "layout": "top",
        "image_bytes": None,
        "image_name": "",
        "use_dropcap": True,   # first page defaults to having a drop cap
        "overlay_style": "auto",
    }]
if "active_page" not in st.session_state:
    st.session_state.active_page = 0


# Migrate any older session entries that pre-date new fields
for _p in st.session_state.pages:
    if "use_dropcap" not in _p:
        _p["use_dropcap"] = False
    if "overlay_style" not in _p:
        _p["overlay_style"] = "auto"


def add_page():
    if len(st.session_state.pages) >= MAX_PAGES:
        st.warning(f"Limit is {MAX_PAGES} pages.")
        return
    # inherit current layout for consistency
    last_layout = st.session_state.pages[st.session_state.active_page]["layout"]
    st.session_state.pages.append({
        "text": "",
        "layout": last_layout,
        "image_bytes": None,
        "image_name": "",
        "use_dropcap": False,   # new pages default to no drop cap
        "overlay_style": "auto",
    })
    st.session_state.active_page = len(st.session_state.pages) - 1


def delete_page(idx: int):
    if len(st.session_state.pages) <= 1:
        st.warning("You must keep at least one page.")
        return
    st.session_state.pages.pop(idx)
    st.session_state.active_page = max(0, min(idx,
                                              len(st.session_state.pages) - 1))


def move_page(idx: int, delta: int):
    new_idx = idx + delta
    if 0 <= new_idx < len(st.session_state.pages):
        st.session_state.pages[idx], st.session_state.pages[new_idx] = \
            st.session_state.pages[new_idx], st.session_state.pages[idx]
        st.session_state.active_page = new_idx


# ═══════════════════════════════════════════════════════════════════
# Page navigation tabs
# ═══════════════════════════════════════════════════════════════════
st.markdown("### 📑 Pages")
N = len(st.session_state.pages)
nav_cols = st.columns([1] * min(N, 12) + [1])
for i in range(N):
    col = nav_cols[i % 12] if N > 12 else nav_cols[i]
    is_active = (i == st.session_state.active_page)
    label = f"▶ {i+1}" if is_active else f"{i+1}"
    if col.button(label, key=f"nav_{i}", use_container_width=True):
        st.session_state.active_page = i
        st.rerun()
# Add page button on last column
add_col = nav_cols[-1] if N <= 12 else nav_cols[(N) % 12]
if add_col.button("➕", key="nav_add", use_container_width=True,
                   help="Add new page"):
    add_page()
    st.rerun()

st.caption(f"Page **{st.session_state.active_page + 1}** of **{N}**  •  "
           f"Use ➕ to add. Reorder / delete with buttons below.")


# ═══════════════════════════════════════════════════════════════════
# Editor + live preview
# ═══════════════════════════════════════════════════════════════════
edit_col, preview_col = st.columns([1.05, 1])

page = st.session_state.pages[st.session_state.active_page]

with edit_col:
    st.markdown("#### ✍️ Story text")
    new_text = st.text_area(
        "Page text",
        value=page["text"],
        height=180,
        label_visibility="collapsed",
        placeholder="Each evening, when the sky deepened to velvet blue, "
                    "Ember padded softly through the floating library…",
        key=f"text_{st.session_state.active_page}",
    )
    if new_text != page["text"]:
        page["text"] = new_text

    st.markdown("#### 🖼️ Page image")
    up = st.file_uploader(
        "Upload image for this page",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=False,
        label_visibility="collapsed",
        key=f"img_{st.session_state.active_page}",
    )
    if up is not None:
        data = up.getvalue()
        if data and data != page["image_bytes"]:
            page["image_bytes"] = data
            page["image_name"] = up.name
    if page["image_bytes"]:
        st.caption(f"📎 {page['image_name'] or 'image attached'}")
        if st.button("Remove image", key=f"rm_img_{st.session_state.active_page}"):
            page["image_bytes"] = None
            page["image_name"] = ""
            st.rerun()

    st.markdown("#### 🎨 Layout")
    layout_label = st.radio(
        "Layout",
        list(LAYOUTS.keys()),
        index=list(LAYOUTS.values()).index(page["layout"]),
        label_visibility="collapsed",
        key=f"layout_{st.session_state.active_page}",
    )
    page["layout"] = LAYOUTS[layout_label]

    page["use_dropcap"] = st.checkbox(
        "✨ Drop cap on this page",
        value=page.get("use_dropcap", False),
        key=f"dropcap_{st.session_state.active_page}",
        help="Only check this for chapter openings — never every page.",
    )

    # Overlay style is only meaningful for Full-bleed layout (C)
    if page["layout"] == "fullbleed":
        ovr_labels = list(OVERLAY_STYLES.keys())
        ovr_values = list(OVERLAY_STYLES.values())
        try:
            ovr_idx = ovr_values.index(page.get("overlay_style", "auto"))
        except ValueError:
            ovr_idx = 0
        ovr_label = st.selectbox(
            "🎨 Text overlay tone",
            ovr_labels,
            index=ovr_idx,
            key=f"overlay_{st.session_state.active_page}",
            help="Tints the text panel to match the scene mood. "
                 "Auto samples the image for you.",
        )
        page["overlay_style"] = OVERLAY_STYLES[ovr_label]

    st.markdown("#### 🗂️ Page actions")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if st.button("⬆️ Move up", use_container_width=True,
                     disabled=st.session_state.active_page == 0):
            move_page(st.session_state.active_page, -1)
            st.rerun()
    with a2:
        if st.button("⬇️ Move down", use_container_width=True,
                     disabled=st.session_state.active_page >= N - 1):
            move_page(st.session_state.active_page, +1)
            st.rerun()
    with a3:
        if st.button("📋 Duplicate", use_container_width=True):
            new_p = dict(page)
            st.session_state.pages.insert(st.session_state.active_page + 1,
                                          new_p)
            st.session_state.active_page += 1
            st.rerun()
    with a4:
        if st.button("🗑️ Delete", use_container_width=True,
                     disabled=N <= 1):
            delete_page(st.session_state.active_page)
            st.rerun()


with preview_col:
    st.markdown("#### 👀 Live preview")
    st.markdown(
        f'<div class="layout-tag">{layout_label}</div>',
        unsafe_allow_html=True,
    )
    try:
        png = compose_page_cached(
            page_w_in, page_h_in, int(dpi), page["layout"],
            page["image_bytes"], page["text"], frame_style,
            page.get("use_dropcap", False),
            float(font_scale), float(line_spacing),
            theme_name,
            page.get("overlay_style", "auto"),
        )
        preview_bytes = make_preview(png)
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.image(preview_bytes, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.caption(
            f"Output PNG: {int(page_w_in*dpi)} × {int(page_h_in*dpi)} px  •  "
            f"{page_w_in}\" × {page_h_in}\" @ {dpi} DPI"
        )
    except Exception as e:
        st.error(f"Preview error: {e}")


# ═══════════════════════════════════════════════════════════════════
# Export ZIP
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 📦 Export all pages")

ex_col1, ex_col2 = st.columns([1, 2])
with ex_col1:
    do_export = st.button(f"📦 Build {N}-page PNG ZIP",
                          use_container_width=True)
with ex_col2:
    st.caption(
        f"Output: **{N} PNGs** at {int(page_w_in*dpi)} × {int(page_h_in*dpi)} px"
        f"  •  Next: upload these to **KDPEasy PDF Builder** to get the final PDF."
    )

if do_export:
    progress = st.progress(0.0, text="Composing pages…")
    try:
        slug = "".join(c if c.isalnum() or c in "-_" else "-"
                        for c in (book_title or "storybook")).strip("-").lower()
        if not slug:
            slug = "storybook"

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w",
                              compression=zipfile.ZIP_DEFLATED) as zf:
            for i, p in enumerate(st.session_state.pages):
                png = compose_page_cached(
                    page_w_in, page_h_in, int(dpi), p["layout"],
                    p["image_bytes"], p["text"], frame_style,
                    p.get("use_dropcap", False),
                    float(font_scale), float(line_spacing),
                    theme_name,
                    p.get("overlay_style", "auto"),
                )
                zf.writestr(f"{slug}-page-{i+1:03d}.png", png)
                progress.progress((i + 1) / N,
                                  text=f"Composing pages… {i+1}/{N}")
        zip_bytes = zip_buf.getvalue()
        progress.progress(1.0, text="Done!")
        size_mb = len(zip_bytes) / (1024 * 1024)
        st.success(f"✅ {N} pages packed — {size_mb:.1f} MB ZIP ready.")
        st.download_button(
            label=f"⬇️ Download {slug}-pages.zip",
            data=zip_bytes,
            file_name=f"{slug}-pages.zip",
            mime="application/zip",
            use_container_width=True,
        )
    except Exception as e:
        progress.empty()
        st.error(f"❌ Could not export: {e}")


# ═══════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#9ca3af;font-size:0.85rem;'>"
    f"{BRAND_NAME} — {TOOL_NAME}  •  Made with ❤️ for KDP storytellers"
    f"</div>",
    unsafe_allow_html=True,
)
