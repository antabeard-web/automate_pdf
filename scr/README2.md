# Protection automatique de PDFs avec mots de passe uniques

Ce script Python protège en écriture tous les fichiers PDF d'un répertoire avec des **mots de passe uniques et forts** générés automatiquement. Les mots de passe ne sont pas sauvegardés - parfait pour une protection maximale sans risque de fuite. Si necessaire resortez les documents

## 📋 Prérequis

Installer la bibliothèque `pikepdf` :

```bash
pip install pikepdf
```

## 🚀 Utilisation

### Commande de base :
```bash
python protect_pdfs.py -i /chemin/source -o /chemin/destination
```

### Avec les sous-répertoires :
```bash
python protect_pdfs.py -i /chemin/source -o /chemin/destination -r
```

### Avec longueur de mot de passe personnalisée :
```bash
python protect_pdfs.py -i /chemin/source -o /chemin/destination --password-length 30
```

## 📝 Paramètres

- `-i` ou `--input` : Répertoire d'entrée contenant les PDFs à protéger (obligatoire)
- `-o` ou `--output` : Répertoire de sortie pour les PDFs protégés (obligatoire)
- `-r` ou `--recursive` : Traiter aussi les sous-répertoires (optionnel)
- `--password-length` : Longueur des mots de passe générés (défaut: 20 caractères)

## ✨ Fonctionnalités

- ✅ **Génération automatique** de mots de passe forts et uniques pour chaque PDF
- ✅ Mots de passe cryptographiquement sûrs (lettres, chiffres, symboles)
- ✅ **Aucune sauvegarde des mots de passe** - sécurité maximale
- ✅ Préserve la structure des dossiers (en mode récursif)
- ✅ Protège uniquement les fichiers non encore protégés
- ✅ Les PDFs restent lisibles sans mot de passe
- ✅ Le mot de passe est requis pour modifier les PDFs

## 📖 Exemples

### Exemple 1 : Répertoire simple
```bash
python protect_pdfs.py -i ./pdfs_originaux -o ./pdfs_proteges
```

### Exemple 2 : Avec sous-dossiers
```bash
python protect_pdfs.py -i "C:\Documents\PDFs" -o "C:\Documents\PDFs_Proteges" --recursive
```

### Exemple 3 : Mots de passe extra-longs (30 caractères)
```bash
python protect_pdfs.py -i ./input -o ./output --password-length 30
```

## 🔒 Sécurité

**Mots de passe générés :**
- Longueur par défaut : 20 caractères (configurable)
- Contiennent : lettres (a-z, A-Z), chiffres (0-9), symboles (!@#$%^&*...)
- Générés avec le module `secrets` de Python (cryptographiquement sûr)
- **Uniques pour chaque fichier** - impossible à deviner
- **Non sauvegardés** - sécurité maximale contre les fuites

**Protection appliquée :**
- Permet la **lecture** sans mot de passe
- Requiert le mot de passe pour **modifier** le document
- Bloque l'impression haute résolution, les modifications, etc.

## ⚠️ Important

**Les mots de passe ne sont PAS sauvegardés !**

- Une fois protégés, les PDFs **ne pourront plus être modifiés** sans le mot de passe
- Si vous devez modifier un PDF, vous devrez **recréer le document** depuis la source originale
- C'est idéal pour les factures, documents finaux, ou tout fichier que vous ne modifierez plus
- Conservez toujours une **copie de sauvegarde** de vos PDFs originaux avant de les protéger

## 💡 Cas d'usage recommandés

✅ **Parfait pour :**
- Factures finales envoyées aux clients
- Documents administratifs finalisés
- Rapports finaux
- Tout document que vous ne modifierez plus jamais

❌ **Déconseillé pour :**
- Documents en cours de rédaction
- Fichiers que vous devez modifier régulièrement
- Documents dont vous pourriez avoir besoin de modifier le contenu

## 📁 Structure générée

Si vous avez :
```
/input
  ├── factures/
  │   ├── 2024.pdf
  │   └── 2025.pdf
  └── contrats/
      └── contrat1.pdf
```

Le script créera :
```
/output
  ├── factures/
  │   ├── 2024.pdf (protégé, mot de passe unique non sauvegardé)
  │   └── 2025.pdf (protégé, mot de passe unique non sauvegardé)
  └── contrats/
      └── contrat1.pdf (protégé, mot de passe unique non sauvegardé)
```
