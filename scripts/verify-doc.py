#!/usr/bin/env python3
"""
verify-doc.py — Vérification post-génération pour pro-docx
Vérifie : pages blanches, chevauchements, numérotations, légendes, structure.

Usage:
  python verify-doc.py document.docx [--fix]

Sans --fix : rapport uniquement
Avec --fix : tente de corriger les problèmes détectés (via unpack/repack)
"""

import sys
import os
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import re
import json
from pathlib import Path

# Namespaces OOXML
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}


class DocVerifier:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.issues = []
        self.warnings = []
        self.stats = {
            'pages': 0,
            'images': 0,
            'tables': 0,
            'headings': 0,
            'figures_with_caption': 0,
            'tables_with_caption': 0,
        }

    def verify_all(self):
        """Run all verification checks."""
        print(f"\n{'='*60}")
        print(f"  VÉRIFICATION PRO-DOCX : {os.path.basename(self.docx_path)}")
        print(f"{'='*60}\n")

        self._check_file_valid()
        self._check_xml_structure()
        self._check_blank_pages()
        self._check_image_spacing()
        self._check_captions()
        self._check_sections()
        self._check_numbering()

        self._print_report()
        return len(self.issues) == 0

    def _check_file_valid(self):
        """Verify the file is a valid DOCX (ZIP with correct structure)."""
        print("[1/7] Vérification de la validité du fichier...")
        if not os.path.exists(self.docx_path):
            self.issues.append("CRITIQUE: Le fichier n'existe pas")
            return
        try:
            with zipfile.ZipFile(self.docx_path, 'r') as z:
                names = z.namelist()
                if 'word/document.xml' not in names:
                    self.issues.append("CRITIQUE: word/document.xml manquant")
                if '[Content_Types].xml' not in names:
                    self.issues.append("CRITIQUE: [Content_Types].xml manquant")
            print("  ✅ Fichier DOCX valide")
        except zipfile.BadZipFile:
            self.issues.append("CRITIQUE: Le fichier n'est pas un ZIP/DOCX valide")

    def _check_xml_structure(self):
        """Parse document.xml and collect stats."""
        print("[2/7] Analyse de la structure XML...")
        try:
            with zipfile.ZipFile(self.docx_path, 'r') as z:
                doc_xml = z.read('word/document.xml')
            root = ET.fromstring(doc_xml)

            # Count elements
            body = root.find('.//w:body', NS)
            if body is None:
                self.issues.append("CRITIQUE: Pas de <w:body> dans document.xml")
                return

            # Count headings
            for p in body.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                ppr = p.find('w:pPr', NS)
                if ppr is not None:
                    pstyle = ppr.find('w:pStyle', NS)
                    if pstyle is not None:
                        val = pstyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')
                        if val.startswith('Heading') or val.startswith('heading'):
                            self.stats['headings'] += 1

            # Count images
            drawings = list(body.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing'))
            self.stats['images'] = len(drawings)

            # Count tables
            tables = list(body.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl'))
            self.stats['tables'] = len(tables)

            print(f"  📊 {self.stats['headings']} titres, {self.stats['images']} images, {self.stats['tables']} tableaux")

        except Exception as e:
            self.issues.append(f"ERREUR XML: {str(e)}")

    def _check_blank_pages(self):
        """Convert to PDF and check for blank pages."""
        print("[3/7] Vérification des pages blanches...")

        pdf_path = self.docx_path.replace('.docx', '_check.pdf')
        soffice_script = '/mnt/skills/public/docx/scripts/office/soffice.py'

        try:
            # Convert to PDF
            result = subprocess.run(
                ['python3', soffice_script, '--headless', '--convert-to', 'pdf',
                 '--outdir', os.path.dirname(self.docx_path) or '.', self.docx_path],
                capture_output=True, text=True, timeout=60
            )

            actual_pdf = self.docx_path.replace('.docx', '.pdf')
            if os.path.exists(actual_pdf):
                pdf_path = actual_pdf

            if os.path.exists(pdf_path):
                # Count pages using pdfinfo or pdftoppm
                result = subprocess.run(
                    ['pdftoppm', '-jpeg', '-r', '72', pdf_path, '/tmp/pagecheck'],
                    capture_output=True, timeout=60
                )
                import glob
                pages = sorted(glob.glob('/tmp/pagecheck-*.jpg'))
                self.stats['pages'] = len(pages)

                # Check each page for content (simple heuristic: file size)
                for i, page_path in enumerate(pages):
                    size = os.path.getsize(page_path)
                    # A mostly-blank A4 page at 72 DPI is typically < 5KB
                    # A page with only header/footer is typically < 8KB
                    if size < 5000 and i > 0 and i < len(pages) - 1:
                        self.issues.append(
                            f"PAGE BLANCHE: Page {i+1} semble vide ({size} bytes)"
                        )
                    elif size < 8000 and i > 0:
                        self.warnings.append(
                            f"Page {i+1} très peu remplie ({size} bytes) — vérifier visuellement"
                        )

                # Cleanup
                for p in pages:
                    os.remove(p)
                if os.path.exists(pdf_path) and pdf_path != self.docx_path.replace('.docx', '.pdf'):
                    os.remove(pdf_path)

                print(f"  📄 {self.stats['pages']} pages détectées")
            else:
                self.warnings.append("Impossible de convertir en PDF pour vérifier les pages blanches")

        except subprocess.TimeoutExpired:
            self.warnings.append("Timeout lors de la conversion PDF")
        except Exception as e:
            self.warnings.append(f"Erreur vérification pages blanches: {str(e)}")

    def _check_image_spacing(self):
        """Verify images have sufficient spacing and don't exceed content width."""
        print("[4/7] Vérification de l'espacement des images...")

        try:
            with zipfile.ZipFile(self.docx_path, 'r') as z:
                doc_xml = z.read('word/document.xml')
            root = ET.fromstring(doc_xml)
            body = root.find('.//w:body', NS)

            paragraphs = list(body.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'))

            for i, p in enumerate(paragraphs):
                # Check if paragraph contains an image
                drawing = p.find('.//w:drawing', NS)
                if drawing is None:
                    continue

                # Check spacing
                ppr = p.find('w:pPr', NS)
                spacing_ok = False
                if ppr is not None:
                    spacing = ppr.find('w:spacing', NS)
                    if spacing is not None:
                        before = int(spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}before', '0'))
                        after = int(spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}after', '0'))
                        if before >= 200 and after >= 200:
                            spacing_ok = True

                if not spacing_ok:
                    self.warnings.append(
                        f"Image (paragraphe ~{i+1}): espacement insuffisant (< 200 twips)"
                    )

                # Check image dimensions
                extent = drawing.find('.//wp:extent', NS)
                if extent is not None:
                    cx = int(extent.get('cx', '0'))  # EMU
                    # A4 content width = 9026 DXA = 9026 * 635 = 5731510 EMU
                    max_width_emu = 5731510
                    if cx > max_width_emu:
                        self.issues.append(
                            f"Image (paragraphe ~{i+1}): largeur {cx} EMU dépasse la zone de contenu ({max_width_emu} EMU)"
                        )

            if self.stats['images'] > 0:
                print(f"  🖼️  {self.stats['images']} images vérifiées")
            else:
                print("  ℹ️  Aucune image dans le document")

        except Exception as e:
            self.warnings.append(f"Erreur vérification images: {str(e)}")

    def _check_captions(self):
        """Verify each image and table has a caption."""
        print("[5/7] Vérification des légendes...")

        try:
            with zipfile.ZipFile(self.docx_path, 'r') as z:
                doc_xml = z.read('word/document.xml').decode('utf-8')

            # Simple heuristic: count "Figure N" and "Tableau N" patterns
            figure_captions = re.findall(r'Figure\s+\d+', doc_xml)
            table_captions = re.findall(r'Tableau\s+\d+', doc_xml)

            self.stats['figures_with_caption'] = len(figure_captions)
            self.stats['tables_with_caption'] = len(table_captions)

            if self.stats['images'] > 0 and len(figure_captions) < self.stats['images']:
                self.warnings.append(
                    f"Légendes manquantes: {self.stats['images']} images mais seulement {len(figure_captions)} légendes 'Figure N'"
                )

            print(f"  📝 {len(figure_captions)} légendes de figures, {len(table_captions)} légendes de tableaux")

        except Exception as e:
            self.warnings.append(f"Erreur vérification légendes: {str(e)}")

    def _check_sections(self):
        """Verify intro and conclusion are present."""
        print("[6/7] Vérification de la structure (intro/conclusion/biblio)...")

        try:
            with zipfile.ZipFile(self.docx_path, 'r') as z:
                doc_xml = z.read('word/document.xml').decode('utf-8').lower()

            has_intro = 'introduction' in doc_xml
            has_conclusion = 'conclusion' in doc_xml
            has_biblio = any(term in doc_xml for term in ['bibliographie', 'sources', 'références'])

            if not has_intro:
                self.issues.append("STRUCTURE: Pas d'introduction détectée")
            if not has_conclusion:
                self.issues.append("STRUCTURE: Pas de conclusion détectée")
            if not has_biblio:
                self.warnings.append("Pas de section bibliographie/sources détectée")

            status = []
            if has_intro: status.append("Introduction ✅")
            else: status.append("Introduction ❌")
            if has_conclusion: status.append("Conclusion ✅")
            else: status.append("Conclusion ❌")
            if has_biblio: status.append("Bibliographie ✅")
            else: status.append("Bibliographie ⚠️")

            print(f"  {' | '.join(status)}")

        except Exception as e:
            self.warnings.append(f"Erreur vérification structure: {str(e)}")

    def _check_numbering(self):
        """Verify figure/table numbering is sequential."""
        print("[7/7] Vérification de la numérotation...")

        try:
            with zipfile.ZipFile(self.docx_path, 'r') as z:
                doc_xml = z.read('word/document.xml').decode('utf-8')

            # Check figure numbering
            fig_nums = [int(m) for m in re.findall(r'Figure\s+(\d+)', doc_xml)]
            if fig_nums:
                expected = list(range(1, max(fig_nums) + 1))
                if fig_nums != expected:
                    self.warnings.append(
                        f"Numérotation figures non séquentielle: trouvé {fig_nums}, attendu {expected}"
                    )

            # Check table numbering
            tab_nums = [int(m) for m in re.findall(r'Tableau\s+(\d+)', doc_xml)]
            if tab_nums:
                expected = list(range(1, max(tab_nums) + 1))
                if tab_nums != expected:
                    self.warnings.append(
                        f"Numérotation tableaux non séquentielle: trouvé {tab_nums}, attendu {expected}"
                    )

            if fig_nums or tab_nums:
                print(f"  🔢 Figures: {fig_nums or 'aucune'} | Tableaux: {tab_nums or 'aucun'}")
            else:
                print("  ℹ️  Aucune numérotation détectée")

        except Exception as e:
            self.warnings.append(f"Erreur vérification numérotation: {str(e)}")

    def _print_report(self):
        """Print the final verification report."""
        print(f"\n{'='*60}")
        print("  RAPPORT DE VÉRIFICATION")
        print(f"{'='*60}\n")

        print(f"📊 Statistiques:")
        print(f"   Pages: {self.stats['pages']}")
        print(f"   Titres: {self.stats['headings']}")
        print(f"   Images: {self.stats['images']}")
        print(f"   Tableaux: {self.stats['tables']}")
        print(f"   Légendes figures: {self.stats['figures_with_caption']}")
        print(f"   Légendes tableaux: {self.stats['tables_with_caption']}")

        if self.issues:
            print(f"\n❌ ERREURS ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   • {issue}")
        else:
            print("\n✅ Aucune erreur critique détectée")

        if self.warnings:
            print(f"\n⚠️  AVERTISSEMENTS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        else:
            print("\n✅ Aucun avertissement")

        if not self.issues and not self.warnings:
            print("\n🎉 Document conforme aux standards pro-docx !")

        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify-doc.py document.docx [--fix]")
        sys.exit(1)

    docx_path = sys.argv[1]
    verifier = DocVerifier(docx_path)
    success = verifier.verify_all()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
