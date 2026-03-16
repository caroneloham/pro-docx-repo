---
name: pro-docx
description: "Skill premium pour générer des documents Word professionnels de qualité ingénieur. Génère automatiquement : page de garde travaillée, table des matières, table des figures, styles custom avec charte graphique au choix, en-têtes/pieds de page, illustrations avec légendes numérotées, bibliographie, intro/conclusion. Supporte 4 types : rapport d'audit cybersécurité, mémoire/thèse professionnelle, TD/compte-rendu de TP, rapport technique générique. Utiliser ce skill dès que l'utilisateur demande un document Word pro, un rapport, un mémoire, un livrable formaté, un audit, un compte-rendu, ou toute demande de .docx avec mise en page soignée. Aussi utiliser quand l'utilisateur mentionne 'rapport pro', 'document pro', 'livrable Word', 'pro-docx', ou veut un rendu de qualité professionnelle/académique."
---

# Pro-DOCX — Générateur de documents Word professionnels

## Vue d'ensemble

Ce skill génère des documents Word (.docx) de qualité professionnelle/académique avec une mise en page complète et cohérente. Il s'appuie sur le skill `docx` de base (voir `/mnt/skills/public/docx/SKILL.md`) pour la partie technique docx-js, et ajoute une couche de structure, design et vérifications automatiques.

**Toujours lire `/mnt/skills/public/docx/SKILL.md` en complément** pour les détails techniques de génération docx-js (tables, images, headers, footers, etc.).

---

## Workflow obligatoire

### Phase 1 : Collecte d'informations (OBLIGATOIRE)

**Le skill DOIT poser des questions AVANT toute génération.** Ne jamais commencer à coder sans avoir collecté les informations minimales.

#### Questions obligatoires (toujours poser) :

1. **Type de document** — Quel type ?
   - Rapport d'audit cybersécurité
   - Mémoire / thèse professionnelle
   - TD / compte-rendu de TP
   - Rapport technique générique

2. **Charte graphique** — Quelle charte couleur ?
   - Classique (bleu marine + rouge accent — académique)
   - Professionnel Neutre (gris-bleu sobre)
   - Cybersécurité (bleu foncé + rouge vif)
   - Rapport Technique (gris ardoise + bleu)
   - Personnalisée (demander les couleurs)

3. **Informations de page de garde** (adapter selon le type) :
   - Titre du document
   - Sous-titre (optionnel)
   - Auteur
   - Formation / poste
   - Organisme / école
   - Entreprise (si alternance/stage)
   - Tuteur(s)
   - Date
   - Année académique
   - Confidentialité (oui/non, niveau)

4. **Contexte du document** :
   - Objectif / finalité du document
   - Destinataire(s) principal(aux)
   - Niveau de détail attendu (synthétique / détaillé / exhaustif)
   - Y a-t-il un cahier des charges ou un plan imposé ?

5. **Contenu spécifique** :
   - Le contenu est-il déjà rédigé ou faut-il aussi le générer ?
   - Y a-t-il des illustrations/graphiques/données à inclure ?
   - Logo(s) à intégrer ? (demander le fichier)
   - Sources / bibliographie à inclure ?

#### Questions conditionnelles (selon le type) :

**Si audit cybersécurité :**
- Périmètre de l'audit (réseau, SI, applicatif...)
- Référentiel utilisé (ISO 27001, EBIOS, ANSSI...)
- Outils utilisés (nmap, Nessus, Burp...)
- Nombre de vulnérabilités à documenter

**Si mémoire/thèse :**
- Problématique
- Plan imposé par l'école ?
- Nombre de pages attendu
- Normes bibliographiques (APA, Vancouver...)

**Si TD/TP :**
- Matière / module (ex: R5.02, R511...)
- Numéro du TD/TP
- Prof / intervenant
- Exercices à traiter

**Si rapport technique :**
- Technologie(s) concernée(s)
- Public cible (technique / management / mixte)

### Phase 2 : Génération du document

Une fois les infos collectées, générer le document en suivant la structure ci-dessous.

#### Dossier de travail (OBLIGATOIRE)

**Chaque document généré DOIT avoir son propre dossier de projet.** Ne jamais générer un .docx en vrac.

