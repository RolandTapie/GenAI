import os
import ast
from collections import defaultdict

def lister_imports_dans_fichier(chemin_fichier):
    """
    Analyse un seul fichier Python pour extraire tous les imports principaux.
    """
    imports = set()
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            code = f.read()

        tree = ast.parse(code)

        for node in ast.walk(tree):
            # Capture 'import module'
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Ajoute le nom du module principal
                    imports.add(alias.name.split('.')[0])

                    # Capture 'from module import name'
            elif isinstance(node, ast.ImportFrom):
                # Ignore les imports relatifs (commençant par un point)
                if node.module and node.level == 0:
                    # Ajoute le nom du module principal
                    imports.add(node.module.split('.')[0])

    except Exception as e:
        print(f"Erreur lors de l'analyse de {chemin_fichier} : {e}")

    return imports

def parcourir_et_lister_imports(repertoire_racine, nom_fichier_liste="imports_list.txt", nom_fichier_sources="import_sources.txt"):
    """
    Parcourt récursivement le répertoire, consolide les imports et leurs sources, puis enregistre les résultats.
    """
    imports_totaux = set()
    # Utilisation d'un dictionnaire où la clé est le module et la valeur est un ensemble de fichiers
    sources_par_module = defaultdict(set)
    dossiers_exclus = {'venv', '.git', '__pycache__', 'env', 'node_modules'}

    print(f"Démarrage de l'analyse dans le répertoire : **{repertoire_racine}**")
    print(f"Exclusion des dossiers : {list(dossiers_exclus)}\n")

    # Parcourt tous les fichiers et répertoires
    for dossier_actuel, sous_dossiers, fichiers in os.walk(repertoire_racine):

        # Logique d'exclusion des dossiers pour os.walk
        sous_dossiers[:] = [d for d in sous_dossiers if d not in dossiers_exclus]

        for nom_fichier in fichiers:
            if nom_fichier.endswith(".py"):
                chemin_complet = os.path.join(dossier_actuel, nom_fichier)
                chemin_relatif = os.path.relpath(chemin_complet, repertoire_racine)

                imports = lister_imports_dans_fichier(chemin_complet)
                imports_totaux.update(imports)

                # Enregistrement de la source pour chaque module importé
                for module in imports:
                    sources_par_module[module].add(chemin_relatif)

    # Tri de la liste des imports
    imports_tries = sorted(list(imports_totaux))

    # --- 1. ENREGISTREMENT DE LA LISTE UNIQUE DES IMPORTS ---
    try:
        with open(nom_fichier_liste, "w", encoding="utf-8") as f:
            f.write("Liste des modules Python importés (principaux) :\n")
            f.write("=" * 50 + "\n")
            for module in imports_tries:
                f.write(module + "\n")
        print(f"✅ Liste des imports enregistrée dans : **{nom_fichier_liste}**")
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier {nom_fichier_liste} : {e}")

    # --- 2. ENREGISTREMENT DES SOURCES DE L'IMPORT ---
    try:
        with open(nom_fichier_sources, "w", encoding="utf-8") as f:
            f.write("Détail des Imports et leurs Fichiers Sources :\n")
            f.write("=" * 60 + "\n")

            for module in imports_tries:
                f.write(f"MODULE: {module}\n")

                # Trier les sources pour une meilleure lisibilité
                sources_tries = sorted(list(sources_par_module[module]))

                for source in sources_tries:
                    f.write(f"  - {source}\n")
                f.write("-" * 40 + "\n")

        print(f"✅ Détail des sources enregistré dans : **{nom_fichier_sources}**")
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier {nom_fichier_sources} : {e}")

    print("\n" + "="*60)
    print(f"✨ Analyse terminée. {len(imports_tries)} modules uniques trouvés.")
    print("="*60)


# --- UTILISATION DU SCRIPT ---
if __name__ == "__main__":
    REPERTOIRE_A_ANALYSER = "."

    if os.path.isdir(REPERTOIRE_A_ANALYSER):
        parcourir_et_lister_imports(REPERTOIRE_A_ANALYSER)
    else:
        print(f"Le répertoire '{REPERTOIRE_A_ANALYSER}' n'existe pas.")