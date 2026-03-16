/**
 * generate-doc.js — Script principal de génération pro-docx
 *
 * Ce script est un TEMPLATE de référence. Le skill l'adapte à chaque génération
 * en modifiant la section CONFIG selon les réponses de l'utilisateur.
 *
 * Usage: node generate-doc.js
 * Prérequis: npm install docx
 *
 * Le skill doit TOUJOURS :
 * 1. Copier ce template
 * 2. Modifier la section CONFIG
 * 3. Adapter les sections de contenu
 * 4. Exécuter
 * 5. Valider avec verify-doc.py
 * 6. Convertir en PDF + images pour vérification visuelle
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun,
  Header, Footer, AlignmentType, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageBreak,
  PageNumber, TabStopType, TabStopPosition,
  Table, TableRow, TableCell, VerticalAlign,
  TableOfContents, LevelFormat,
  PositionalTab, PositionalTabAlignment,
  PositionalTabRelativeTo, PositionalTabLeader,
} = require("docx");

// ============================================================
// CHARTES GRAPHIQUES
// ============================================================
const CHARTES = {
  "classique": {
    name: "Classique",
    primary: "1B2A4A", secondary: "C8102E", accent: "4A6FA5",
    light: "F5F6F8", text: "2D2D2D",
  },
  "neutre": {
    name: "Professionnel Neutre",
    primary: "2C3E50", secondary: "34495E", accent: "5D6D7E",
    light: "F2F3F4", text: "2C3E50",
  },
  "cyber": {
    name: "Cybersécurité",
    primary: "1A1A2E", secondary: "E94560", accent: "0F3460",
    light: "EDF2F7", text: "1A202C",
  },
  "technique": {
    name: "Rapport Technique",
    primary: "263238", secondary: "0277BD", accent: "546E7A",
    light: "ECEFF1", text: "263238",
  },
};

// ============================================================
// CONFIG — À adapter par le skill pour chaque génération
// ============================================================
const CONFIG = {
  // Type : "audit" | "memoire" | "td" | "rapport"
  type: "audit",
  charte: "cyber",
  format: "A4", // "A4" ou "US-Letter"

  // Page de garde
  titre: "Audit de Sécurité Informatique",
  sousTitre: "Infrastructure réseau et systèmes d'information",
  auteur: "Eloham",
  formation: "BUT Réseaux & Télécommunications — Cybersécurité",
  organisme: "IUT de Valence — Université Grenoble Alpes",
  entreprise: "MegaO Informatique",
  tuteurAcademique: "M. Dupont",
  tuteurEntreprise: "M. Mallet",
  anneeAcademique: "2025 — 2026",
  date: "Mars 2026",
  confidentiel: true,
  logoPath: null, // Chemin vers le logo ou null

  // Contenu
  outputPath: "output.docx",
};

const charte = CHARTES[CONFIG.charte];
const PAGE = CONFIG.format === "A4"
  ? { width: 11906, height: 16838, content: 9026 }
  : { width: 12240, height: 15840, content: 9360 };

// ============================================================
// HELPERS
// ============================================================

function decorativeLine(color, thickness = 6) {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: thickness, color, space: 1 } },
    children: [],
  });
}

function spacer(twips = 200) {
  return new Paragraph({ spacing: { before: twips, after: 0 }, children: [] });
}

/** Crée un paragraphe de légende (Figure N ou Tableau N) */
function caption(type, number, description) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 60, after: 200 },
    children: [
      new TextRun({
        text: `${type} ${number} — ${description}`,
        font: "Arial",
        size: 24, // 12pt — suffisamment gros pour être lisible
        italics: true,
        bold: true,
        color: charte.accent,
      }),
    ],
  });
}

/** Crée une image avec espacement et anti-chevauchement */
function imageWithCaption(imgPath, captionType, captionNumber, captionDesc, maxWidthPx = 600) {
  const imgData = fs.readFileSync(imgPath);

  // Déterminer les dimensions
  // maxWidthPx est la largeur max en pixels dans le doc
  // On calcule la hauteur proportionnelle
  const ratio = 0.75; // ratio par défaut si on ne peut pas lire l'image
  const width = Math.min(maxWidthPx, Math.floor(PAGE.content / 15)); // Heuristic: DXA to approx px
  const height = Math.floor(width * ratio);

  const imgType = path.extname(imgPath).replace('.', '').toLowerCase();

  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 300, after: 100 },
      children: [
        new ImageRun({
          type: imgType === 'jpg' ? 'jpeg' : imgType,
          data: imgData,
          transformation: { width, height },
          altText: {
            title: `${captionType} ${captionNumber}`,
            description: captionDesc,
            name: `${captionType.toLowerCase()}${captionNumber}`,
          },
        }),
      ],
    }),
    caption(captionType, captionNumber, captionDesc),
  ];
}

