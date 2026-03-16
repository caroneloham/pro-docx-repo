#!/usr/bin/env python3
"""
generate_cover.py — Générateur de page de garde académique/professionnelle
Design sobre, sérieux, niveau mémoire d'ingénieur / rapport professionnel.
"""

from PIL import Image, ImageDraw, ImageFont
import sys, os

CHARTES = {
    "classique": {
        "name": "Classique", "primary": "#1B2A4A", "secondary": "#C8102E",
        "accent": "#4A6FA5", "light": "#F5F6F8", "text": "#2D2D2D",
        "bg_header": "#1B2A4A", "line": "#C8102E",
    },
    "neutre": {
        "name": "Professionnel Neutre", "primary": "#2C3E50", "secondary": "#34495E",
        "accent": "#5D6D7E", "light": "#F2F3F4", "text": "#2C3E50",
        "bg_header": "#2C3E50", "line": "#5D6D7E",
    },
    "cyber": {
        "name": "Cybersécurité", "primary": "#1A1A2E", "secondary": "#16213E",
        "accent": "#0F3460", "light": "#EDF2F7", "text": "#1A202C",
        "bg_header": "#1A1A2E", "line": "#E94560",
    },
    "technique": {
        "name": "Rapport Technique", "primary": "#263238", "secondary": "#37474F",
        "accent": "#546E7A", "light": "#ECEFF1", "text": "#263238",
        "bg_header": "#263238", "line": "#0277BD",
    },
}

TYPE_LABELS = {
    "audit": "Rapport d'audit cybersécurité",
    "memoire": "Mémoire professionnel",
    "td": "Compte-rendu de TP",
    "rapport": "Rapport technique",
}

W, H = 2480, 3508

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _font(size, variant="serif-bold"):
    m = {
        "serif-bold": ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                       "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"],
        "serif": ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                  "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"],
        "serif-italic": ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"],
        "sans": ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
        "sans-bold": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    }
    for p in m.get(variant, m["serif"]):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def _tw(d, t, f):
    b = d.textbbox((0,0), t, font=f); return b[2]-b[0]

