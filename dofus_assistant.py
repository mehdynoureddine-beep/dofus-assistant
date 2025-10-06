#!/usr/bin/env python3
"""Assistant Dofus Rétro - Application locale (Tkinter)
Usage: Lancer, fournir une clé OpenAI (si tu veux utiliser l'API), puis discuter.
Fonctionnalités :
- Chat local (interactions avec l'API OpenAI si clé fournie)
- Sauvegarde du profil perso (niveau, métiers, stuff)
- Calcul basique de craft / besoins à partir d'une base locale JSON
- Aucune automatisation du jeu — conforme aux CGU Ankama
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json, os, threading

try:
    import openai
except Exception:
    openai = None

APP_DATA = os.path.join(os.path.expanduser('~'), '.dofus_assistant')
os.makedirs(APP_DATA, exist_ok=True)
PROFILE_PATH = os.path.join(APP_DATA, 'profile.json')
RECIPES_PATH = os.path.join(APP_DATA, 'recipes.json')

DEFAULT_RECIPES = {
    "Anneau Agile": {"level":10, "ingredients":{"Cuir de Bouftou":2,"Bois de Châtaigner":3}},
    "Anneau Chanceux": {"level":60, "ingredients":{"Cuir du Tofu Maléfique":4,"Or":1}}
}

def load_recipes():
    if not os.path.exists(RECIPES_PATH):
        with open(RECIPES_PATH,'w',encoding='utf-8') as f:
            json.dump(DEFAULT_RECIPES,f,ensure_ascii=False,indent=2)
    with open(RECIPES_PATH,'r',encoding='utf-8') as f:
        return json.load(f)

def save_profile(profile):
    with open(PROFILE_PATH,'w',encoding='utf-8') as f:
        json.dump(profile,f,ensure_ascii=False,indent=2)

def load_profile():
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH,'r',encoding='utf-8') as f:
            return json.load(f)
    return {"name":"", "class":"Sacrieur", "level":121, "orientation":"Eau/Sagesse", "MP":6, "PA":12, "vitality":1400, "server":"Riktus", "note":""}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assistant Dofus Rétro - Local")
        self.geometry("800x600")
        self.profile = load_profile()
        self.recipes = load_recipes()
        self.openai_key = ""
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(fill='both', expand=True, padx=8, pady=8)

        left = ttk.Frame(frm)
        left.pack(side='left', fill='y', padx=(0,8))

        ttk.Label(left, text="Profil").pack(anchor='w')
        self.name_var = tk.StringVar(value=self.profile.get("name",""))
        ttk.Entry(left, textvariable=self.name_var).pack(fill='x')
        ttk.Label(left, text="Classe / Orientation").pack(anchor='w', pady=(6,0))
        self.cls_var = tk.StringVar(value=self.profile.get("class","Sacrieur"))
        ttk.Entry(left, textvariable=self.cls_var).pack(fill='x')
        ttk.Label(left, text="Niveau").pack(anchor='w', pady=(6,0))
        self.level_var = tk.IntVar(value=self.profile.get("level",121))
        ttk.Spinbox(left, from_=1, to=200, textvariable=self.level_var).pack(fill='x')

        ttk.Button(left, text="Sauvegarder profil", command=self.save_profile).pack(fill='x', pady=(8,0))
        ttk.Button(left, text="Importer recettes", command=self.import_recipes).pack(fill='x', pady=(4,0))
        ttk.Button(left, text="Ouvrir dossier de données", command=self.open_data_folder).pack(fill='x', pady=(4,0))

        ttk.Separator(frm, orient='vertical').pack(side='left', fill='y', padx=8)

        right = ttk.Frame(frm)
        right.pack(side='left', fill='both', expand=True)

        # OpenAI Key
        toprow = ttk.Frame(right)
        toprow.pack(fill='x')
        ttk.Label(toprow, text="Clé OpenAI (optionnelle)").pack(side='left')
        self.key_var = tk.StringVar(value=os.environ.get('OPENAI_API_KEY',''))
        ttk.Entry(toprow, textvariable=self.key_var, show='*', width=40).pack(side='left', padx=(8,0))
        ttk.Button(toprow, text="Tester clé", command=self.test_key).pack(side='left', padx=(6,0))

        # Chat area
        self.chat = scrolledtext.ScrolledText(right, wrap='word', state='disabled', height=18)
        self.chat.pack(fill='both', expand=True, pady=(8,0))

        entryrow = ttk.Frame(right)
        entryrow.pack(fill='x', pady=(6,0))
        self.input_var = tk.StringVar()
        ttk.Entry(entryrow, textvariable=self.input_var).pack(side='left', fill='x', expand=True)
        ttk.Button(entryrow, text="Envoyer", command=self.on_send).pack(side='left', padx=(6,0))
        ttk.Button(entryrow, text="Assistant local", command=self.local_help).pack(side='left', padx=(6,0))

        # Recipes quick access
        botrow = ttk.Frame(right)
        botrow.pack(fill='x', pady=(6,0))
        ttk.Label(botrow, text="Recette rapide").pack(side='left')
        self.recipe_cb = ttk.Combobox(botrow, values=list(self.recipes.keys()))
        self.recipe_cb.pack(side='left', padx=(8,0))
        ttk.Button(botrow, text="Voir recette", command=self.show_recipe).pack(side='left', padx=(6,0))
        ttk.Button(botrow, text="Calcul besoins", command=self.calc_needs).pack(side='left', padx=(6,0))

        self.log("Assistant Dofus Rétro — prêt. Pas d'automatisation, usage hors-client.")

    def open_data_folder(self):
        import webbrowser, pathlib
        webbrowser.open(os.path.join(os.path.expanduser('~'), '.dofus_assistant'))

    def save_profile(self):
        self.profile.update({
            "name": self.name_var.get(),
            "class": self.cls_var.get(),
            "level": int(self.level_var.get())
        })
        save_profile(self.profile)
        self.log("Profil sauvegardé.")

    def import_recipes(self):
        path = filedialog.askopenfilename(title="Importer recettes JSON", filetypes=[("JSON files","*.json")])
        if path:
            try:
                with open(path,'r',encoding='utf-8') as f:
                    data = json.load(f)
                with open(RECIPES_PATH,'w',encoding='utf-8') as f:
                    json.dump(data,f,ensure_ascii=False,indent=2)
                self.recipes = data
                self.recipe_cb['values'] = list(self.recipes.keys())
                self.log("Recettes importées.")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def test_key(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showinfo("Info","Aucune clé fournie. L'assistant fonctionnera en local sans accès API.")
            return
        if openai is None:
            messagebox.showwarning("OpenAI missing","Le paquet 'openai' n'est pas installé dans cet environnement. L'API ne pourra pas être contactée.")
            return
        try:
            openai.api_key = key
            # Petit test : liste des modèles (s'il est disponible)
            openai.Model.list()
            messagebox.showinfo("Succès","Clé valide et API accessible.")
            self.openai_key = key
        except Exception as e:
            messagebox.showerror("Erreur clé", str(e))

    def on_send(self):
        txt = self.input_var.get().strip()
        if not txt:
            return
        self.append_chat("Tu", txt)
        self.input_var.set("")
        # traite localement quelques commandes
        if txt.lower().startswith("/profile"):
            self.append_chat("Bot", json.dumps(self.profile, ensure_ascii=False, indent=2))
            return
        if txt.lower().startswith("/recipes"):
            self.append_chat("Bot", json.dumps(self.recipes, ensure_ascii=False, indent=2))
            return
        if txt.lower().startswith("/help"):
            self.append_chat("Bot", "Commandes : /profile, /recipes, /recipe <nom>, /needs <nom>")
            return
        if txt.lower().startswith("/recipe "):
            name = txt[8:].strip()
            r = self.recipes.get(name)
            if r:
                self.append_chat("Bot", json.dumps(r, ensure_ascii=False, indent=2))
            else:
                self.append_chat("Bot", f"Recette '{name}' introuvable.")
            return
        if txt.lower().startswith("/needs "):
            name = txt[7:].strip()
            r = self.recipes.get(name)
            if r:
                self.append_chat("Bot", "Calcul des besoins :\\n" + "\\n".join(f\"{k}: {v}\" for k,v in r.get('ingredients',{}).items()))
            else:
                self.append_chat("Bot", f"Recette '{name}' introuvable.")
            return
        # sinon, si clé openai fournie, interroger l'API dans un thread
        if self.key_var.get().strip() and openai is not None:
            threading.Thread(target=self.call_openai, args=(txt,)).start()
        else:
            # réponse locale simple
            self.append_chat("Bot", "Je suis en mode local. Fournis une clé OpenAI pour des réponses enrichies.\nCommandes : /help")

    def append_chat(self, who, text):
        self.chat.config(state='normal')
        self.chat.insert('end', f"{who}: {text}\\n\\n")
        self.chat.see('end')
        self.chat.config(state='disabled')

    def call_openai(self, txt):
        try:
            openai.api_key = self.key_var.get().strip()
            system = "Tu es un assistant Dofus Rétro. Tu aides le joueur sans proposer d'automatisation. Sois concis en français."
            messages = [{"role":"system","content":system},{"role":"user","content":txt}]
            resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages, max_tokens=600)
            answer = resp['choices'][0]['message']['content']
        except Exception as e:
            answer = "Erreur API: " + str(e)
        self.append_chat("Bot", answer)

if __name__ == '__main__':
    app = App()
    app.mainloop()
