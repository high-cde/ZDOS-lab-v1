# ZDOS Ecosystem Integration Contract v1

**Stato:** proposta implementabile
**Scopo:** collegare Zlang, ZDOS, zdos-organism, ZDOS-SEC-PORTAL e ZDOS Lab senza promuovere mock o claim a evidenza runtime.

## Principio di verità operativa

Ogni componente espone uno stato osservabile. `VERIFIED` è ammesso solo quando un comando riproducibile produce una prova salvata con commit sorgente, timestamp, versione del contratto e checksum. `REACHABLE` indica soltanto che un endpoint risponde. `CONFIGURED` indica che i parametri sono presenti. `EXPERIMENTAL` identifica una capability non ancora coperta da un gate completo. `NOT_VERIFIED` è obbligatorio quando manca una prova.

## Pipeline canonica

```text
Zlang source
  → ZLB2 compiler contract
  → ZDOS x86_64 build
  → QEMU serial verification
  → evidence record
  → Lab manifest
  → SEC Portal telemetry
  → organism cycle / operational decision
```

Il portale visualizza prove già generate; non può dichiarare da solo che un build, boot, endpoint o ledger sia verificato.

## Artefatto di prova

Ogni gate produce un documento JSON con questa forma minima:

```json
{
  "schema": "zdos-evidence/v1",
  "component": "zlang|zdos|organism|sec-portal|lab",
  "status": "VERIFIED|REACHABLE|CONFIGURED|EXPERIMENTAL|NOT_VERIFIED",
  "source_commit": "40-character git sha",
  "contract": "zlb2-2.5|organism-runtime-0.1|sec-api-1",
  "created_at_utc": "RFC3339 timestamp",
  "checks": [],
  "sha256": "sha256 of canonical payload"
}
```

Un record senza `source_commit`, `contract` o `checks` non può essere pubblicato come `VERIFIED`.

## Contratto Zlang/ZDOS

Zlang deve generare bytecode ZLB2 v2.5. Il kernel ZDOS deve validare magic, versione, opcode, lunghezze e `HALT`. Il gate minimo è `python3 -m unittest discover -s tests -p 'test_*.py'`, seguito da build e boot QEMU quando le dipendenze sono disponibili. Variabili, file system, rete, processi e syscall restano non supportati finché non esistono capability, policy, quota, timeout e test negativi.

## Contratto zdos-organism

La CLI deve fornire `--eval` per l’esecuzione locale deterministica e `--once` per un battito osservabile. Il runtime deve usare `ZDOS_LLM_URL` e `ZDOS_STATE_DIR`; nessun endpoint remoto è considerato verificato senza health check, timeout, errore controllato e prova registrata.

## Contratto SEC Portal

Le API minime sono `GET /api/social/feed`, `GET /api/chain/ledger`, `POST /api/sync/submit` e un endpoint di health. Il ledger deve usare hash deterministici e verificabili, non casualità. La compilazione deve essere asincrona, autenticata, limitata, isolata in worker e confinata a una workspace temporanea; il portale non deve scrivere direttamente nel checkout di produzione.

## Contratto Lab

`zdos-labctl inspect` deve leggere i repository senza modificarli. `sync --check` non deve produrre mutazioni. `sync --apply` ammette soltanto working tree puliti e fast-forward. `gate` deve chiamare soltanto script presenti nel catalogo e deve fallire con una diagnosi azionabile quando una fonte manca. I bundle source-first non sono ISO e non devono essere dichiarati eseguibili nativi senza test sul target.

## Gate di release integrata

Una release aggregata è pubblicabile solo se:

1. Zlang compiler tests e contratto ZLB2 sono verdi.
2. ZDOS build/boot QEMU è verde oppure lo stato è esplicitamente `NOT_VERIFIED` e la release non viene promossa a production.
3. zdos-organism format, Clippy, test e smoke test sono verdi.
4. SEC Portal ha test HTTP, input validation, authentication test e ledger verification.
5. Lab `inspect`, `manifest` e `gate` sono verdi.
6. Nessun segreto, password hard-coded, artefatto `target/` o stato locale è nel diff.
7. Il changelog e le note di release riportano i limiti residui.

## Non-obiettivi v1

Questo contratto non trasforma automaticamente ZDOS in un sistema operativo general-purpose, Z-CYBERCORE in uno strumento offensivo reale o Evidence Chain in una blockchain con consenso. Questi componenti devono restare marcati secondo la prova effettivamente disponibile.
