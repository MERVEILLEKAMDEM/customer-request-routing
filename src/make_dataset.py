"""Construit un jeu de messages clients bancaires fictifs en français.

Les messages sont générés à partir de gabarits variés (formulations, fautes de
frappe, registres familier / formel) pour simuler un flux de mails entrants.
"""
import random
from pathlib import Path

import pandas as pd

# Chaque catégorie = des "intentions" (début de phrase) x des "détails" (fin de phrase).
# Les combinaisons donnent des centaines de formulations différentes.
GABARITS = {
    "carte_bancaire": (
        ["ma carte est bloquée", "ma carte bancaire a été avalée par le distributeur",
         "je voudrais augmenter le plafond de ma carte", "j'ai oublié le code de ma carte",
         "je n'ai pas reçu ma nouvelle carte", "mon paiement par carte est refusé",
         "je veux faire opposition sur ma carte", "ma carte ne marche plus en sans contact",
         "je souhaite commander une carte Visa Premier", "ma carte est abîmée"],
        ["{moment}", "{lieu}", "et je ne peux plus payer", "alors que j'ai de l'argent sur le compte",
         "pouvez-vous m'envoyer une nouvelle carte", "que dois-je faire ?", "c'est pénible pour mes achats"],
    ),
    "credit_immobilier": (
        ["je souhaite une simulation de prêt immobilier", "quel taux pour un crédit immobilier sur 25 ans",
         "nous voulons renégocier notre prêt", "où en est mon dossier de crédit habitat",
         "j'attends l'offre de prêt pour le notaire", "je veux faire un remboursement anticipé de mon crédit immo",
         "j'ai besoin d'un financement pour acheter un appartement", "pouvez-vous étudier notre capacité d'emprunt",
         "je voudrais moduler mes mensualités de prêt", "quelles garanties pour mon emprunt immobilier"],
        ["{lieu}", "{moment}", "pour une maison de {montant}", "avec un apport de {montant}",
         "nous sommes primo-accédants", "merci de me rappeler", "quels sont les frais de dossier ?"],
    ),
    "reclamation_frais": (
        ["je conteste les frais prélevés", "pourquoi ai-je des frais d'incident",
         "on m'a prélevé des agios", "je demande le remboursement des frais de tenue de compte",
         "la commission d'intervention est injustifiée", "vous m'avez compté deux fois la cotisation",
         "je ne suis pas d'accord avec cette facturation", "des frais bancaires abusifs apparaissent sur mon relevé",
         "je réclame le remboursement d'une pénalité", "les frais de rejet de prélèvement sont trop élevés"],
        ["de {montant}", "{moment}", "c'est inadmissible", "alors que je n'étais pas à découvert",
         "je veux être remboursé", "merci de régulariser", "je suis client depuis 15 ans"],
    ),
    "fraude": (
        ["il y a un paiement que je n'ai pas fait", "j'ai reçu un SMS bizarre et j'ai donné mon code",
         "quelqu'un a utilisé ma carte sur internet", "j'ai été victime d'une arnaque au faux conseiller",
         "des virements inconnus sont partis de mon compte", "mon compte a été piraté",
         "je ne reconnais pas une opération", "on a usurpé mon identité",
         "un prélèvement frauduleux est passé", "j'ai cliqué sur un lien de phishing"],
        ["de {montant}", "{lieu}", "{moment}", "aidez-moi vite", "URGENT", "je suis paniqué",
         "bloquez tout s'il vous plaît"],
    ),
    "epargne_placement": (
        ["je veux ouvrir un livret A", "quels sont les rendements de l'assurance vie",
         "comment verser de l'argent sur mon PEA", "je souhaite transférer mon livret vers mon compte courant",
         "pouvez-vous me conseiller un placement", "je veux clôturer mon plan épargne logement",
         "je souhaite épargner pour mes enfants", "quel est le taux du LDDS",
         "je voudrais investir en bourse", "j'aimerais diversifier mon épargne"],
        ["{montant}", "{moment}", "cette année", "pour ma retraite", "avec peu de risque",
         "merci de me rappeler", "quels sont les frais ?"],
    ),
    "gestion_compte": (
        ["je déménage et je dois changer mon adresse", "merci de m'envoyer un RIB",
         "je n'arrive pas à me connecter à l'application", "comment ajouter un bénéficiaire",
         "je veux clôturer mon compte joint", "je souhaite mettre à jour mon numéro de téléphone",
         "j'ai oublié mon identifiant", "je veux changer mon mot de passe espace client",
         "comment télécharger mes relevés", "je voudrais ajouter une procuration sur mon compte"],
        ["{lieu}", "{moment}", "merci", "le site affiche une erreur", "c'est pour mon employeur",
         "comment faire ?", "svp"],
    ),
}
MOMENTS = ["hier", "ce matin", "la semaine dernière", "depuis 3 jours", "le mois dernier", "aujourd'hui", "le 12"]
LIEUX = ["à Lyon", "à l'étranger", "à Paris", "en Espagne", "sur Amazon", "à la gare", ""]
MONTANTS = ["45 €", "120 euros", "1 500 €", "8,50€", "300 euros", "2000 €", "60€"]
DEBUTS = ["", "Bonjour, ", "Bonjour madame, ", "Salut, ", "Bonsoir, ", "Madame, Monsieur, "]
FINS = ["", " Merci.", " Cordialement.", " merci d'avance", " Bonne journée", " !!"]


def bruit(texte: str, rng: random.Random) -> str:
    """Ajoute des fautes de frappe légères (inversion ou suppression de lettre)."""
    if rng.random() < 0.3 and len(texte) > 10:
        i = rng.randrange(1, len(texte) - 2)
        texte = texte[:i] + texte[i + 1] + texte[i] + texte[i + 2:]
    if rng.random() < 0.2:
        i = rng.randrange(1, len(texte) - 1)
        texte = texte[:i] + texte[i + 1:]
    if rng.random() < 0.3:
        texte = texte.lower()
    return texte


def construire(n_par_classe=400, seed=11) -> pd.DataFrame:
    rng = random.Random(seed)
    lignes = []
    for cat, gabs in GABARITS.items():  # noqa: B007
        intentions, details = gabs
        for _ in range(n_par_classe):
            k = rng.randrange(len(intentions))
            g = (intentions[k] + " " + rng.choice(details)).format(moment=rng.choice(MOMENTS), lieu=rng.choice(LIEUX),
                                        montant=rng.choice(MONTANTS))
            txt = bruit(rng.choice(DEBUTS) + g + rng.choice(FINS), rng)
            lignes.append({"message": " ".join(txt.split()), "categorie": cat, "intention": f"{cat}_{k}"})
    df = pd.DataFrame(lignes).sample(frac=1, random_state=seed).reset_index(drop=True)
    return df


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "data" / "messages.csv"
    df = construire()
    df.to_csv(out, index=False)
    print(df["categorie"].value_counts())
