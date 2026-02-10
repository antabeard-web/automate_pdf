#!/usr/bin/env python3
"""
Script pour protéger en écriture tous les fichiers PDF d'un répertoire avec un mot de passe.
Sauvegarde les fichiers protégés dans un répertoire de sortie.
Ignore les fichiers déjà protégés.
"""

import os
import sys
import argparse
from pathlib import Path
import secrets
import string
import shutil

try:
    import pikepdf
    import re
except ImportError:
    print("❌ La bibliothèque 'pikepdf' n'est pas installée.")
    print("📦 Installez-la avec: pip install pikepdf")
    sys.exit(1)


def generate_strong_password(length=20):
    """Génère un mot de passe fort et aléatoire."""
    # Caractères disponibles : lettres, chiffres et symboles
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    # Utilise secrets pour une génération cryptographiquement sûre
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def is_pdf_encrypted(pdf_path):
    """Vérifie si un PDF est déjà protégé."""
    try:
        with pikepdf.open(pdf_path) as pdf:
            return pdf.is_encrypted
    except pikepdf.PasswordError:
        return True  # Le fichier est protégé
    except Exception as e:
        print(f"⚠️  Erreur lors de la vérification de {pdf_path}: {e}")
        return False

def analyze_filename(nom_fichier):
    """
    Parse le nom du fichier PDF et extrait les informations suivantes:
    Facture et Client
    
    Format attendu: "NUMERO_FACTURE NUMERO_CLIENT.pdf"
    Exemple: "3001694 AB123456.pdf"
    
    Args:
        nom_fichier (str): Nom du fichier PDF
    
    Returns:
        dict: Dictionnaire contenant {'facture': ..., 'client': ...}
    """
    try:
        # Supprimer l'extension .pdf
        nom_sans_ext = os.path.splitext(nom_fichier)[0]
        
        # Expression régulière pour parser le nom
        pattern = r'^(?P<facture>\d{6,})\s+(?P<client>[a-zA-Z]{0,2}\d{6,})?'
        
        match = re.match(pattern, nom_sans_ext)
        
        if match:
            client = match.group('client')
            return {
                'facture': match.group('facture'),
                'client': client if client else '',  # Retourne une chaîne vide si pas de client
            }
        else:
            print(f"⚠️  Format de fichier invalide: {nom_fichier}")
            return None
    
    except Exception as e:
        print(f"❌ Erreur lors du parsing de {nom_fichier}: {e}")
        return None
    
