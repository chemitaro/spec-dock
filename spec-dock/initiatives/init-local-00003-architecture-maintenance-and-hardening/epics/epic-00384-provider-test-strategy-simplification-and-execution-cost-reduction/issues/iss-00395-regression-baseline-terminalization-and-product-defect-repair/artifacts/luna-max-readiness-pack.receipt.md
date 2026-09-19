---
kind: "readiness-pack-receipt"
issue: "iss-00395"
generated_at: "2026-09-15"
repository: "chemitaro/spec-dock"
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
zip: "luna-max-readiness-pack.zip"
manifest: "luna-max-readiness-manifest.md"
manifest_sha256: "240e893f2c1d917d1033d1d2b59fdff4764b00c81bacb5ec415fbb8b85caa47f"
zip_sha256: "ad77d40a59808a5391b41bb49fd1f816e7f6d461b9040d339c8d32c885e05498"
---

# Issue #395 LunaMax readiness pack receipt

このreceiptは、配布ZIPの最終バイトを固定した後に、自己参照を避けるためManifest外へ記録するSHA-256を示す。receipt自身はZIPへ含めない。

## ZIP

- `luna-max-readiness-pack.zip`
- SHA-256: `ad77d40a59808a5391b41bb49fd1f816e7f6d461b9040d339c8d32c885e05498`
- member count: 5
- member order and bytes: verified
- ZIP integrity: verified

## Manifest

- `luna-max-readiness-manifest.md`
- SHA-256: `240e893f2c1d917d1033d1d2b59fdff4764b00c81bacb5ec415fbb8b85caa47f`
- YAML front matter: verified
- Four source-document hashes: recorded and matched

## ZIP members

1. `artifacts/luna-max-readiness-analysis.md`
2. `artifacts/design-luna-max-ready.md`
3. `artifacts/plan-lunamax-ready.md`
4. `artifacts/luna-max-implementation-handoff-ready.md`
5. `artifacts/luna-max-readiness-manifest.md`

Product source、test、ledger、timing、policy、workflow、commit、push、PR、merge、Issue closureはこのpackaging操作では変更していない。
