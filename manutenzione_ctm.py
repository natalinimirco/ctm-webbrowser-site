#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pannello di Manutenzione CTM Browser
=====================================
Piccola interfaccia grafica con 3 pulsanti per le operazioni ripetute più
di frequente durante lo sviluppo, cosi' non serve ricordarsi comandi o
procedure da terminale:

  1. Pulisci cartella progetto  -> pulizia.py (anteprima o esecuzione)
  2. Crea app Windows            -> stessa sequenza di build_ctm.bat
                                     (PyArmor + PyInstaller + hash + Inno Setup)
  3. Pubblica su GitHub          -> stessa sequenza di push_reset.ps1
                                     (reset repository locale + push forzato)

L'output di ogni comando viene mostrato IN TEMPO REALE dentro la finestra
stessa (non in una finestra nera separata che potrebbe chiudersi da sola
prima di riuscire a leggere qualcosa) e salvato automaticamente in
log_manutenzione.txt per poterlo rivedere o incollare in una richiesta di
assistenza.

Uso: doppio clic su Manutenzione_CTM.bat (lancia questo script).
"""

import os
import sys
import subprocess
import threading
import datetime
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

# ── CONFIGURAZIONE ────────────────────────────────────────────────────────
CARTELLA_PROGETTO = os.path.dirname(os.path.abspath(__file__))
REPO_URL = "https://github.com/natalinimirco/CTM-BROWSER.git"
BRANCH = "main"
LOG_FILE = os.path.join(CARTELLA_PROGETTO, "log_manutenzione.txt")

FILE_DA_OFFUSCARE = [
    "app.py", "run.py", "ctm_sistema.py", "ctm_licenza.py",
    "ctm_notifiche.py", "ctm_dati.py", "ctm_routes_extra.py",
    "ctm_diagnostica.py",
]


class PannelloManutenzione:
    def __init__(self, root):
        self.root = root
        self.in_esecuzione = False
        root.title("CTM Browser — Pannello di Manutenzione")
        root.geometry("880x600")
        root.configure(bg="#1e3a5f")

        titolo = tk.Label(
            root, text="CTM Browser — Pannello di Manutenzione",
            font=("Segoe UI", 14, "bold"), bg="#1e3a5f", fg="white", pady=10,
        )
        titolo.pack(fill=tk.X)

        sottotitolo = tk.Label(
            root, text=f"Cartella: {CARTELLA_PROGETTO}",
            font=("Segoe UI", 9), bg="#1e3a5f", fg="#b8c9dc",
        )
        sottotitolo.pack(fill=tk.X, pady=(0, 10))

        # ── Pulsanti ──────────────────────────────────────────────
        frame_pulsanti = tk.Frame(root, bg="#1e3a5f")
        frame_pulsanti.pack(pady=5)

        self.btn_pulisci = self._crea_pulsante(
            frame_pulsanti, "🧹  Pulisci cartella progetto",
            self.pulisci, "#4a90d9", col=0,
        )
        self.btn_build = self._crea_pulsante(
            frame_pulsanti, "🔨  Crea app Windows",
            self.crea_app_windows, "#4a90d9", col=1,
        )
        self.btn_push = self._crea_pulsante(
            frame_pulsanti, "☁️  Pubblica su GitHub",
            self.pubblica_github, "#c0392b", col=2,
        )

        # ── Area di log ───────────────────────────────────────────
        self.log_widget = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, bg="#0d1117", fg="#58d68d",
            insertbackground="white", font=("Consolas", 10), padx=8, pady=8,
        )
        self.log_widget.pack(fill=tk.BOTH, expand=True, padx=12, pady=(5, 5))
        self.log_widget.tag_config("errore", foreground="#ff6b6b")
        self.log_widget.tag_config("ok", foreground="#58d68d")
        self.log_widget.tag_config("comando", foreground="#5dade2")
        self.log_widget.tag_config("info", foreground="#f4d03f")

        # ── Barra di stato ────────────────────────────────────────
        self.stato = tk.Label(
            root, text="Pronto.", anchor="w",
            bg="#16314f", fg="white", font=("Segoe UI", 9), padx=10, pady=4,
        )
        self.stato.pack(fill=tk.X, side=tk.BOTTOM)

        self._log("Pronto. Scegli un'operazione dai pulsanti sopra.\n", "info")
        self._log(f"Ogni operazione viene salvata anche in: {LOG_FILE}\n\n", "info")

    def _crea_pulsante(self, parent, testo, comando, colore, col):
        b = tk.Button(
            parent, text=testo, command=comando, width=26, height=2,
            bg=colore, fg="white", font=("Segoe UI", 10, "bold"),
            activebackground=colore, relief=tk.FLAT, cursor="hand2",
        )
        b.grid(row=0, column=col, padx=8)
        return b

    # ── Utilità di log ───────────────────────────────────────────
    def _log(self, testo, tag=None):
        def _scrivi():
            self.log_widget.insert(tk.END, testo, tag)
            self.log_widget.see(tk.END)
        self.root.after(0, _scrivi)
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(testo)
        except Exception:
            pass

    def _imposta_stato(self, testo):
        self.root.after(0, lambda: self.stato.config(text=testo))

    def _blocca_pulsanti(self, blocca=True):
        stato = tk.DISABLED if blocca else tk.NORMAL
        for b in (self.btn_pulisci, self.btn_build, self.btn_push):
            self.root.after(0, lambda b=b: b.config(state=stato))
        self.in_esecuzione = blocca

    def _intestazione_sessione(self, titolo):
        self._log(f"\n{'='*70}\n", "comando")
        self._log(f" {titolo} — {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n", "comando")
        self._log(f"{'='*70}\n", "comando")

    def _esegui_comando(self, cmd, invio_stdin=None, ignora_errore=False, shell=False):
        """
        Esegue un comando mostrando l'output riga per riga in tempo reale.
        Ritorna True se il comando e' terminato con successo (returncode 0).
        invio_stdin: testo da inviare sullo stdin del processo appena
        avviato (serve per rispondere automaticamente a un'eventuale
        richiesta di conferma interna del comando stesso, dato che la
        conferma vera e propria la fa gia' questa finestra prima di
        arrivare qui).
        """
        cmd_stampato = cmd if isinstance(cmd, str) else " ".join(cmd)
        self._log(f"\n$ {cmd_stampato}\n", "comando")
        # PYTHONIOENCODING forza UTF-8 nell'output di QUALSIASI script Python
        # lanciato da qui, anche quelli che non se lo impostano da soli:
        # senza, Windows userebbe una codifica limitata (cp1252) non appena
        # l'output viene catturato (come facciamo qui) invece che mostrato
        # in un terminale interattivo, causando crash su simboli speciali.
        ambiente = os.environ.copy()
        ambiente["PYTHONIOENCODING"] = "utf-8"
        try:
            processo = subprocess.Popen(
                cmd, cwd=CARTELLA_PROGETTO, shell=shell, env=ambiente,
                stdin=subprocess.PIPE if invio_stdin else None,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if invio_stdin:
                processo.stdin.write(invio_stdin)
                processo.stdin.flush()
                processo.stdin.close()
            for riga in processo.stdout:
                self._log(riga)
            processo.wait()
        except FileNotFoundError as e:
            self._log(f"\n[ERRORE] Comando non trovato: {e}\n", "errore")
            return False
        except Exception as e:
            self._log(f"\n[ERRORE] {e}\n", "errore")
            return False

        if processo.returncode == 0:
            self._log(f"[OK] Terminato correttamente.\n", "ok")
            return True
        else:
            self._log(f"[ERRORE] Codice di uscita: {processo.returncode}\n", "errore")
            return ignora_errore

    # ══════════════════════════════════════════════════════════════
    # 1) PULIZIA CARTELLA
    # ══════════════════════════════════════════════════════════════
    def pulisci(self):
        if self.in_esecuzione:
            return
        anteprima = messagebox.askyesnocancel(
            "Pulisci cartella progetto",
            "Vuoi vedere prima un'ANTEPRIMA di cosa verrebbe eliminato "
            "(consigliato), senza cancellare nulla?\n\n"
            "Sì = mostra anteprima\n"
            "No = elimina subito (chiederà comunque conferma finale)\n"
            "Annulla = non fare nulla",
        )
        if anteprima is None:
            return
        self._blocca_pulsanti(True)
        threading.Thread(
            target=self._pulisci_worker, args=(anteprima,), daemon=True
        ).start()

    def _pulisci_worker(self, solo_anteprima):
        self._intestazione_sessione("PULIZIA CARTELLA PROGETTO")
        self._imposta_stato("Pulizia in corso...")
        if solo_anteprima:
            self._esegui_comando([sys.executable, "pulizia.py"])
            self._log(
                "\nQuesta era solo un'anteprima: nessun file è stato "
                "eliminato. Premi di nuovo il pulsante e scegli \"No\" per "
                "eliminare davvero.\n", "info",
            )
        else:
            conferma = messagebox.askyesno(
                "Conferma eliminazione",
                "Confermi l'eliminazione dei file obsoleti elencati?\n"
                "L'operazione non è annullabile.",
            )
            if conferma:
                # Il comando chiede una sua conferma interna (s/N):
                # gliela diamo qui, dato che l'utente ha già confermato sopra.
                self._esegui_comando([sys.executable, "pulizia.py", "--esegui"], invio_stdin="s\n")
            else:
                self._log("Operazione annullata.\n", "info")
        self._imposta_stato("Pronto.")
        self._blocca_pulsanti(False)

    # ══════════════════════════════════════════════════════════════
    # 2) CREA APP WINDOWS (stessa sequenza di build_ctm.bat)
    # ══════════════════════════════════════════════════════════════
    def crea_app_windows(self):
        if self.in_esecuzione:
            return
        if not messagebox.askyesno(
            "Crea app Windows",
            "Verrà eseguita la build completa:\n\n"
            "1. Pulizia cartelle precedenti\n"
            "2. Offuscamento sorgenti (PyArmor)\n"
            "3. Compilazione exe (PyInstaller)\n"
            "4. Calcolo hash SHA256\n"
            "5. Creazione installer (Inno Setup)\n\n"
            "Può richiedere diversi minuti, soprattutto la prima volta. "
            "Continuare?",
        ):
            return
        self._blocca_pulsanti(True)
        threading.Thread(target=self._build_worker, daemon=True).start()

    def _build_worker(self):
        self._intestazione_sessione("CREAZIONE APP WINDOWS")

        self._imposta_stato("Verifica Python...")
        self._log(f"Python usato: {sys.executable}\n", "info")
        self._esegui_comando([sys.executable, "--version"])

        self._imposta_stato("Chiusura istanze precedenti...")
        self._log("\n[1/6] Chiusura istanze CTMBrowser.exe eventualmente aperte...\n", "comando")
        subprocess.run(
            ["taskkill", "/F", "/IM", "CTMBrowser.exe"],
            cwd=CARTELLA_PROGETTO, capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

        self._imposta_stato("Pulizia cartelle precedenti...")
        self._log("\n[2/6] Pulizia cartelle precedenti (build, build_obf, dist)...\n", "comando")
        import shutil
        for cartella in ("build", "build_obf", "dist"):
            percorso = os.path.join(CARTELLA_PROGETTO, cartella)
            if os.path.isdir(percorso):
                try:
                    shutil.rmtree(percorso)
                    self._log(f"  rimossa: {cartella}\n")
                except Exception as e:
                    self._log(f"  impossibile rimuovere {cartella}: {e}\n", "errore")

        self._imposta_stato("Generazione timbro di build...")
        self._log("\n[3/6] Generazione identificativo di build...\n", "comando")
        self._esegui_comando(
            [sys.executable, "-c",
             "import subprocess, datetime, os; "
             "sha = subprocess.run(['git','rev-parse','--short','HEAD'],capture_output=True,text=True).stdout.strip() or 'nogit'; "
             "data = datetime.datetime.now().strftime('%Y-%m-%d %H:%M'); "
             "os.makedirs('static', exist_ok=True); "
             "open('static/build_info.txt','w').write(f'build locale - commit {sha} - {data} - windows')"],
            ignora_errore=True,
        )

        self._imposta_stato("Offuscamento con PyArmor (può richiedere qualche minuto)...")
        self._log("\n[4/6] Offuscamento sorgenti con PyArmor...\n", "comando")
        ok = self._esegui_comando(
            [sys.executable, "-m", "pyarmor.cli", "gen", "-O", "build_obf"] + FILE_DA_OFFUSCARE
        )
        if not ok:
            self._log("\nBuild interrotta: l'offuscamento PyArmor è fallito.\n", "errore")
            self._imposta_stato("Errore durante l'offuscamento.")
            self._blocca_pulsanti(False)
            return

        self._imposta_stato("Compilazione con PyInstaller (può richiedere diversi minuti)...")
        self._log("\n[5/6] Compilazione EXE con PyInstaller...\n", "comando")
        self._log("      (la fase di analisi può durare diversi minuti, è normale)\n", "info")
        ok = self._esegui_comando(
            [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "CTMBrowser_fixed.spec"]
        )
        if not ok or not os.path.exists(os.path.join(CARTELLA_PROGETTO, "dist", "CTMBrowser.exe")):
            self._log("\nBuild interrotta: PyInstaller non ha prodotto dist\\CTMBrowser.exe.\n", "errore")
            self._imposta_stato("Errore durante la compilazione.")
            self._blocca_pulsanti(False)
            return

        self._imposta_stato("Calcolo hash SHA256...")
        self._log("\n[6/6] Calcolo SHA256 di dist\\CTMBrowser.exe...\n", "comando")
        try:
            import hashlib
            path_exe = os.path.join(CARTELLA_PROGETTO, "dist", "CTMBrowser.exe")
            digest = hashlib.sha256(open(path_exe, "rb").read()).hexdigest()
            with open(os.path.join(CARTELLA_PROGETTO, "dist", "core_hash.txt"), "w") as f:
                f.write(digest)
            self._log(f"  {digest}\n", "ok")
        except Exception as e:
            self._log(f"  impossibile calcolare l'hash: {e}\n", "errore")

        self._log("\nCompilazione dell'installer con Inno Setup...\n", "comando")
        inno_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
        if os.path.exists(inno_path):
            self._esegui_comando([inno_path, "CTMWebSetup.iss"])
        else:
            self._log(
                f"  Inno Setup non trovato in {inno_path} — installer NON creato.\n"
                f"  L'exe in dist\\CTMBrowser.exe è comunque pronto.\n", "errore",
            )

        self._log("\n" + "="*70 + "\n", "ok")
        self._log(" BUILD COMPLETATA\n", "ok")
        self._log("="*70 + "\n", "ok")
        self._log(
            "\nPRIMA DI DISTRIBUIRE, VERIFICA MANUALMENTE:\n"
            "  1) Apri dist\\CTMBrowser.exe e prova le funzioni chiave\n"
            "  2) Controlla Sicurezza di Windows -> Cronologia protezione\n\n",
            "info",
        )
        self._imposta_stato("Build completata.")
        self._blocca_pulsanti(False)

    # ══════════════════════════════════════════════════════════════
    # 3) PUBBLICA SU GITHUB (stessa sequenza di push_reset.ps1)
    # ══════════════════════════════════════════════════════════════
    def pubblica_github(self):
        if self.in_esecuzione:
            return
        primo_ok = messagebox.askyesno(
            "ATTENZIONE — operazione distruttiva",
            "Questa operazione:\n\n"
            "1. Elimina la cronologia Git LOCALE (.git)\n"
            "2. Ricrea il repository da zero\n"
            "3. Aggiunge tutti i file presenti nella cartella\n"
            "4. FORZA il push su GitHub, sostituendo tutto\n\n"
            "La cronologia precedente su GitHub verrà PERSA e non è "
            "recuperabile da qui.\n\nContinuare davvero?",
            icon="warning",
        )
        if not primo_ok:
            return
        secondo_ok = messagebox.askyesno(
            "Ultima conferma", "Sei sicuro di voler procedere con il push forzato?"
        )
        if not secondo_ok:
            return

        messaggio = simpledialog.askstring(
            "Messaggio di commit",
            "Messaggio per questo aggiornamento:",
            initialvalue="CTM Browser update",
        )
        if messaggio is None:
            self._log("Operazione annullata.\n", "info")
            return
        if not messaggio.strip():
            messaggio = "CTM Browser update"

        self._blocca_pulsanti(True)
        threading.Thread(target=self._push_worker, args=(messaggio,), daemon=True).start()

    def _push_worker(self, messaggio_commit):
        self._intestazione_sessione("PUBBLICAZIONE SU GITHUB")
        self._log(f"Cartella:   {CARTELLA_PROGETTO}\n", "info")
        self._log(f"Repository: {REPO_URL}\n", "info")
        self._log(f"Branch:     {BRANCH}\n", "info")

        self._imposta_stato("Verifica Git...")
        if not self._esegui_comando(["git", "--version"]):
            self._log("\nGit non è installato o non è nel PATH. Operazione interrotta.\n", "errore")
            self._imposta_stato("Errore: Git non trovato.")
            self._blocca_pulsanti(False)
            return

        self._imposta_stato("Eliminazione repository locale...")
        self._log("\n[1/7] Eliminazione repository Git locale...\n", "comando")
        import shutil
        cartella_git = os.path.join(CARTELLA_PROGETTO, ".git")
        if os.path.isdir(cartella_git):
            try:
                shutil.rmtree(cartella_git)
                self._log("  .git eliminato.\n", "ok")
            except Exception as e:
                self._log(f"  impossibile eliminare .git: {e}\n", "errore")
                self._imposta_stato("Errore durante l'eliminazione di .git.")
                self._blocca_pulsanti(False)
                return
        else:
            self._log("  .git non presente, nulla da eliminare.\n")

        passi = [
            ("[2/7] Creazione nuovo repository...", ["git", "init"]),
            (None, ["git", "branch", "-M", BRANCH]),
            ("[3/7] Aggiunta di tutti i file...", ["git", "add", "."]),
            ("[4/7] Creazione commit...", ["git", "commit", "-m", messaggio_commit]),
            ("[5/7] Configurazione repository GitHub...", ["git", "remote", "add", "origin", REPO_URL]),
        ]
        self._imposta_stato("Preparazione repository...")
        for titolo, cmd in passi:
            if titolo:
                self._log(f"\n{titolo}\n", "comando")
            if not self._esegui_comando(cmd):
                self._log(f"\nOperazione interrotta al comando: {' '.join(cmd)}\n", "errore")
                self._imposta_stato("Errore durante la preparazione del repository.")
                self._blocca_pulsanti(False)
                return

        self._log("\n[6/7] Controllo repository...\n", "comando")
        self._esegui_comando(["git", "status"], ignora_errore=True)
        self._log("\nFile inclusi nel commit:\n", "info")
        self._esegui_comando(["git", "ls-files"], ignora_errore=True)

        self._imposta_stato("Invio a GitHub in corso...")
        self._log("\n[7/7] PUSH SU GITHUB (forzato)...\n", "comando")
        ok = self._esegui_comando(["git", "push", "-u", "origin", BRANCH, "--force"])

        self._log("\n" + "="*70 + "\n", "ok" if ok else "errore")
        if ok:
            self._log(" PUSH COMPLETATO CON SUCCESSO\n", "ok")
            self._log("="*70 + "\n", "ok")
            self._log(f"\nRepository aggiornata: {REPO_URL}\n", "ok")
        else:
            self._log(" PUSH FALLITO\n", "errore")
            self._log("="*70 + "\n", "errore")
            self._log(
                "\nControlla il messaggio d'errore sopra (causa comune: "
                "credenziali GitHub scadute o non configurate).\n", "errore",
            )
        self._imposta_stato("Pronto." if ok else "Errore durante il push.")
        self._blocca_pulsanti(False)


def main():
    root = tk.Tk()
    app = PannelloManutenzione(root)
    root.mainloop()


if __name__ == "__main__":
    main()
