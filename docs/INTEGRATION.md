# ZDOS Integrated Runtime

Questa guida descrive il percorso verificabile tra le fonti ufficiali dell’ecosistema.

## Workspace

I repository devono essere cloni affiancati:

```text
workspace/
├── ZDOS/
├── Zlang/
├── zdos-organism/
├── ZDOS-SEC-PORTAL/
├── Z-CYBERCORE/
└── ZDOS-lab-v1/
```

## Gate locale

Dalla directory `ZDOS-lab-v1`:

```sh
export ZDOS_LAB_WORKSPACE="$PWD/.."
./orchestration/zdos-labctl inspect
./orchestration/zdos-labctl manifest
./orchestration/zdos-labctl gate
python3 orchestration/zdos-lab-pack.py --component unified --output-dir artifacts/portable
```

Il gate controlla entrypoint realmente presenti in ZDOS, il Makefile x86_64, la policy Evidence Chain e gli script shell. Non dichiara automaticamente che QEMU o hardware fisico siano stati verificati.

## Verifica dei componenti

```sh
(cd ../Zlang && python3 -m unittest discover -s tests -p 'test_*.py' -v)
(cd ../Zlang && cargo test --all-targets)
(cd ../zdos-organism && cargo test --workspace --all-targets --all-features)
(cd ../Z-CYBERCORE && cargo test --all-targets)
(cd ../ZDOS-SEC-PORTAL && npm ci --ignore-scripts && npm test)
```

Il percorso Zlang/ZDOS x86_64 richiede inoltre `gcc`, `binutils`, `make`, `grub-mkrescue`, `xorriso` e `qemu-system-x86_64`. Se uno di questi strumenti manca, lo stato corretto è `NOT_VERIFIED`, non `VERIFIED`.

## Portale SEC

Avviare il portale solo in una rete amministrativa o locale:

```sh
export ZDOS_SEC_DATA_DIR="$PWD/var/sec-data"
export ZDOS_COMPILE_TOKEN="scegli-un-segreto-lungo"
export ZDOS_ROOT="$PWD/../ZDOS"
npm ci
npm start
```

Il portale espone `/api/health`, feed e ledger locali. L’endpoint di compilazione richiede `x-zdos-compile-token`, usa processi senza shell e applica un timeout. Non esporre il portale su Internet senza reverse proxy TLS, autenticazione di sessione, rate limiting, isolamento del worker e revisione della superficie filesystem.

## Stati di release

| Stato | Significato |
|---|---|
| `VERIFIED` | Gate automatico superato con commit sorgente e prova registrata |
| `REACHABLE` | Endpoint raggiungibile, senza prova di correttezza |
| `CONFIGURED` | Parametri presenti e leggibili |
| `EXPERIMENTAL` | Codice operativo ma non pronto alla promozione |
| `NOT_VERIFIED` | Prova assente o gate non eseguito |

Z-CYBERCORE resta una demo difensiva locale. Evidence Chain resta un ledger locale append-only, non una blockchain con consenso. Questi confini fanno parte del prodotto e devono restare visibili nelle release.
