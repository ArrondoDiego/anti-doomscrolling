# Guida all'uso su Mac (Apple Silicon M1+)

👉 **Repository GitHub:** [https://github.com/ArrondoDiego/anti-doomscrolling](https://github.com/ArrondoDiego/anti-doomscrolling)

Questa guida spiega passo dopo passo come scaricare e avviare **Doomscroll** su Mac con chip Apple Silicon (M1, M2, M3, M4 o superiori). Non richiede di installare Python né di compilare nulla.

---

## 📥 1. Scarica l'applicazione pronta
1. Vai alla pagina delle [GitHub Actions della repository](https://github.com/ArrondoDiego/anti-doomscrolling/actions).
2. Clicca sull'ultimo workflow completato con successo (🟢 spunta verde nella lista).
3. Nella sezione **Artifacts** in fondo alla pagina, scarica il file **`Doomscroll-macos-arm64`** (contiene lo ZIP).
4. Estrai l'archivio ZIP per ottenere l'applicazione **`Doomscroll.app`**.

## 📂 2. Spostala in Applicazioni
Trascina l'applicazione **`Doomscroll.app`** dentro la cartella **Applicazioni** del tuo Mac.

## 🔓 3. Primo avvio (Bypassare Gatekeeper)
Poiché l'app è compilata tramite GitHub Actions e non possiede una firma Apple a pagamento, macOS mostrerà un avviso di sicurezza la prima volta che provi ad aprirla.

Fai così **solo la prima volta**:
1. Fai **Click destro** (o tieni premuto `Control` e clicca) sull'icona di **`Doomscroll.app`**.
2. Seleziona **Apri** dal menu a tendina.
3. Nella finestra di avviso che compare, clicca su **Apri**.

*(Alternativa da Terminale)*:
```bash
xattr -cr /Applications/Doomscroll.app
```

## 📷 4. Permesso Fotocamera
Quando avvii l'app per la prima volta, macOS ti chiederà l'autorizzazione ad accedere alla **Fotocamera**:
* Clicca su **Consenti** (fondamentale affinché l'app possa monitorare la tua attenzione e la presenza dello smartphone).

Fatto! Ora Doomscroll è pronto a funzionare sul tuo Mac.
