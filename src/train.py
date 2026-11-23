"""Entraîne et compare des modèles de routage de messages clients.

Évaluation honnête : le découpage train/test se fait par *intention* (GroupKFold),
donc le modèle est testé sur des intentions formulées autrement que dans
l'entraînement. Un second test porte sur 48 messages écrits à la main.
"""
import json
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, f1_score
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import FeatureUnion, make_pipeline
from sklearn.svm import LinearSVC

RACINE = Path(__file__).resolve().parents[1]
RES = RACINE / "results"


def vectoriseur():
    # Mots + n-grammes de caractères : robuste aux fautes de frappe
    return FeatureUnion([
        ("mots", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2)),
        ("chars", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=2)),
    ])


MODELES = {
    "Naive Bayes": lambda: make_pipeline(vectoriseur(), ComplementNB()),
    "Régression logistique": lambda: make_pipeline(vectoriseur(), LogisticRegression(max_iter=2000, C=5)),
    "SVM linéaire": lambda: make_pipeline(vectoriseur(), LinearSVC(C=0.5)),
}


def main():
    (RES / "figures").mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(RACINE / "data" / "messages.csv")
    X, y, g = df["message"], df["categorie"], df["intention"]
    cv = GroupKFold(n_splits=5)

    scores, preds = {}, {}
    for nom, fabrique in MODELES.items():
        p = cross_val_predict(fabrique(), X, y, groups=g, cv=cv)
        preds[nom] = p
        scores[nom] = round(f1_score(y, p, average="macro"), 3)
        print(f"{nom:<24} F1 macro = {scores[nom]:.3f}")

    meilleur = max(scores, key=scores.get)
    print(f"\nMeilleur modèle : {meilleur}\n")
    rapport = classification_report(y, preds[meilleur], digits=3)
    print(rapport)
    (RES / "rapport_classification.txt").write_text(rapport, encoding="utf-8")
    (RES / "scores.json").write_text(json.dumps(scores, ensure_ascii=False, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(7, 6))
    ConfusionMatrixDisplay.from_predictions(y, preds[meilleur], ax=ax, cmap="Blues",
                                            xticks_rotation=40, colorbar=False)
    ax.set_title(f"Matrice de confusion – {meilleur} (validation croisée par intention)")
    fig.tight_layout(); fig.savefig(RES / "figures" / "matrice_confusion.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3))
    ax.barh(list(scores), list(scores.values()), color=["#95a5a6", "#1f4e79", "#2e86c1"])
    ax.set_xlim(0.5, 1); ax.set_xlabel("F1 macro"); ax.set_title("Comparaison des modèles")
    for i, v in enumerate(scores.values()):
        ax.text(v + 0.005, i, f"{v:.3f}", va="center")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(RES / "figures" / "comparaison_modeles.png", dpi=150); plt.close(fig)

    final = MODELES[meilleur]().fit(X, y)
    joblib.dump(final, RES / "modele_routage.joblib")

    # Test externe : 48 messages écrits à la main, jamais vus
    tm = pd.read_csv(RACINE / "data" / "test_manuel.csv")
    externe = {}
    for nom, fabrique in MODELES.items():
        m = fabrique().fit(X, y)
        externe[nom] = round(f1_score(tm["categorie"], m.predict(tm["message"]), average="macro"), 3)
        print(f"Test manuel – {nom:<24} F1 macro = {externe[nom]:.3f}")
    (RES / "scores.json").write_text(json.dumps({"validation_croisee_par_intention": scores,
                                                 "test_manuel_48_messages": externe},
                                                ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
