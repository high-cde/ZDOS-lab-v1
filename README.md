# ZDOS LAB

## Il forge operativo di ZDOS e Zlang

ZDOS Lab è il contenitore tecnico dell’ecosistema ZDOS: riunisce sorgenti, specifiche, runtime, kernel, distro, Evidence Chain, policy, portale SEC, test, profili hardware e artefatti di build in un unico spazio operativo. Non sostituisce i repository ufficiali: li coordina, li identifica e li sincronizza senza perdere la provenienza.

> **One lab. Two official sources. Zero ambiguous mirrors.**

ZDOS Lab prende dal modello GitHub la leggibilità del codice e dal modello GitLab la pipeline, gli artifact e gli ambienti. L’identità rimane però ZDOS: ogni oggetto ha owner, commit sorgente, livello di verifica e regola di pubblicazione.

## Layout

| Area | Contenuto | Stato |
|---|---|---|
| `catalog/` | registro dei componenti, repository e profili | VERIFIED |
| `contracts/` | contratti ZLB2, policy, manifest e sync | VERIFIED |
| `orchestration/` | script per inspect, manifest, sync e gate | PREPARED |
| `workspaces/` | punto di montaggio per cloni locali o mirror controllati | PREPARED |
| `artifacts/` | output di build, checksum e prove | NOT VERIFIED finché non attestati |
| `ci/` | pipeline e gate riproducibili | PREPARED |

## Componenti ufficiali

Il catalogo parte dai repository ufficiali già esistenti:

- `high-cde/ZDOS` — kernel, distro, build unificata, Evidence Chain e strumenti.
- `high-cde/Zlang` — compilatore, runtime, VM, specifica e ZLB2.
- `high-cde/ZDOS-SEC-PORTAL` — workspace operativo e interfaccia SEC.

Il Lab non copia silenziosamente i repository e non promuove un mirror a fonte primaria. Il file `catalog/lab-manifest.json` conserva URL, commit, ruolo e livello di verifica di ogni componente.

## Comandi

```sh
./orchestration/zdos-labctl inspect
./orchestration/zdos-labctl manifest
./orchestration/zdos-labctl sync --check
./orchestration/zdos-labctl sync --apply
./orchestration/zdos-labctl gate
```

`sync --check` è sempre non distruttivo. `sync --apply` aggiorna soltanto cloni con working tree pulito e fast-forward possibile; rifiuta reset, force-push, cancellazione di branch e sovrascrittura di modifiche locali. La pubblicazione verso GitHub o GitLab richiede un remote configurato e un’autenticazione già disponibile; senza questi requisiti il Lab produce un report diagnostico, non inventa una sincronizzazione riuscita.

## Stati

`VERIFIED` significa codice e prova osservabile. `PREPARED` significa contratto e percorso predisposti ma non completamente provati. `EXPERIMENTAL` identifica un laboratorio attivo. `NOT_VERIFIED` è il valore obbligatorio quando manca una prova. La presenza di un componente nel catalogo non ne aumenta lo stato.

## Direzione del forge

Il workspace web ZDOS Lab espone repository, file, commit, activity, CI, release, evidence e hardware matrix. Il cuore operativo resta locale e versionabile: il web layer visualizza i contratti del Lab e non sostituisce il controllo Git o le prove QEMU.

## Licenza e identità

I repository mantengono le proprie licenze. I commit del Lab usano l’identità richiesta: `High-cde <Highkali13@proton.me>`.
