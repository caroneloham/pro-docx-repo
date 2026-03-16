# Chartes graphiques — Définitions des palettes

## Palettes disponibles

### Classique
```javascript
const CHARTE_CLASSIQUE = {
  id: "classique",
  name: "Classique",
  primary: "1B2A4A",    // Bleu marine — titres, éléments forts
  secondary: "C8102E",  // Rouge accent — filets, badges
  accent: "4A6FA5",     // Bleu moyen — sous-titres, labels
  light: "F5F6F8",      // Fond clair — tableaux alternés
  text: "2D2D2D",       // Texte principal
};
```

### Professionnel Neutre
```javascript
const CHARTE_NEUTRE = {
  id: "neutre",
  name: "Professionnel Neutre",
  primary: "2C3E50",    // Gris-bleu foncé
  secondary: "34495E",  // Gris accent
  accent: "5D6D7E",     // Gris moyen
  light: "F2F3F4",      // Fond clair
  text: "2C3E50",       // Texte principal
};
```

### Cybersécurité
```javascript
const CHARTE_CYBER = {
  id: "cyber",
  name: "Cybersécurité",
  primary: "1A1A2E",    // Bleu très foncé
  secondary: "16213E",  // Bleu nuit
  accent: "0F3460",     // Bleu profond
  light: "EDF2F7",      // Fond clair
  text: "1A202C",       // Texte principal
  line: "E94560",       // Rouge vif pour filets
};
```

### Rapport Technique
```javascript
const CHARTE_TECHNIQUE = {
  id: "technique",
  name: "Rapport Technique",
  primary: "263238",    // Gris ardoise
  secondary: "37474F",  // Gris moyen
  accent: "546E7A",     // Gris-bleu
  light: "ECEFF1",      // Fond clair
  text: "263238",       // Texte principal
  line: "0277BD",       // Bleu technique
};
```

## Application des couleurs

| Élément | Couleur utilisée |
|---------|-----------------|
| Titre page de garde | primary |
| Sous-titre page de garde | accent |
| Filets décoratifs | line / secondary |
| Titres H1 | primary |
| Titres H2 | accent |
| Titres H3 | text (bold) |
| En-tête tableau | primary (fond) + blanc (texte) |
| Lignes alternées tableau | light (fond) |
| Légendes figures/tableaux | accent |
| Header/Footer | accent |