def protect_pdf(input_path, output_path, password):
    """Protège un PDF en écriture avec un mot de passe."""

    infos = analyze_filename(input_path.name)

    try:
        with pikepdf.open(input_path) as pdf:
            
            if pdf.docinfo is None:
                pdf.docinfo = pdf.make_stream(b"")
            
            pdf.docinfo.Title = f"Bill {infos['facture']}"
            pdf.docinfo.Subject = f"Client: {infos['client']}"

            # Ajouter les métadonnées personnalisées
            pdf.docinfo.Bill = infos['facture']
            pdf.docinfo.Customer = infos['client']
            # pdf.docinfo.Project = infos['project']

            # Protège en écriture (permet la lecture sans mot de passe)
            # AUTORISE la signature et les annotations
            pdf.save(
                output_path,
                encryption=pikepdf.Encryption(
                    owner=password,  # Mot de passe propriétaire (pour modifier)
                    user="",         # Pas de mot de passe pour lire
                    allow=pikepdf.Permissions(
                        accessibility=True,
                        extract=True,
                        modify_annotation=True,   # ✅ AUTORISE les signatures et annotations
                        modify_assembly=False,
                        modify_form=True,         # ✅ AUTORISE le remplissage de formulaires
                        modify_other=False,       # ❌ Interdit la modification du contenu
                        print_lowres=True,
                        print_highres=True
                    )
                )
            )
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la protection de {input_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Protège en écriture tous les PDFs d'un répertoire avec des mots de passe uniques et forts."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Répertoire d'entrée (lecture) contenant les PDFs"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Répertoire de sortie (écriture) pour les PDFs protégés"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Traiter aussi les sous-répertoires"
    )
    parser.add_argument(
        "--password-length",
        type=int,
        default=20,
        help="Longueur des mots de passe générés (défaut: 20)"
    )
    parser.add_argument(
        "--delete-source",
        action="store_true",
        help="Supprimer le fichier source après protection réussie"
    )
    
    args = parser.parse_args()
    
    # Vérifier que le répertoire d'entrée existe
    input_dir = Path(args.input)
    if not input_dir.exists():
        print(f"❌ Le répertoire d'entrée '{args.input}' n'existe pas.")
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"❌ '{args.input}' n'est pas un répertoire.")
        sys.exit(1)
    
    # Créer le répertoire de sortie s'il n'existe pas
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Trouver tous les fichiers PDF
    if args.recursive:
        pdf_files = list(input_dir.rglob("*.pdf"))
    else:
        pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"ℹ️  Aucun fichier PDF trouvé dans '{args.input}'")
        return
    
    print(f"📂 Répertoire d'entrée: {input_dir}")
    print(f"📂 Répertoire de sortie: {output_dir}")
    print(f"📁 {len(pdf_files)} fichier(s) PDF trouvé(s)")
    print("🔍 Vérification des fichiers déjà protégés...\n")
    
    protected_count = 0
    skipped_count = 0
    error_count = 0
    already_exists_count = 0
    
    for pdf_file in pdf_files:
        # Calculer le chemin relatif pour recréer la structure
        relative_path = pdf_file.relative_to(input_dir)
        
        # Créer le chemin de sortie en conservant la structure
        output_file = output_dir / relative_path
        
        # Créer le répertoire de destination s'il n'existe pas (une seule fois pour tous les cas)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Vérifier si le fichier de sortie existe déjà
        if output_file.exists():
            print(f"⏭️  Ignoré (fichier de sortie existe déjà): {relative_path}")
            already_exists_count += 1
            # Supprimer le fichier source si demandé
            if args.delete_source:
                try:
                    pdf_file.unlink()
                    print(f"   🗑️  Fichier source supprimé: {relative_path}")
                except Exception as e:
                    print(f"   ⚠️  Erreur lors de la suppression de {relative_path}: {e}")
            continue

        # Vérifier si déjà protégé
        if is_pdf_encrypted(pdf_file):
            print(f"⏭️  Ignoré (déjà protégé): {relative_path}")
            skipped_count += 1
            
            # Copier le fichier déjà protégé vers la destination
            try:
                shutil.copy2(pdf_file, output_file)
                print(f"   📋 Fichier copié vers la destination: {relative_path}")
                
                # Supprimer le fichier source si demandé
                if args.delete_source:
                    pdf_file.unlink()
                    print(f"   🗑️  Fichier source supprimé: {relative_path}")
            except Exception as e:
                print(f"   ⚠️  Erreur lors de la copie/suppression de {relative_path}: {e}")
            
            continue
        
        # Générer un mot de passe unique et fort
        password = generate_strong_password(args.password_length)
        
        # Protéger le fichier
        print(f"🔒 Protection de: {relative_path}...", end=" ")
        
        if protect_pdf(pdf_file, output_file, password):
            print("✅")
            protected_count += 1
            
            # Supprimer le fichier source si demandé
            if args.delete_source:
                try:
                    pdf_file.unlink()
                    print(f"   🗑️  Fichier source supprimé: {relative_path}")
                except Exception as e:
                    print(f"   ⚠️  Erreur lors de la suppression de {relative_path}: {e}")
        else:
            error_count += 1
    
    # Résumé
    print("\n" + "="*50)
    print(f"✅ Fichiers protégés: {protected_count}")
    print(f"⏭️  Fichiers ignorés (sortie existe déjà): {already_exists_count}")
    print(f"⏭️  Fichiers ignorés (déjà protégés): {skipped_count}")
    if error_count > 0:
        print(f"❌ Erreurs: {error_count}")
    print("="*50)


if __name__ == "__main__":
    main()
