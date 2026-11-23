"""Route un message vers la bonne équipe et fixe sa priorité.

Usage : python src/route.py "Quelqu'un a utilisé ma carte sur internet"
"""
import re
import sys
from pathlib import Path

import joblib

MODELE = Path(__file__).resolve().parents[1] / "results" / "modele_routage.joblib"

EQUIPES = {
    "carte_bancaire": "Service Cartes",
    "credit_immobilier": "Pôle Crédit Habitat",
    "reclamation_frais": "Service Réclamations",
    "fraude": "Cellule Fraude",
    "epargne_placement": "Conseillers Patrimoine",
    "gestion_compte": "Back-office Comptes",
}
MOTS_URGENTS = re.compile(r"urgent|vite|piraté|arnaque|bloqu|vol|perdu|inconnu", re.I)


def router(message: str, modele=None) -> dict:
    modele = modele or joblib.load(MODELE)
    cat = modele.predict([message])[0]
    urgent = cat == "fraude" or bool(MOTS_URGENTS.search(message))
    return {
        "categorie": cat,
        "equipe": EQUIPES[cat],
        "priorite": "P1 – sous 1 h" if urgent else "P3 – sous 48 h",
    }


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) or "Bonjour, je ne reconnais pas un paiement de 89 € sur mon compte"
    print(msg, "\n->", router(msg))