/** Crée un tableau pro avec header coloré et lignes alternées */
function proTable(headers, rows, widths = null) {
  const numCols = headers.length;
  const colWidth = Math.floor(PAGE.content / numCols);
  const colWidths = widths || Array(numCols).fill(colWidth);

  const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const headerBorder = {
    top: { style: BorderStyle.SINGLE, size: 1, color: charte.accent },
    bottom: { style: BorderStyle.SINGLE, size: 1, color: charte.accent },
    left: { style: BorderStyle.SINGLE, size: 1, color: charte.accent },
    right: { style: BorderStyle.SINGLE, size: 1, color: charte.accent },
  };

  return new Table({
    width: { size: PAGE.content, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      // Header row
      new TableRow({
        children: headers.map((text, i) =>
          new TableCell({
            width: { size: colWidths[i], type: WidthType.DXA },
            borders: headerBorder,
            shading: { fill: charte.primary, type: ShadingType.CLEAR },
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ text, font: "Arial", size: 22, bold: true, color: "FFFFFF" })],
            })],
          })
        ),
      }),
      // Data rows with alternating shading
      ...rows.map((row, rowIdx) =>
        new TableRow({
          children: row.map((text, i) =>
            new TableCell({
              width: { size: colWidths[i], type: WidthType.DXA },
              borders,
              shading: rowIdx % 2 === 1
                ? { fill: charte.light, type: ShadingType.CLEAR }
                : undefined,
              margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [new Paragraph({
                children: [new TextRun({ text: String(text), font: "Arial", size: 22, color: charte.text })],
              })],
            })
          ),
        })
      ),
    ],
  });
}

