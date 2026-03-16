# Page de garde — Template de référence

## Structure de la page de garde

La page de garde est TOUJOURS dans sa propre section docx-js, avec :
- `titlePage: true` dans les propriétés de section
- Headers et footers vides (pas de numérotation)
- Un `PageBreak` à la fin pour séparer du contenu

## Éléments dans l'ordre (de haut en bas)

### 1. Logo (optionnel)
- Position : centré, en haut
- Taille max : 150px de large, ratio préservé
- Espacement : 400 twips après

```javascript
// Si un logo est fourni :
new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 400 },
  children: [new ImageRun({
    type: "png",
    data: fs.readFileSync(logoPath),
    transformation: { width: 150, height: calculatedHeight },
    altText: { title: "Logo", description: "Logo organisme", name: "logo" },
  })],
})
```

### 2. Type de document
- Texte en MAJUSCULES avec espacement lettres
- Petite taille (10pt), couleur accent, bold
- `characterSpacing: 200` pour l'effet espacé

### 3. Ligne décorative supérieure
- Couleur : secondary
- Épaisseur : 8 (size dans BorderStyle)
- Espacement : 200 twips avant et après

### 4. Titre principal
- Taille : 28pt, bold, couleur primary
- Centré
- Espacement : 200 twips après

### 5. Sous-titre
- Taille : 14pt, italic, couleur accent
- Centré
- Espacement : 100 twips après

### 6. Ligne décorative inférieure
- Couleur : secondary
- Épaisseur : 4 (plus fine que la supérieure)
- Espacement : 400 twips avant

### 7. Bloc d'informations
- Centré
- Chaque ligne : "Label : " (bold, accent) + "Valeur" (normal, text)
- Taille : 11pt
- Espacement : 60 twips entre chaque ligne

Lignes à afficher (adapter selon le type de doc) :

| Type de doc | Lignes affichées |
|-------------|-----------------|
| Audit | Auteur, Organisme, Entreprise auditée, Référentiel, Date |
| Mémoire | Auteur, Formation, Organisme, Entreprise, Tuteur académique, Tuteur entreprise, Année académique |
| TD/TP | Auteur, Formation, Module, Enseignant, Date |
| Rapport technique | Auteur, Poste/Formation, Organisme, Date, Version |

### 8. Date
- Taille : 12pt, bold, couleur primary
- Centré
- Espacement : 400 twips avant

### 9. Badge confidentiel (si activé)
- Bordure complète couleur secondary (2pt)
- Texte : "DOCUMENT CONFIDENTIEL" en MAJUSCULES
- Taille : 10pt, bold, couleur secondary
- `characterSpacing: 100`
- L'ordre des bordures dans le XML DOIT être : top, left, bottom, right (sinon erreur de validation OOXML)

### 10. PageBreak final
```javascript
new Paragraph({ children: [new PageBreak()] })
```

## Code de la section page de garde

```javascript
{
  properties: {
    page: {
      size: { width: 11906, height: 16838 }, // A4
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
    },
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
    ...buildCoverPage(config, charte),
    new Paragraph({ children: [new PageBreak()] }),
  ],
}
```
