from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()

memory_file = os.getenv("MEMORY_PATH")

class AgentMemory():

    def __init__(self, utilisateur,fichier="memoire.txt"):
        self.fichier = memory_file + utilisateur+"-"+fichier
        self.info_memory=utilisateur+"-"+fichier
        self.create_memory()
        self.memoire = []
        self.load_memory()

    def get_info_memory(self):
        return self.info_memory

    def create_memory(self):
        """Crée un fichier mémoire vide s'il n'existe pas déjà"""
        fichier = self.fichier
        try:
            with open(fichier, "x", encoding="utf-8") as f:  # "x" = création exclusive
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] >>> Création de la mémoire de l'agent")
            print(f"Fichier '{fichier}' créé avec succès.")
        except FileExistsError:
            print(f"Le fichier '{fichier}' existe déjà.")

    def load_memory(self):
        """Charge la mémoire existante depuis le fichier"""
        if os.path.exists(self.fichier):
            with open(self.fichier, "r", encoding="utf-8") as f:
                self.memoire = [ligne.strip() for ligne in f.readlines()]
        else:
            self.memoire = []

    def save_memory(self):
        """Sauvegarde la mémoire actuelle dans le fichier"""
        with open(self.fichier, "w", encoding="utf-8") as f:
            for entree in self.memoire:
                f.write("\n" + entree)

    def update_memory(self, info: str):
        info = info.replace("\n"," ")
        """Ajoute une nouvelle information avec un horodatage"""
        entree = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] >>>  {info}"
        self.memoire.append(entree)

    def get_memories(self):
        """Rappelle les n derniers souvenirs"""
        return self.memoire

    def get_last_memories(self, n=5):
        """Rappelle les n derniers souvenirs"""
        return self.memoire[-n:]