// ============================================================
// PAGE DE GARDE
// ============================================================
function buildCoverPage() {
  // La page de garde est générée en image par scripts/generate_cover.py
  // puis insérée en pleine page pour un rendu premium.
  // Fallback en texte si l'image n'existe pas.
  
  const coverPath = path.join(__dirname, '..', 'cover_generated.png');
  
  if (fs.existsSync(coverPath)) {
    // Image pleine page A4 : 595pt wide × 842pt high (approx)
    // En pixels pour docx-js : on utilise les dimensions qui remplissent la zone de contenu
    return [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 0 },
        children: [new ImageRun({
          type: "png",
          data: fs.readFileSync(coverPath),
          transformation: { width: 595, height: 842 },
          altText: { title: "Page de garde", description: "Page de garde du document", name: "cover" },
        })],
      }),
    ];
  }

  // Fallback texte si l'image n'a pas été générée
  const children = [];

  children.push(spacer(600));

  // Logo (si fourni)
  if (CONFIG.logoPath && fs.existsSync(CONFIG.logoPath)) {
    const logoType = path.extname(CONFIG.logoPath).replace('.', '').toLowerCase();
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
      children: [new ImageRun({
        type: logoType === 'jpg' ? 'jpeg' : logoType,
        data: fs.readFileSync(CONFIG.logoPath),
        transformation: { width: 150, height: 80 },
        altText: { title: "Logo", description: "Logo organisme", name: "logo" },
      })],
    }));
  }

  // Type de document
  const typeLabels = {
    audit: "RAPPORT D'AUDIT CYBERSÉCURITÉ",
    memoire: "MÉMOIRE PROFESSIONNEL",
    td: "COMPTE-RENDU DE TP",
    rapport: "RAPPORT TECHNIQUE",
  };
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    children: [new TextRun({
      text: typeLabels[CONFIG.type] || "DOCUMENT",
      font: "Arial", size: 20, color: charte.accent, bold: true,
      characterSpacing: 200,
    })],
  }));

  // Ligne décorative supérieure
  children.push(decorativeLine(charte.secondary, 8));
  children.push(spacer(400));

  // Titre
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({
      text: CONFIG.titre,
      font: "Arial", size: 56, bold: true, color: charte.primary,
    })],
  }));

  // Sous-titre
  if (CONFIG.sousTitre) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 100 },
      children: [new TextRun({
        text: CONFIG.sousTitre,
        font: "Arial", size: 28, color: charte.accent, italics: true,
      })],
    }));
  }

  // Ligne décorative inférieure
  children.push(spacer(400));
  children.push(decorativeLine(charte.secondary, 4));
  children.push(spacer(600));

  // Bloc d'informations (adapté selon le type)
  const infoLines = [];
  infoLines.push({ label: "Auteur", value: CONFIG.auteur });

  if (CONFIG.type === "td") {
    if (CONFIG.formation) infoLines.push({ label: "Formation", value: CONFIG.formation });
    if (CONFIG.module) infoLines.push({ label: "Module", value: CONFIG.module });
    if (CONFIG.enseignant) infoLines.push({ label: "Enseignant", value: CONFIG.enseignant });
  } else if (CONFIG.type === "memoire") {
    if (CONFIG.formation) infoLines.push({ label: "Formation", value: CONFIG.formation });
    if (CONFIG.organisme) infoLines.push({ label: "Organisme", value: CONFIG.organisme });
    if (CONFIG.entreprise) infoLines.push({ label: "Entreprise d'accueil", value: CONFIG.entreprise });
    if (CONFIG.tuteurAcademique) infoLines.push({ label: "Tuteur académique", value: CONFIG.tuteurAcademique });
    if (CONFIG.tuteurEntreprise) infoLines.push({ label: "Tuteur entreprise", value: CONFIG.tuteurEntreprise });
    if (CONFIG.anneeAcademique) infoLines.push({ label: "Année académique", value: CONFIG.anneeAcademique });
  } else if (CONFIG.type === "audit") {
    if (CONFIG.organisme) infoLines.push({ label: "Organisme", value: CONFIG.organisme });
    if (CONFIG.entreprise) infoLines.push({ label: "Entreprise auditée", value: CONFIG.entreprise });
    if (CONFIG.referentiel) infoLines.push({ label: "Référentiel", value: CONFIG.referentiel });
  } else {
    if (CONFIG.formation) infoLines.push({ label: "Formation / Poste", value: CONFIG.formation });
    if (CONFIG.organisme) infoLines.push({ label: "Organisme", value: CONFIG.organisme });
    if (CONFIG.entreprise) infoLines.push({ label: "Entreprise", value: CONFIG.entreprise });
  }

  for (const info of infoLines) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 60, after: 60 },
      children: [
        new TextRun({ text: `${info.label} : `, font: "Arial", size: 22, color: charte.accent, bold: true }),
        new TextRun({ text: info.value, font: "Arial", size: 22, color: charte.text }),
      ],
    }));
  }

  // Date
  children.push(spacer(400));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({ text: CONFIG.date, font: "Arial", size: 24, color: charte.primary, bold: true })],
  }));

  // Badge confidentiel
  if (CONFIG.confidentiel) {
    children.push(spacer(200));
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      border: {
        top: { style: BorderStyle.SINGLE, size: 2, color: charte.secondary },
        left: { style: BorderStyle.SINGLE, size: 2, color: charte.secondary },
        bottom: { style: BorderStyle.SINGLE, size: 2, color: charte.secondary },
        right: { style: BorderStyle.SINGLE, size: 2, color: charte.secondary },
      },
      spacing: { before: 100, after: 100 },
      children: [new TextRun({
        text: "  DOCUMENT CONFIDENTIEL  ",
        font: "Arial", size: 20, bold: true, color: charte.secondary,
        allCaps: true, characterSpacing: 100,
      })],
    }));
  }

  return children;
}

// ============================================================
// STYLES
// ============================================================
function buildStyles() {
  return {
    default: {
      document: { run: { font: "Arial", size: 24, color: charte.text } },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: charte.primary },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: charte.accent },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: charte.text },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 2 },
      },
    ],
  };
}

// ============================================================
// HEADERS / FOOTERS
// ============================================================
function buildHeader() {
  const typeLabels = {
    audit: "Rapport d'audit cybersécurité",
    memoire: "Mémoire professionnel",
    td: "Compte-rendu de TP",
    rapport: "Rapport technique",
  };
  return new Header({
    children: [new Paragraph({
      children: [new TextRun({
        text: typeLabels[CONFIG.type] || "Document",
        font: "Arial", size: 18, color: charte.accent, italics: true,
      })],
      border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: charte.secondary, space: 1 } },
    })],
  });
}

