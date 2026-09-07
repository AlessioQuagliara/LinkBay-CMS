---
description: A description of your rule
---

Regole per analisi della codebase

- Usa soltanto file e percorsi realmente presenti nel workspace.
- Prima di analizzare o proporre modifiche, esplora la root del repository.
- Non presumere linguaggi, framework, file di ingresso o convenzioni di directory.
- Non tentare `src/main.ts`, `src/main.py`, `app/*` o altri percorsi standard
  se non sono stati prima rilevati nell'inventario del repository.
- Per ogni conclusione, indica i file che la supportano.
- Se i file disponibili non sono sufficienti, dichiaralo invece di inventare.
- Per task medio-grandi: prima mostra piano e file da ispezionare; poi attendi
  conferma, a meno che l'utente chieda esplicitamente l'analisi completa.
- Privilegia interventi minimi, non aggiungere dipendenze e non modificare
  file non coinvolti senza una ragione esplicita.