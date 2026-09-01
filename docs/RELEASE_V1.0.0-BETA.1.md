# ZDOS Lab v1.0.0-beta.1

**Stato:** prerelease tecnico  
**Repository:** `high-cde/ZDOS-lab-v1`  
**Policy:** `default-deny`  
**Provenienza:** repository ufficiali catalogati nel manifest del Lab

## Cosa contiene

Questa prerelease raccoglie il primo pacchetto portabile del forge ZDOS Lab. Include catalogo, contratti di integrazione, orchestrazione, manifest di stato, checksum e bundle source-first dei componenti disponibili.

| Pacchetto | Formati | Contenuto | Stato |
|---|---|---|---|
| `zdos-lab-unified` | `.tar.gz`, `.zip` | Bundle aggregato dei componenti catalogati e dei contratti del Lab | `PREPARED` |
| `zdos-lab-zdos` | `.tar.gz`, `.zip` | Bundle del componente ZDOS | `PREPARED` |
| `zdos-lab-zlang` | `.tar.gz`, `.zip` | Bundle del componente Zlang | `PREPARED` |
| `zdos-lab-sec` | `.tar.gz`, `.zip` | Bundle del portale SEC sperimentale | `EXPERIMENTAL` |
| `SHA256SUMS-*` | testo | Checksum per verifica offline degli artefatti | `AVAILABLE` |

## Verifica

Prima dell’uso, verificare i checksum con:

```sh
sha256sum -c SHA256SUMS-unified
```

Il percorso di controllo del Lab è:

```sh
./orchestration/zdos-labctl inspect
./orchestration/zdos-labctl manifest
./orchestration/zdos-labctl gate
```

La pipeline CI `ZDOS Ecosystem Integration` è attiva e ha prodotto run riuscite sul repository. La release non promuove automaticamente tutti i componenti a produzione: il manifest conserva gli stati individuali e i limiti di verifica.

## Limiti dichiarati

Questa release **non è un ISO avviabile, non è un APK Android e non è una distribuzione production-ready**. I bundle sono source-first e non sostituiscono i repository ufficiali. Il componente `zdos-organism` rimane `NOT_VERIFIED` quando il checkout locale non è presente; `ZDOS-SEC-PORTAL` e `Z-CYBERCORE` restano sperimentali secondo il catalogo.

La release non abilita force-push, sincronizzazioni distruttive, esecuzione remota, accesso libero al filesystem o pubblicazione automatica. Per la futura app Android ZDOS Lab Console sarà necessario un artefatto APK prodotto da una pipeline Expo/Android separata e collegato a un commit identificabile.