def _tc(d, y, t, f, fill):
    d.text(((W - _tw(d, t, f)) // 2, y), t, font=f, fill=fill)

def _tcml(d, y, t, f, fill, mw):
    words, lines, cur = t.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if _tw(d, test, f) <= mw: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    lh = int(f.size * 1.35)
    for l in lines: _tc(d, y, l, f, fill); y += lh
    return y


def generate_cover(config, output_path="cover.png"):
    ch = CHARTES.get(config.get("charte", "classique"), CHARTES["classique"])
    dt = config.get("type", "rapport")
    c = {k: hex_to_rgb(v) for k, v in ch.items() if k != "name"}
    white = (255, 255, 255)
    
    img = Image.new('RGB', (W, H), white)
    d = ImageDraw.Draw(img)
    mx = 240
    cw = W - 2 * mx

    # ── Double filet supérieur ──
    y = 180
    d.rectangle([mx, y, W-mx, y+6], fill=c["bg_header"])
    d.rectangle([mx, y+14, W-mx, y+16], fill=c["bg_header"])

    # ── Type de document ──
    y = 300
    _tc(d, y, TYPE_LABELS.get(dt, "Document").upper(), _font(38, "sans"), c["accent"])
    y = 365
    d.rectangle([(W-200)//2, y, (W+200)//2, y+3], fill=c["line"])

    # ── Titre ──
    y = 460
    y = _tcml(d, y, config.get("titre", "Document"), _font(115, "serif-bold"), c["primary"], cw)

    # ── Sous-titre ──
    st = config.get("sousTitre", "")
    if st:
        y += 30
        y = _tcml(d, y, st, _font(50, "serif-italic"), c["accent"], cw)

    # ── Filet central ──
    y += 60
    d.rectangle([mx+200, y, W-mx-200, y+4], fill=c["line"])

    # ── Auteur ──
    y += 80
    lbl = {"memoire": "Présenté par", "audit": "Réalisé par"}.get(dt, "Rédigé par")
    _tc(d, y, lbl, _font(34, "sans"), c["accent"])
    y += 60
    _tc(d, y, config.get("auteur", ""), _font(54, "serif-bold"), c["primary"])
    y += 90

    # ── Bloc infos ──
    info = []
    if dt == "td":
        for k, l in [("formation","Formation"),("module","Module"),("enseignant","Enseignant")]:
            if config.get(k): info.append((l, config[k]))
    elif dt == "memoire":
        for k, l in [("formation","Formation"),("organisme","Organisme"),("entreprise","Entreprise d'accueil"),
                      ("tuteurAcademique","Tuteur académique"),("tuteurEntreprise","Tuteur entreprise"),
                      ("anneeAcademique","Année académique")]:
            if config.get(k): info.append((l, config[k]))
    elif dt == "audit":
        for k, l in [("organisme","Organisme"),("entreprise","Entité auditée"),("referentiel","Référentiel")]:
            if config.get(k): info.append((l, config[k]))
    else:
        for k, l in [("formation","Formation / Poste"),("organisme","Organisme"),("entreprise","Entreprise")]:
            if config.get(k): info.append((l, config[k]))

    if info:
        fl = _font(32, "sans-bold")
        fv = _font(32, "sans")
        mlw = max(_tw(d, f"{l} :", fl) for l, _ in info)
        
        y += 30
        bp = 30
        by0, by1 = y - bp, y + len(info) * 55 + bp
        d.rectangle([mx+100, by0, W-mx-100, by1], fill=c["light"])
        d.rectangle([mx+100, by0+8, mx+106, by1-8], fill=c["line"])
        
        for label, val in info:
            lx = mx + 140
            d.text((lx, y), f"{label} :", font=fl, fill=c["accent"])
            d.text((lx + mlw + 40, y), val, font=fv, fill=c["text"])
            y += 55

    # ── Date ──
    y += 80
    _tc(d, y, config.get("date", ""), _font(50, "serif"), c["primary"])

    # ── Confidentiel ──
    if config.get("confidentiel"):
        y += 100
        _tc(d, y, "— Document confidentiel —", _font(30, "sans-bold"), c["line"])

    # ── Double filet inférieur ──
    by = H - 180
    d.rectangle([mx, by, W-mx, by+6], fill=c["bg_header"])
    d.rectangle([mx, by+14, W-mx, by+16], fill=c["bg_header"])

    # ── Logo ──
    lp = config.get("logoPath")
    if lp and os.path.exists(lp):
        try:
            logo = Image.open(lp).convert("RGBA")
            r = min(280/logo.width, 120/logo.height)
            logo = logo.resize((int(logo.width*r), int(logo.height*r)), Image.LANCZOS)
            bg = Image.new('RGBA', logo.size, (255,255,255,255))
            bg.paste(logo, (0,0), logo)
            img.paste(bg.convert('RGB'), ((W-logo.width)//2, 200))
        except: pass

    img.save(output_path, quality=95, dpi=(300, 300))
    print(f"✅ Page de garde générée : {output_path}")
    return output_path


if __name__ == '__main__':
    config = {
        "type": "audit", "charte": "classique",
        "titre": "Audit de Sécurité du Système d'Information",
        "sousTitre": "Infrastructure réseau et systèmes d'information",
        "auteur": "Eloham", "formation": "BUT RT — Cybersécurité",
        "organisme": "IUT de Valence — UGA", "entreprise": "Kiventoo",
        "referentiel": "ISO 27001 / EBIOS RM", "date": "Mars 2026",
        "confidentiel": True,
    }
    output = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/pro-docx-repo/screenshots/cover_classique.png"
    os.makedirs(os.path.dirname(output), exist_ok=True)
    generate_cover(config, output)
    for cid in ["neutre", "cyber", "technique"]:
        c2 = dict(config); c2["charte"] = cid
        generate_cover(c2, output.replace("cover_classique.png", f"cover_{cid}.png"))
