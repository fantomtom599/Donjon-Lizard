"""
Point d'entrée : choix des personnages puis duel.
Lance depuis ce dossier : python3 main.py
"""

from classes import Sorcier, Paladin, Archer
from combat import duel
from utils import demander_entier


def creer_personnage(numero_joueur: int):
    nom = input(f"Nom du joueur {numero_joueur} : ").strip() or f"Joueur {numero_joueur}"

    print("\nClasse : 1=Sorcier  2=Paladin  3=Archer")
    classe = demander_entier("Ton choix : ", 1, 3)

    if classe == 1:
        return Sorcier(nom)
    if classe == 2:
        return Paladin(nom)
    return Archer(nom)


def main():
    print("=== Donjon & Lézard (prototype) ===")
    print("\nMode de jeu : 1=Solo (contre bot)  2=Multi (2 joueurs)")
    mode = demander_entier("Ton choix : ", 1, 2)
    j1 = creer_personnage(1)
    if mode == 1:
        print("\n--- Création du bot (joueur 2) ---")
        j2 = creer_personnage(2)
        duel(j1, j2, bot_b=True)
    else:
        j2 = creer_personnage(2)
        duel(j1, j2)


if __name__ == "__main__":
    main()
