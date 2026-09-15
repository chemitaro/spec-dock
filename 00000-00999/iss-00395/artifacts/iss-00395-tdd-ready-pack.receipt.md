---
kind: "tdd-ready-pack-receipt"
issue: "iss-00395"
generated_at: "2026-09-15"
repository: "chemitaro/spec-dock"
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
archive: "iss-00395-tdd-ready-pack.zip"
manifest: "iss-00395-tdd-ready-manifest.md"
manifest_sha256: "fa82c10367f24fbbd73cc8ed9010ad1deae7c968439b941d497b549a94615314"
archive_sha256: "ed89283e96d8b3cfbdef8e1882e4f73b3d5b9b9e9cb72a31738e40a0bfb78ff9"
---

# Issue #395 TDD readiness pack receipt

このreceiptは、Manifest自身とZIPの最終SHA-256を、自己参照を避けるためZIP外へ記録します。receipt自身はZIPへ含めません。

## Final hashes

- Manifest: `iss-00395-tdd-ready-manifest.md`
- Manifest SHA-256: `fa82c10367f24fbbd73cc8ed9010ad1deae7c968439b941d497b549a94615314`
- ZIP: `iss-00395-tdd-ready-pack.zip`
- ZIP SHA-256: `ed89283e96d8b3cfbdef8e1882e4f73b3d5b9b9e9cb72a31738e40a0bfb78ff9`

## ZIP validation

- Exact six Markdown members
- Member order verified
- Member bytes equal source bytes
- ZIP integrity verified
- No Product source、test source、ledger、timing、policy、workflow、credential、raw logを収録

This is an advisory replacement candidate. Canonical adoption、independent specification review、implementation authorization、Product mutation、PR、mergeは別ゲートです。
