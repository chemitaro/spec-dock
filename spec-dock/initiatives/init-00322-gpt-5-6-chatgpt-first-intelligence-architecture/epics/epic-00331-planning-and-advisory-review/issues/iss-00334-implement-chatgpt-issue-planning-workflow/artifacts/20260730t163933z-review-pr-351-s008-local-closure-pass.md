# PR #351 S008 fresh local closure review

## Scope

- Candidate verified-FD publication on Darwin and unprivileged Linux
- apply output-directory FD lifecycle
- exact-old remote CAS and resume absent/unavailable classification
- application guard identity propagation
- public contract and Human-approved Oracle configuration boundary
- provider/dogfood projection parity and focused regression evidence

The reviewers were fresh, read-only, and limited to concrete P0/P1 defects.
They were instructed not to propose redesigns, improvements, P2/P3 work, style
changes, or scope expansion.

## Spec review

```json
{"findings":[],"review_scope_summary":"PR #351 S008 の現行未コミット差分について、Candidate の verified-FD publication、apply の output-directory FD lifecycle、exact-old remote CAS、公開 status/reason/schema と Oracle 設定境界、provider/dogfood parity、関連テストを canonical Issue 文書および修復台帳と照合した。focused unit/application は 92 passed, 1 skipped、apply integration は 68 passed、変更された provider/dogfood 5組は byte-identical であることを確認した。","review_status":"pass","review_status_reason":"指定範囲に、実装継続またはマージ準備を阻害する具体的な P0/P1 の欠陥、契約矛盾、検証欠落は確認されなかった。既知の non-blocking follow-up は今回の blocking review scope 外として扱った。","overall_confidence_score":0.97}
```

## Code review

```json
{"findings":[],"overall_correctness":"patch is correct","overall_explanation":"S008 の Linux descriptor-bound publication、resume 時の remote absent/unavailable 分類、guard identity テストを確認した。対象差分に具体的な P0/P1 の正確性・安全性・移植性上の欠陥は認められない。","review_status":"pass","review_status_reason":"指定された P0/P1 限定の最終コードレビューを実施し、workflow を阻害する問題は確認されなかった。","overall_confidence_score":0.97}
```

## QA review

```json
{"findings":[],"overall_correctness":"patch is correct","overall_explanation":"指定された競合・CAS・descriptor-bound publication・guard identity・証跡不変条件には、実装境界と実Git挙動を組み合わせた回帰テストがあります。対象テストは160件成功、Linux専用の実動作テスト1件のみ現在のmacOS環境で想定どおりskipされ、具体的なP0/P1テスト欠落は確認されませんでした。","review_status":"pass","review_status_reason":"変更契約に対する重要な正常系・競合系・失敗系の回帰保護を信頼できる形で評価でき、マージを妨げるP0/P1のQA所見はありません。","overall_confidence_score":0.97}
```

## Main verification

- Candidate infra: `34 passed, 1 skipped`
- application apply: `36 passed`
- apply unit: `22 passed`
- apply integration with explicit full-regression permission: `68 passed`
- ordinary fast lane: `1161 passed, 2153 skipped`
- `make lint`: Ruff check, format check, and mypy PASS
- provider/dogfood runtime parity: five changed pairs byte-identical
- SpecDock validate: `nodes=227`
- `git diff --check`: PASS

## Gate result

- P0: 0
- P1: 0
- Result: `PASS`
- Linux real-syscall test is intentionally skipped on macOS and remains a
  required Provider CI assertion on the unprivileged Linux runner.
