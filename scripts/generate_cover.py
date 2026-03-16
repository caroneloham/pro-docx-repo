#!/usr/bin/env python3
"""
generate_cover.py — Générateur de page de garde académique/professionnelle
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
        "serif": ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"],
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

    # ── Bloc infos — TOUS les champs disponibles ──
    info = []
    
    # Champs communs à tous les types
    if config.get("formation"):
        info.append(("Formation", config["formation"]))
    if config.get("organisme"):
        info.append(("Organisme", config["organisme"]))
    
    # Champs spécifiques par type
    if dt == "td":
        if config.get("module"):
            info.append(("Module", config["module"]))
        if config.get("enseignant"):
            info.append(("Enseignant", config["enseignant"]))
    elif dt == "memoire":
        if config.get("entreprise"):
            info.append(("Entreprise d'accueil", config["entreprise"]))
        if config.get("tuteurAcademique"):
            info.append(("Tuteur académique", config["tuteurAcademique"]))
        if config.get("tuteurEntreprise"):
            info.append(("Tuteur entreprise", config["tuteurEntreprise"]))
    elif dt == "audit":
        if config.get("entreprise"):
            info.append(("Entité auditée", config["entreprise"]))
        if config.get("referentiel"):
            info.append(("Référentiel", config["referentiel"]))
        if config.get("tuteurAcademique"):
            info.append(("Tuteur académique", config["tuteurAcademique"]))
        if config.get("tuteurEntreprise"):
            info.append(("Tuteur entreprise", config["tuteurEntreprise"]))
    else:
        if config.get("entreprise"):
            info.append(("Entreprise", config["entreprise"]))
        if config.get("version"):
            info.append(("Version", config["version"]))
    
    # Année académique — commun
    if config.get("anneeAcademique"):
        info.append(("Année académique", config["anneeAcademique"]))

    if info:
        fl = _font(34, "sans-bold")
        fv = _font(34, "sans")
        mlw = max(_tw(d, f"{l} :", fl) for l, _ in info)
        
        y += 30
        bp = 40
        line_h = 60
        by0, by1 = y - bp, y + len(info) * line_h + bp
        
        # Fond du bloc
        d.rectangle([mx+80, by0, W-mx-80, by1], fill=c["light"])
        
        # Barre accent gauche
        d.rectangle([mx+80, by0+10, mx+88, by1-10], fill=c["line"])
        
        # Ligne de séparation entre chaque champ
        for i in range(1, len(info)):
            sep_y = y + i * line_h - line_h//2 + 25
            d.line([(mx+120, sep_y), (W-mx-120, sep_y)], fill=(210, 215, 225), width=1)
        
        for label, val in info:
            lx = mx + 130
            d.text((lx, y), f"{label} :", font=fl, fill=c["accent"])
            d.text((lx + mlw + 50, y), val, font=fv, fill=c["text"])
            y += line_h

    # ── Date ──
    y += 80
    _tc(d, y, config.get("date", ""), _font(50, "serif"), c["primary"])

    # ── Confidentiel ──
    if config.get("confidentiel"):
        y += 100
        _tc(d, y, "— Document confidentiel —", _font(32, "sans-bold"), c["line"])

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
        "auteur": "Eloham",
        "formation": "BUT RT — Cybersécurité",
        "organisme": "IUT de Valence — UGA",
        "entreprise": "Kiventoo",
        "referentiel": "ISO 27001 / EBIOS RM",
        "tuteurAcademique": "M. Dupont",
        "tuteurEntreprise": "M. Mallet",
        "anneeAcademique": "2025 — 2026",
        "date": "Mars 2026",
        "confidentiel": True,
    }
    output = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/pro-docx-repo/screenshots/cover_classique.png"
    os.makedirs(os.path.dirname(output), exist_ok=True)
    generate_cover(config, output)
    for cid in ["neutre", "cyber", "technique"]:
        c2 = dict(config); c2["charte"] = cid
        generate_cover(c2, output.replace("cover_classique.png", f"cover_{cid}.png"))
