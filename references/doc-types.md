# Types de documents — Structures spécifiques

## 1. Rapport d'audit cybersécurité

### Structure imposée

1. **Page de garde**
2. **Table des matières**
3. **Table des figures**
4. **Glossaire** (termes techniques : CVE, CVSS, MFA, EDR, etc.)
5. **Introduction**
   - Contexte de l'audit
   - Périmètre (réseau, SI, applicatif, physique)
   - Méthodologie (outils, référentiels)
   - Calendrier de l'audit
6. **Cartographie du SI**
   - Architecture réseau (schéma obligatoire → Figure)
   - Inventaire des actifs
   - Matrice des flux
7. **Analyse des vulnérabilités**
   - Synthèse globale (graphique camembert par criticité → Figure)
   - Détail par vulnérabilité :
     - ID CVE
     - Score CVSS
     - Description
     - Impact
     - Preuve / capture (→ Figure si applicable)
     - Recommandation
   - Matrice de risques (→ Figure, tableau coloré criticité)
8. **Recommandations**
   - Tableau récapitulatif (priorité, effort, impact)
   - Plan d'action proposé
9. **Conclusion**
   - Niveau de sécurité global
   - Points critiques
   - Prochaines étapes
10. **Bibliographie / Sources**
11. **Annexes**
    - Résultats bruts des scans
    - Configuration des outils

### Illustrations obligatoires pour un audit
- Schéma d'architecture réseau (minimum 1)
- Graphique de répartition des vulnérabilités par criticité
- Matrice de risques (impact × vraisemblance)
- Captures d'écran des vulnérabilités majeures (si fournies)

### Couleurs de criticité dans les tableaux
```javascript
const CRITICITE = {
  critique: { fond: "FF0000", texte: "FFFFFF" },  // Rouge + blanc
  haute:    { fond: "FF6600", texte: "FFFFFF" },  // Orange + blanc
  moyenne:  { fond: "FFD700", texte: "000000" },  // Jaune + noir
  faible:   { fond: "90EE90", texte: "000000" },  // Vert clair + noir
  info:     { fond: "87CEEB", texte: "000000" },  // Bleu clair + noir
};
```

---

## 2. Mémoire / Thèse professionnelle

### Structure imposée

1. **Page de garde** (infos complètes : tuteurs, formation, année)
2. **Remerciements** (optionnel)
3. **Table des matières**
4. **Table des figures**
5. **Table des tableaux**
6. **Glossaire / Liste des abréviations**
7. **Introduction générale**
   - Contexte
   - Problématique
   - Objectifs
   - Méthodologie
   - Annonce du plan
8. **Partie 1 : Contexte et état de l'art**
   - Présentation de l'entreprise
   - Environnement technique
   - État de l'art / revue de littérature
9. **Partie 2 : Analyse et conception**
   - Analyse des besoins
   - Architecture proposée
   - Choix techniques justifiés
10. **Partie 3 : Réalisation et mise en œuvre**
    - Implémentation
    - Tests et validation
    - Résultats obtenus (graphiques, métriques → Figures)
11. **Conclusion générale**
    - Synthèse des travaux
    - Bilan personnel
    - Perspectives et améliorations
12. **Bibliographie** (formatée selon normes demandées)
13. **Annexes**
    - Code source pertinent
    - Configurations
    - Données complémentaires

### Illustrations typiques pour un mémoire
- Organigramme de l'entreprise
- Schéma d'architecture avant/après
- Diagrammes de Gantt (planning)
- Graphiques de résultats/métriques
- Captures d'écran de l'interface/outil développé

---

## 3. TD / Compte-rendu de TP

### Structure imposée

1. **Page de garde** (module, numéro TD/TP, enseignant)
2. **Table des matières** (si > 5 pages, sinon optionnel)
3. **Introduction** (courte : objectif du TD/TP)
4. **Exercice 1 / Manipulation 1**
   - Énoncé (résumé ou référence)
   - Démarche / commandes
   - Résultats (captures → Figures)
   - Analyse / réponses aux questions
5. **Exercice 2 / Manipulation 2** (idem)
6. **[...]**
7. **Conclusion** (courte : ce qui a été appris, difficultés)
8. **Sources** (si applicable)

### Spécificités TD/TP
- Les captures d'écran de terminal doivent avoir un fond légèrement grisé
- Les commandes doivent être en police Consolas
- Chaque exercice commence par un rappel court de l'énoncé en italique
- Numérotation des figures : "Figure Ex.N — Description" (ex: "Figure 2.1 — Résultat du scan nmap")

---

## 4. Rapport technique générique

### Structure imposée

1. **Page de garde**
2. **Historique des versions** (tableau : version, date, auteur, modifications)
3. **Table des matières**
4. **Table des figures**
5. **Introduction**
   - Contexte
   - Objectif du document
   - Public cible
   - Périmètre
6. **Présentation générale**
   - Description du système/technologie
   - Architecture (schéma → Figure)
7. **Analyse technique**
   - Détails d'implémentation
   - Configurations
   - Tests réalisés (résultats → Figures/Tableaux)
8. **Résultats et discussion**
   - Métriques
   - Comparaisons
   - Limitations
9. **Conclusion et recommandations**
10. **Bibliographie**
11. **Annexes**

### Spécificités rapport technique
- Inclure un tableau d'historique des versions en page 2
- Les blocs de code/configuration doivent être dans des cellules de tableau avec fond gris clair
- Diagrammes d'architecture obligatoires si le sujet est infra/réseau

---

## Éléments communs à tous les types

### Introduction — Structure minimale
Toute introduction DOIT contenir au minimum :
- 1 paragraphe de contexte
- 1 paragraphe d'objectifs
- 1 phrase d'annonce du plan ("Ce document s'articule en N parties...")

### Conclusion — Structure minimale
Toute conclusion DOIT contenir au minimum :
- 1 paragraphe de synthèse
- 1 paragraphe de perspectives / recommandations

### Bibliographie
Format par défaut (sauf demande contraire) :
```
[1] Auteur, "Titre", Source, Date. URL (si applicable)
```
Numérotée séquentiellement, références appelées dans le texte avec [N].
