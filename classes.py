"""Personnages du jeu : classe de base + archétypes."""


class Personnage:
    """
    Base : PV + liste d'attaques.

    Modèle d'attaque (dict):
    - nom (str)
    - type: "damage" | "heal" | "buff" | "stealing_life"
    - valeur (int) : dégâts, soin, vol de vie, blocage
    - precision (float 0..1) : chance de toucher (pour damage/heal)
    - effet (dict) : pour buff (ex: bouclier/blocage)
    - crit_chance (float 0..1, optionnel) : chance de critique
    - crit_mult (float, optionnel) : multiplicateur de critique
    - cooldown (int, optionnel) : tours de recharge après utilisation
    """

    def __init__(self, nom: str, pv_max: int, attaques: list):
        self.nom = nom
        self.pv_max = pv_max
        self.pv = pv_max
        self.attaques = attaques
        self.cooldowns = [0 for _ in attaques]
        self.etats = {
            "bouclier_pct": 0.0,      # réduit les dégâts subis (0.5 => -50%)
            "bouclier_tours": 0,      # nombre de prochains coups réduits
            "blocage_prochain": False # bloque le prochain coup qui touche
        }

    def est_vivant(self) -> bool:
        return self.pv > 0

    def subir_degats(self, montant: int) -> int:
        """Enlève des PV (avec bouclier/blocage). Retourne les dégâts effectifs."""
        if montant <= 0:
            return 0

        if self.etats["blocage_prochain"]:
            self.etats["blocage_prochain"] = False
            return 0

        degats = montant
        if self.etats["bouclier_tours"] > 0 and self.etats["bouclier_pct"] > 0:
            degats = int(round(degats * (1.0 - self.etats["bouclier_pct"])))
            self.etats["bouclier_tours"] -= 1
            if self.etats["bouclier_tours"] <= 0:
                self.etats["bouclier_pct"] = 0.0
                self.etats["bouclier_tours"] = 0

        self.pv = max(0, self.pv - degats)
        return degats

    def soigner(self, montant: int) -> int:
        """Ajoute des PV sans dépasser pv_max. Retourne le soin effectif."""
        if montant <= 0:
            return 0
        avant = self.pv
        self.pv = min(self.pv_max, self.pv + montant)
        return self.pv - avant

    def appliquer_bouclier(self, pct: float, tours: int) -> None:
        self.etats["bouclier_pct"] = max(0.0, min(0.9, float(pct)))
        self.etats["bouclier_tours"] = max(0, int(tours))

    def bloquer_prochain_coup(self) -> None:
        self.etats["blocage_prochain"] = True

    def attaque(self, index_attaque: int) -> dict:
        """Retourne le dict d'attaque (la logique est gérée dans combat.py)."""
        return self.attaques[index_attaque]

    def attaque_disponible(self, index_attaque: int) -> bool:
        return self.cooldowns[index_attaque] <= 0

    def cooldown_restant(self, index_attaque: int) -> int:
        return max(0, int(self.cooldowns[index_attaque]))

    def demarrer_cooldown(self, index_attaque: int) -> None:
        cd = max(0, int(self.attaques[index_attaque].get("cooldown", 0)))
        if cd > 0:
            self.cooldowns[index_attaque] = cd

    def reduire_cooldowns(self) -> None:
        self.cooldowns = [max(0, cd - 1) for cd in self.cooldowns]


class Sorcier(Personnage):
    def __init__(self, nom: str):
        super().__init__(
            nom,
            pv_max=80,
            attaques=[
                {"nom": "Boule de feu", "type": "damage", "valeur": 26, "precision": 0.55},
                {"nom": "Éclair", "type": "damage", "valeur": 16, "precision": 0.80, "crit_chance": 0.2, "crit_mult": 1.5},
                {"nom": "Bouclier magique", "type": "buff", "valeur": 0, "precision": 1.0, "effet": {"bouclier_pct": 0.5, "bouclier_tours": 2}},
                {"nom": "Soin mineur", "type": "heal", "valeur": 18, "precision": 0.90},
            ],
        )


class Paladin(Personnage):
    def __init__(self, nom: str):
        super().__init__(
            nom,
            pv_max=120,
            attaques=[
                {"nom": "Coup de bouclier", "type": "damage", "valeur": 14, "precision": 0.85},
                {"nom": "Frappe sacrée", "type": "damage", "valeur": 28, "precision": 0.55, "cooldown": 2},
                {"nom": "Prière de soin", "type": "heal", "valeur": 22, "precision": 0.95},
                {"nom": "Protection", "type": "buff", "valeur": 0, "precision": 1.0, "effet": {"blocage_prochain": True}},
            ],
        )


class Archer(Personnage):
    def __init__(self, nom: str):
        super().__init__(
            nom,
            pv_max=90,
            attaques=[
                {"nom": "Tir précis", "type": "damage", "valeur": 14, "precision": 0.90},
                {"nom": "Tir puissant", "type": "damage", "valeur": 30, "precision": 0.45, "crit_chance": 0.3, "crit_mult": 1.6, "cooldown": 1},
                {"nom": "Bandage", "type": "heal", "valeur": 14, "precision": 0.95},
            ],
        )


class Goblin(Personnage):
    def __init__(self, nom: str):
        super().__init__(
            nom,
            pv_max=60,
            attaques=[
                {"nom": "Vol de vie", "type": "stealing_life", "valeur": 14, "precision": 0.90, "crit_chance": 0.15, "crit_mult": 1.4},
                {"nom": "Coup de poignard", "type": "damage", "valeur": 30, "precision": 0.45},
                {"nom": "Soin mineur", "type": "heal", "valeur": 14, "precision": 0.95},
            ],
        )