function buildFooter() {
  return new Footer({
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      border: { top: { style: BorderStyle.SINGLE, size: 2, color: charte.accent, space: 1 } },
      spacing: { before: 100 },
      children: [
        new TextRun({ text: `${CONFIG.auteur} — ${CONFIG.organisme}`, font: "Arial", size: 16, color: charte.accent }),
        new TextRun({ text: "    |    Page ", font: "Arial", size: 16, color: charte.accent }),
        new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: charte.primary, bold: true }),
      ],
    })],
  });
}

// ============================================================
// DOCUMENT ASSEMBLY
// ============================================================
async function generate() {
  const doc = new Document({
    styles: buildStyles(),
    sections: [
      // === Section 0 : Page de garde ===
      {
        properties: {
          page: { size: { width: PAGE.width, height: PAGE.height }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } },
          titlePage: true,
        },
        headers: {
          default: new Header({ children: [new Paragraph("")] }),
          first: new Header({ children: [new Paragraph("")] }),
        },
        footers: {
          default: new Footer({ children: [new Paragraph("")] }),
          first: new Footer({ children: [new Paragraph("")] }),
        },
        children: [
          ...buildCoverPage(),
          new Paragraph({ children: [new PageBreak()] }),
        ],
      },

      // === Section 1 : Table des matières ===
      {
        properties: {
          page: { size: { width: PAGE.width, height: PAGE.height }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } },
        },
        headers: { default: buildHeader() },
        footers: { default: buildFooter() },
        children: [
          new Paragraph({
            heading: HeadingLevel.HEADING_1,
            children: [new TextRun("Table des matières")],
          }),
          new TableOfContents("Table des matières", {
            hyperlink: true,
            headingStyleRange: "1-3",
          }),
          new Paragraph({ children: [new PageBreak()] }),

          // Table des figures (placeholder — le skill la génère dynamiquement)
          new Paragraph({
            heading: HeadingLevel.HEADING_1,
            children: [new TextRun("Table des figures")],
          }),
          new Paragraph({
            spacing: { after: 200 },
            children: [new TextRun({
              text: "[Générée automatiquement à la mise à jour des champs dans Word]",
              font: "Arial", size: 22, italics: true, color: charte.accent,
            })],
          }),
          new Paragraph({ children: [new PageBreak()] }),
        ],
      },

      // === Section 2 : Corps du document (PLACEHOLDER — le skill remplace ce contenu) ===
      {
        properties: {
          page: { size: { width: PAGE.width, height: PAGE.height }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } },
        },
        headers: { default: buildHeader() },
        footers: { default: buildFooter() },
        children: [
          // INTRODUCTION
          new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Introduction")] }),
          new Paragraph({
            spacing: { after: 200 },
            children: [new TextRun({
              text: "[Le skill génère l'introduction selon le contexte fourni par l'utilisateur]",
              font: "Arial", size: 24,
            })],
          }),

          // CONTENU PRINCIPAL (placeholder)
          new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Première partie")] }),
          new Paragraph({
            spacing: { after: 200 },
            children: [new TextRun({
              text: "[Contenu principal du document]",
              font: "Arial", size: 24,
            })],
          }),

          // CONCLUSION
          new Paragraph({ pageBreakBefore: true, heading: HeadingLevel.HEADING_1, children: [new TextRun("Conclusion")] }),
          new Paragraph({
            spacing: { after: 200 },
            children: [new TextRun({
              text: "[Le skill génère la conclusion selon le contexte]",
              font: "Arial", size: 24,
            })],
          }),

          // BIBLIOGRAPHIE
          new Paragraph({ pageBreakBefore: true, heading: HeadingLevel.HEADING_1, children: [new TextRun("Bibliographie")] }),
          new Paragraph({
            spacing: { after: 200 },
            children: [new TextRun({
              text: "[1] Sources référencées dans le document",
              font: "Arial", size: 22,
            })],
          }),
        ],
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(CONFIG.outputPath, buffer);
  console.log(`✅ Document généré : ${CONFIG.outputPath}`);
}

generate().catch(console.error);