Structure obligatoire :
```
pro-docx-output/<nom-du-projet>/
├── <nom-du-projet>.docx          # Document final
├── <nom-du-projet>.pdf           # Export PDF (généré automatiquement)
├── images/                        # Toutes les illustrations en fichiers séparés
│   ├── fig-01-titre.png
│   ├── fig-02-titre.png
│   ├── tab-01-titre.png          # Captures des tableaux complexes (optionnel)
│   └── ...
└── sources/                       # Fichiers sources utilisés (optionnel)
    ├── data.csv
    ├── graphe-script.py
    └── ...
```

**Règles :**
- Le nom du dossier est dérivé du titre du document (slug, sans accents ni espaces)
- Chaque image générée (matplotlib, SVG converti, diagramme) est TOUJOURS sauvegardée en PNG dans `images/` EN PLUS d'être intégrée dans le .docx
- Les images doivent avoir des noms descriptifs : `fig-01-architecture-reseau.png`, pas `image1.png`
- Le PDF est généré automatiquement via LibreOffice après le .docx
- En environnement Claude.ai : copier le dossier final vers `/mnt/user-data/outputs/`
- En environnement Cowork ou Claude Code : créer le dossier dans le répertoire de travail courant

Cela permet à l'utilisateur de :
- Réutiliser les images indépendamment (présentations, emails, autres docs)
- Avoir un backup structuré de tout le projet
- Retrouver facilement chaque illustration

### Phase 3 : Vérifications post-génération (OBLIGATOIRE)

Après chaque génération, effectuer TOUTES ces vérifications :

1. **Pas de pages blanches parasites** — Vérifier qu'aucune page ne contient seulement un header/footer sans contenu. Convertir en PDF et compter les pages vs le contenu attendu.

