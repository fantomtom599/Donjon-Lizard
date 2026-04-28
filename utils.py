"""Menus et saisies réutilisables."""


def demander_entier(message: str, minimum: int, maximum: int) -> int:
    """Demande un entier entre minimum et maximum (inclus)."""
    while True:
        try:
            valeur = int(input(message))
            if minimum <= valeur <= maximum:
                return valeur
            print(f"Choisis un nombre entre {minimum} et {maximum}.")
        except ValueError:
            print("Entrée invalide : un nombre entier est attendu.")


def afficher_barre_pv(personnage) -> None:
    """Affiche le nom et les PV actuels (tu peux améliorer l'affichage plus tard)."""
    print(f"  {personnage.nom} — PV: {personnage.pv}/{personnage.pv_max}")
