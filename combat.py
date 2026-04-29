"""Boucle de combat tour par tour."""

import random

from utils import demander_entier, afficher_barre_pv


def choisir_attaque_bot(personnage, adversaire) -> int:
    """
    Bot simple:
    - si PV bas, tente un soin
    - sinon choisit le meilleur dégât "attendu" (valeur * précision)
    """
    # Si on est sous 40%, on cherche un heal
    if personnage.pv <= int(personnage.pv_max * 0.4):
        heals = [i for i, a in enumerate(personnage.attaques) if a.get("type") == "heal"]
        if heals:
            return heals[0]

    meilleur_index = 0
    meilleur_score = -1.0
    for i, att in enumerate(personnage.attaques):
        t = att.get("type")
        if t == "damage":
            score = float(att.get("valeur", 0)) * float(att.get("precision", 1.0))
        elif t == "stealing_life":
            # Slightly favor lifesteal over pure damage for sustain.
            score = float(att.get("valeur", 0)) * float(att.get("precision", 1.0)) + 2.0
        elif t == "buff":
            score = 1.0  # valeur fixe faible
        else:  # heal
            score = 0.5
        if score > meilleur_score:
            meilleur_score = score
            meilleur_index = i
    return meilleur_index


def _touche(precision: float) -> bool:
    return random.random() < max(0.0, min(1.0, float(precision)))


def duel(joueur_a, joueur_b, bot_b: bool = False):
    """
    Combat jusqu'à ce qu'un personnage tombe à 0 PV.
    joueur_a commence. À toi d'ajouter : critique, défense, objets, etc.
    """
    actif, passif = joueur_a, joueur_b

    while actif.est_vivant() and passif.est_vivant():
        print("\n--- Tour ---")
        afficher_barre_pv(joueur_a)
        afficher_barre_pv(joueur_b)
        print(f"\nC'est au tour de {actif.nom}.")

        for i, att in enumerate(actif.attaques):
            t = att.get("type")
            if t == "damage":
                infos = f"{att['valeur']} dégâts, {int(att['precision'] * 100)}% précision"
            elif t == "heal":
                infos = f"{att['valeur']} soin, {int(att['precision'] * 100)}% précision"
            elif t == "stealing_life":
                infos = f"{att['valeur']} dégâts + soin, {int(att['precision'] * 100)}% précision"
            else:
                infos = "effet (buff)"
            print(f"  {i + 1}. {att['nom']} ({infos})")

        if bot_b and actif is joueur_b:
            index = choisir_attaque_bot(actif, passif)
            print(f"(Bot) Choix: {index + 1}")
        else:
            choix = demander_entier(
                "Numéro de l'attaque : ",
                1,
                len(actif.attaques),
            )
            index = choix - 1

        att = actif.attaque(index)
        nom_att = att["nom"]
        type_att = att.get("type")

        if type_att in ("damage", "heal", "stealing_life"):
            if not _touche(att.get("precision", 1.0)):
                print(f"{actif.nom} utilise {nom_att}… mais ça rate !")
                actif, passif = passif, actif
                continue

        if type_att == "damage":
            degats = passif.subir_degats(int(att["valeur"]))
            if degats == 0:
                print(f"{actif.nom} utilise {nom_att} → bloqué !")
            else:
                print(f"{actif.nom} utilise {nom_att} → {degats} dégâts !")
        elif type_att == "heal":
            soin = actif.soigner(int(att["valeur"]))
            print(f"{actif.nom} utilise {nom_att} → +{soin} PV !")

        elif type_att == "stealing_life":
            degats = passif.subir_degats(int(att["valeur"]))
            soin = actif.soigner(degats)
            print(f"{actif.nom} utilise {nom_att} → {degats} dégâts et +{soin} PV !")

        elif type_att == "buff":
            effet = att.get("effet", {})
            if "bouclier_pct" in effet and "bouclier_tours" in effet:
                actif.appliquer_bouclier(effet["bouclier_pct"], effet["bouclier_tours"])
                print(f"{actif.nom} lance {nom_att} → bouclier activé !")
            elif effet.get("blocage_prochain"):
                actif.bloquer_prochain_coup()
                print(f"{actif.nom} utilise {nom_att} → bloquera le prochain coup !")
            else:
                print(f"{actif.nom} utilise {nom_att}.")
        else:
            print(f"{actif.nom} hésite… (attaque inconnue)")

        actif, passif = passif, actif

    gagnant = joueur_a if joueur_a.est_vivant() else joueur_b
    print(f"\n*** {gagnant.nom} remporte le duel ! ***")
    return gagnant
