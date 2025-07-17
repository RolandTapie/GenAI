
# 🧠 Agent IA – Interaction avec Fonctions & Serveur MCP

## 🗂️ Description du projet

Ce projet met en œuvre un **agent conversationnel intelligent** capable de répondre à des requêtes en langage naturel. Il est conçu pour fonctionner selon deux modes :

1. **Appels directs aux fonctions/tools** : l'agent utilise des fonctions Python locales pour répondre ou effectuer des actions.
2. **Intégration avec un serveur MCP** : l'agent délègue les appels de fonction à un serveur MCP (Multi-Channel Processing) via une interface CLI, permettant une architecture plus distribuée.

---

## ⚙️ Fonctionnalités principales

- Compréhension du langage naturel.
- Exécution directe de fonctions Python.
- Interaction avec un serveur MCP distant.
- Planification de rendez-vous, récupération de données contextuelles (ex. météo).
- Support multilingue (ex. français démontré).

---

## 🧩 Librairies Python utilisées

| Librairie              | Description |
|------------------------|-------------|
| `openai`               | Accès aux modèles de langage d'OpenAI. |
| `python-dotenv`        | Gestion des variables d’environnement via fichiers `.env`. |
| `mcp[cli]`             | Interface CLI pour serveur MCP (nécessite Node.js). |

---

## 🖥️ Prérequis

- Python 3.9 ou supérieur
- Node.js (pour le serveur MCP)
- Clé API OpenAI (fichier `.env` requis)

---

## 🚀 Lancer le projet

### 1. Cloner le dépôt

```bash
git clone <url-du-depot>
cd <nom-du-projet>
```

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Créer un fichier `.env`

```env
OPENAI_API_KEY=your_openai_key_here
```

### 4. Lancer un test simple

```bash
python test_openai.py
```

### 5. (Optionnel) Lancer le serveur MCP

```bash
npm install -g @mcp/cli
mcp start
```

---

## 📁 Structure du projet

```bash
.
├── src/
│   ├── ChatBot_LangChain.py     # Version de l'agent avec LangChain
│   ├── ChatBot_Mistral.py       # Variante utilisant un autre modèle
├── serveur.py                   # Interaction avec le serveur MCP
├── test_openai.py               # Script de test de l'agent
├── prompt.py                    # Fichier de définition des prompts
├── tools.json                   # Déclaration des outils fonctionnels
```

---

## 📸 Exemple d'interaction

```plaintext
Roland : quelle est la temperature actuelle à Bruxelles?
🤖 : La température actuelle à Bruxelles est de 23 degrés.

Roland : fixe un rendez-vous avec Jean dans mon agenda, demain 10h00 pour la présentation d'un nouveau produit.
🤖 : Le rendez-vous avec Jean a été fixé dans votre agenda pour demain à 10h00.
```

---

## 📌 Remarques

- L’architecture du projet permet facilement d’ajouter de nouveaux outils (tools/functions).
- Le serveur MCP étend les capacités de l’agent via un système modulaire orienté services.
- L’agent est adaptable à d'autres langues et cas d'usage métier.

---

## 📄 Licence

Ce projet est distribué sous licence MIT (ou à personnaliser).
