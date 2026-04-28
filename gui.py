"""Interface graphique Tkinter
Fichier à lancer pour lancer le jeu 
A faire evoluer 
"""

import random
import tkinter as tk
import customtkinter as ctk  # type: ignore[reportMissingImports]

from classes import Archer, Paladin, Sorcier
from combat import choisir_attaque_bot


def _touche(precision: float) -> bool:
    return random.random() < max(0.0, min(1.0, float(precision)))


def _creer_personnage(classe_nom: str, nom: str):
    mapping = {
        "Sorcier": Sorcier,
        "Paladin": Paladin,
        "Archer": Archer,
    }
    return mapping[classe_nom](nom)


class JeuGUI:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Donjon & Lezard")
        self.root.geometry("820x560")

        self.j1 = None
        self.j2 = None
        self.tour_j1 = True
        self.partie_terminee = False

        self.mode_var = tk.StringVar(value="Solo")
        self.nom1_var = tk.StringVar(value="Joueur 1")
        self.classe1_var = tk.StringVar(value="Sorcier")
        self.nom2_var = tk.StringVar(value="Bot")
        self.classe2_var = tk.StringVar(value="Paladin")

        self._construire_ui()

    def _construire_ui(self):
        top = ctk.CTkFrame(self.root)
        top.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(top, text="Configuration").grid(row=0, column=0, columnspan=7, padx=6, pady=(6, 2), sticky="w")

        ctk.CTkLabel(top, text="Mode").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkComboBox(top, variable=self.mode_var, values=["Solo", "Multi"], width=120).grid(
            row=1, column=1, padx=6, pady=6, sticky="w"
        )

        ctk.CTkLabel(top, text="Nom J1").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(top, textvariable=self.nom1_var, width=140).grid(row=1, column=3, padx=6, pady=6)
        ctk.CTkLabel(top, text="Classe J1").grid(row=1, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkComboBox(top, variable=self.classe1_var, values=["Sorcier", "Paladin", "Archer"], width=120).grid(
            row=1, column=5, padx=6, pady=6
        )

        ctk.CTkLabel(top, text="Nom J2").grid(row=2, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(top, textvariable=self.nom2_var, width=140).grid(row=2, column=3, padx=6, pady=6)
        ctk.CTkLabel(top, text="Classe J2").grid(row=2, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkComboBox(top, variable=self.classe2_var, values=["Sorcier", "Paladin", "Archer"], width=120).grid(
            row=2, column=5, padx=6, pady=6
        )

        ctk.CTkButton(top, text="Nouvelle partie", command=self.demarrer_partie).grid(row=1, column=6, rowspan=2, padx=10, pady=6)

        info = ctk.CTkFrame(self.root)
        info.pack(fill="x", padx=10, pady=4)

        self.label_pv_j1 = ctk.CTkLabel(info, text="J1: -")
        self.label_pv_j1.pack(side="left", padx=8)
        self.label_pv_j2 = ctk.CTkLabel(info, text="J2: -")
        self.label_pv_j2.pack(side="left", padx=8)
        self.label_tour = ctk.CTkLabel(info, text="Tour: -")
        self.label_tour.pack(side="right", padx=8)

        self.frame_attaques = ctk.CTkFrame(self.root)
        self.frame_attaques.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(self.frame_attaques, text="Actions du joueur actif").pack(anchor="w", padx=8, pady=(6, 2))

        self.log = ctk.CTkTextbox(self.root, height=320)
        self.log.configure(state="disabled")
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

        self._log("Bienvenue ! Choisis la config puis clique sur 'Nouvelle partie'.")

    def _log(self, message: str):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def demarrer_partie(self):
        nom1 = self.nom1_var.get().strip() or "Joueur 1"
        nom2 = self.nom2_var.get().strip() or ("Bot" if self.mode_var.get() == "Solo" else "Joueur 2")
        self.j1 = _creer_personnage(self.classe1_var.get(), nom1)
        self.j2 = _creer_personnage(self.classe2_var.get(), nom2)
        self.tour_j1 = True
        self.partie_terminee = False

        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self._log("Nouvelle partie lancee.")
        self._log(f"{self.j1.nom} ({self.classe1_var.get()}) vs {self.j2.nom} ({self.classe2_var.get()})")

        self._rafraichir_ui()
        self._maj_boutons_actions()

    def _personnages_actifs(self):
        if self.tour_j1:
            return self.j1, self.j2
        return self.j2, self.j1

    def _rafraichir_ui(self):
        if not self.j1 or not self.j2:
            return
        self.label_pv_j1.configure(text=f"{self.j1.nom}: {self.j1.pv}/{self.j1.pv_max} PV")
        self.label_pv_j2.configure(text=f"{self.j2.nom}: {self.j2.pv}/{self.j2.pv_max} PV")
        actif = self.j1 if self.tour_j1 else self.j2
        self.label_tour.configure(text=f"Tour: {actif.nom}")

    def _vider_actions(self):
        for widget in self.frame_attaques.winfo_children():
            widget.destroy()

    def _maj_boutons_actions(self):
        self._vider_actions()
        if not self.j1 or not self.j2 or self.partie_terminee:
            return

        actif, _ = self._personnages_actifs()
        solo_bot = self.mode_var.get() == "Solo"
        if solo_bot and actif is self.j2:
            ctk.CTkLabel(self.frame_attaques, text="Le bot joue...").pack(anchor="w", padx=8, pady=8)
            self.root.after(700, self._tour_bot)
            return

        ctk.CTkLabel(self.frame_attaques, text=f"Choisis l'action pour {actif.nom}:").pack(anchor="w", padx=8, pady=6)
        for idx, att in enumerate(actif.attaques):
            details = self._description_attaque(att)
            texte = f"{idx + 1}. {att['nom']} ({details})"
            ctk.CTkButton(
                self.frame_attaques,
                text=texte,
                command=lambda i=idx: self._jouer_action(i),
            ).pack(fill="x", padx=8, pady=3)

    def _description_attaque(self, att: dict) -> str:
        t = att.get("type")
        if t == "damage":
            return f"{att['valeur']} degats, {int(att['precision'] * 100)}% precision"
        if t == "heal":
            return f"{att['valeur']} soin, {int(att['precision'] * 100)}% precision"
        if t == "buff":
            effet = att.get("effet", {})
            if "bouclier_pct" in effet:
                return f"bouclier {int(effet['bouclier_pct'] * 100)}% ({effet['bouclier_tours']} coups)"
            if effet.get("blocage_prochain"):
                return "bloque le prochain coup"
        return "effet"

    def _jouer_action(self, index: int):
        if self.partie_terminee:
            return
        actif, passif = self._personnages_actifs()
        att = actif.attaque(index)
        self._executer_action(actif, passif, att)

        if self._verifier_fin_partie():
            return

        self.tour_j1 = not self.tour_j1
        self._rafraichir_ui()
        self._maj_boutons_actions()

    def _tour_bot(self):
        if self.partie_terminee:
            return
        actif, passif = self._personnages_actifs()
        if self.mode_var.get() != "Solo" or actif is not self.j2:
            return
        index = choisir_attaque_bot(actif, passif)
        att = actif.attaque(index)
        self._log(f"(Bot) choisit: {att['nom']}")
        self._executer_action(actif, passif, att)

        if self._verifier_fin_partie():
            return

        self.tour_j1 = not self.tour_j1
        self._rafraichir_ui()
        self._maj_boutons_actions()

    def _executer_action(self, actif, passif, att: dict):
        nom_att = att["nom"]
        type_att = att.get("type")

        if type_att in ("damage", "heal") and not _touche(att.get("precision", 1.0)):
            self._log(f"{actif.nom} utilise {nom_att}... mais ca rate.")
            self._rafraichir_ui()
            return

        if type_att == "damage":
            degats = passif.subir_degats(int(att["valeur"]))
            if degats == 0:
                self._log(f"{actif.nom} utilise {nom_att} -> bloque.")
            else:
                self._log(f"{actif.nom} utilise {nom_att} -> {degats} degats.")
        elif type_att == "heal":
            soin = actif.soigner(int(att["valeur"]))
            self._log(f"{actif.nom} utilise {nom_att} -> +{soin} PV.")
        elif type_att == "buff":
            effet = att.get("effet", {})
            if "bouclier_pct" in effet and "bouclier_tours" in effet:
                actif.appliquer_bouclier(effet["bouclier_pct"], effet["bouclier_tours"])
                self._log(f"{actif.nom} active un bouclier.")
            elif effet.get("blocage_prochain"):
                actif.bloquer_prochain_coup()
                self._log(f"{actif.nom} bloquera le prochain coup.")
            else:
                self._log(f"{actif.nom} utilise {nom_att}.")
        else:
            self._log(f"{actif.nom} hesite... action inconnue.")
        self._rafraichir_ui()

    def _verifier_fin_partie(self) -> bool:
        if self.j1.est_vivant() and self.j2.est_vivant():
            return False
        self.partie_terminee = True
        gagnant = self.j1 if self.j1.est_vivant() else self.j2
        self._log(f"*** {gagnant.nom} remporte le duel ! ***")
        self._maj_boutons_actions()
        return True


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    JeuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