2. **Pas de chevauchement texte/images** — Vérifier que :
   - Chaque image a un espacement suffisant (minimum 200 twips avant et après)
   - Les images ne dépassent pas la largeur de contenu (9026 DXA en A4 avec marges 1")
   - Les légendes sont toujours immédiatement sous leur figure
   - Aucune image n'est coupée entre deux pages (utiliser `pageBreakBefore` si nécessaire)

3. **Cohérence des numérotations** — Figures, tableaux et pages numérotés séquentiellement sans saut.

4. **Légendes présentes** — Chaque figure et chaque tableau a une légende numérotée.

5. **Sections complètes** — Intro et conclusion présentes, bibliographie en fin de document.

---

## Structure standard d'un document

Chaque document généré DOIT contenir (dans cet ordre) :

### Section 0 : Page de garde (IMAGE PLEINE PAGE)
- Générée par `scripts/generate_cover.py` en image PNG haute résolution (300 DPI, A4)
- Design premium : bloc supérieur foncé avec titre/sous-titre, éléments géométriques décoratifs, bloc d'informations stylisé, badge confidentiel
- Insérée en pleine page dans le document via `ImageRun`
- Pas de header/footer sur cette section
- Pas de numéro de page
- Workflow de génération :
  1. Préparer le config JSON avec toutes les infos collectées
  2. `python scripts/generate_cover.py` → génère `cover_generated.png`
  3. Le script `generate-doc.js` détecte et insère automatiquement l'image
- Voir `references/cover-page.md` pour le template détaillé

### Section 1 : Pages liminaires
- Table des matières (TOC auto)
- Table des figures (si le document contient des figures)
- Table des tableaux (si le document contient des tableaux)
- Glossaire (si nécessaire, surtout pour audit/mémoire)

### Section 2 : Corps du document
- **Introduction** (toujours)
  - Contexte
  - Objectifs
  - Périmètre (si applicable)
  - Plan du document
- **Chapitres/sections** (contenu principal)
- **Conclusion** (toujours)
  - Synthèse
  - Perspectives / recommandations

### Section 3 : Annexes et références
- **Bibliographie / Table des sources** (toujours, même si vide → "Aucune source externe")
- **Annexes** (si applicable)

---

## Chartes graphiques

Voir `references/chartes.md` pour les définitions complètes des palettes de couleurs.

Chaque charte définit :
- `primary` — Couleur principale (titres H1, éléments forts)
- `secondary` — Couleur d'accent (lignes décoratives, badges)
- `accent` — Couleur secondaire (titres H2, labels, header/footer)
- `light` — Couleur de fond clair (fonds de tableaux alternés)
- `text` — Couleur du texte courant

---

## Styles typographiques

| Élément | Police | Taille | Style | Couleur |
|---------|--------|--------|-------|---------|
| Titre page de garde | Arial | 28pt | Bold | primary |
| Sous-titre page de garde | Arial | 14pt | Italic | accent |
| H1 | Arial | 16pt | Bold | primary |
| H2 | Arial | 14pt | Bold | accent |
| H3 | Arial | 13pt | Bold | text |
| Corps | Arial | 12pt | Normal | text |
| Légende figure/tableau | Arial | 12pt | Italic + Bold | accent |
| En-tête | Arial | 9pt | Italic | accent |
| Pied de page | Arial | 8pt | Normal | accent |
| Code / technique | Consolas | 10pt | Normal | text |

---

## Gestion des illustrations

### Règles de placement des images

1. **Espacement obligatoire** : minimum 200 twips (spacing before/after) autour de chaque image
2. **Largeur max** : ne jamais dépasser la largeur de contenu (9026 DXA en A4)
3. **Ratio préservé** : toujours conserver le ratio hauteur/largeur original
4. **Anti-chevauchement** : si une image + sa légende risquent d'être coupées en bas de page, ajouter un `pageBreakBefore: true` sur le paragraphe de l'image
5. **Légende systématique** : format "Figure N — Description" ou "Tableau N — Description", centré, italique + bold, 12pt, couleur accent
6. **Lisibilité du texte dans les images** : TOUTE image générée (matplotlib, SVG, diagramme) DOIT avoir des polices suffisamment grandes pour être lisibles une fois insérée dans le document. Règles minimales :
   - matplotlib : `plt.rcParams.update({'font.size': 14, 'axes.titlesize': 18, 'axes.labelsize': 16, 'xtick.labelsize': 13, 'ytick.labelsize': 13, 'legend.fontsize': 13})`
   - SVG : texte minimum 14px, titres minimum 18px
   - Largeur d'export minimum : 2000px pour garantir la netteté à 300 DPI
   - TOUJOURS vérifier visuellement que le texte des graphiques est lisible après insertion

### Génération d'illustrations

Le skill peut générer des illustrations via :
- **matplotlib** (Python) — graphiques, diagrammes, matrices de risques, camemberts
- **SVG inline** — schémas d'architecture, diagrammes de flux
- **Figma/Mermaid** — si les outils MCP sont connectés

Workflow pour chaque illustration :
1. Générer l'image (PNG, 300 DPI minimum)
2. Calculer les dimensions pour qu'elle tienne dans la largeur de contenu
3. Insérer avec `ImageRun` + `transformation` calculée
4. Ajouter la légende numérotée immédiatement après
5. Vérifier l'espacement avant/après

---

## Vérification anti-pages-blanches

Après génération, exécuter cette procédure :

```bash
# 1. Convertir en PDF
python /mnt/skills/public/docx/scripts/office/soffice.py --headless --convert-to pdf output.docx

# 2. Convertir chaque page en image
pdftoppm -jpeg -r 150 output.pdf page-check

# 3. Vérifier visuellement chaque page
# Si une page ne contient que le header/footer → problème de page blanche
```

Si des pages blanches sont détectées : ajuster les sauts de page, supprimer les `PageBreak` superflus, ou fusionner les sections.

---

## Vérification anti-chevauchement

Pour chaque image dans le document :

1. S'assurer que `spacing.before >= 200` et `spacing.after >= 200` sur le paragraphe contenant l'image
2. S'assurer que la légende a `spacing.before = 60` et `spacing.after = 200`
3. Vérifier que `transformation.width` en pixels × 9525 (EMU) ne dépasse pas 9026 × 635 (DXA → EMU)
4. En cas de doute, réduire l'image à 80% de la largeur de contenu max

---

## Fichiers de référence

- `references/chartes.md` — Définitions des palettes de couleurs
- `references/cover-page.md` — Template de page de garde détaillé
- `references/doc-types.md` — Structures spécifiques par type de document
- `scripts/generate-doc.js` — Script principal de génération
- `scripts/verify-doc.py` — Script de vérification post-génération
- `assets/` — Logos et ressources graphiques par défaut
