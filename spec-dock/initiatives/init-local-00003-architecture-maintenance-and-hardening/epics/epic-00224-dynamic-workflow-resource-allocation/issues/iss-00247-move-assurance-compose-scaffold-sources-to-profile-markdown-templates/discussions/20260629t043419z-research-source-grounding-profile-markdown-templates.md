---
種別: research
ID: "20260629t043419z-research"
タイトル: "Source Grounding For Profile Markdown Templates"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
親: ["iss-00247"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260629t043419z-research Source Grounding For Profile Markdown Templates

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00247` の要件定義に入る前に、`assurance compose` の現行契約、親 Epic の要求、既存 research、コード、テストから、profile 別 Markdown template 化で守るべき範囲と不変条件を整理する。
- 特に、`profile-sections.json` に埋め込まれている `design.md` / `plan.md` / `report.md` の Markdown prose を、どこまで Markdown template files へ移すべきかを判断できる状態にする。

## sources / 調査方法 (必須)
- 参照先:
  - `spec-dock/active/initiative/requirement.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/discussions/20260629t022552z-research-profile-markdown-template-management.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifact_composer.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/templates/assurance/profile-sections.json`
  - `src/spec_dock/assets/spec_dock/templates/issue/design.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
  - `tests/unit/domain/test_artifact_composer.py`
  - `tests/unit/application/test_assurance.py`
  - `tests/cli_runtime/test_assurance.py`
  - `tests/cli_runtime/test_assurance_compose.py`
  - `tests/cli_runtime/test_new.py`
- 検証手順:
  - active issue / parent docs を読み、Issue がまだ placeholder 状態であることを確認した。
  - composer / store / application layer を読み、現行 compose の責務境界と fail-closed 条件を抽出した。
  - CLI / domain / application tests を読み、既存 regression contract を抽出した。
  - ChatGPT GPT-5.5 Pro Extended へ設計判断レビューを依頼した。結果は `20260629t043420z-disc-template-source-scope-decision-synthesis.md` 側で advisory evidence として統合した。
- 実験条件:
  - この research では runtime 挙動を変更していない。
  - `requirement.md` / `design.md` / `plan.md` はまだ canonical authoring していない。

## facts / 観測できた事実 (必須)
- `iss-00247` の canonical `requirement.md` は placeholder のままで、まだ要件具体化されていない。
- `design.md` と `plan.md` は `artifact_state: awaiting-assurance-compose` を持つ placeholder であり、この状態のまま本文を書き始めないよう明示している。
- 親 Epic の `E-RQ-006` は `design / plan / report` の必要 sections を policy fragment から合成し、substantive user content を自動上書きしないことを要求している。
- 親 Epic の `E-AC-006` は profile-specific planning として、異なる Profile fixture で必要 section だけが生成され、不要 Profile の workflow が含まれず、既存 substantive content が保持されることを要求している。
- 親 Epic design では `Artifact Composer` の責務を `design / plan / report fragment` の単調合成として定義している。
- 現行 `profile-sections.json` は `sections` に Markdown heading/body を JSON string として持ち、`profiles` が profile/artifact 別の section id list を持つ。
- 現行 composer は `authorized_profile` だけで section を選択し、`lite_candidate` は `ComposeArtifactResult` に保持されるが selection authority には使われない。
- `artifact_composer.py` は managed section marker を scan し、duplicated / mismatched / malformed / unclosed marker を fail-closed にする。
- `design.md` / `plan.md` は unedited placeholder の場合だけ `artifact_state: awaiting-assurance-compose` を取り除き、`状態: "draft"` を `状態: "approved"` に変換して materialize する。
- `design.md` / `plan.md` に substantive body がある場合、または placeholder marker と直接編集が混在する場合、compose は `substantive_content_conflict` として上書きを拒否する。
- `report.md` は placeholder 判定の対象外で、現行実装では append-oriented managed section 合成の対象になっている。
- `application/assurance.py` は compose 前に `.assurance.json` を verify し、missing / invalid / stale source binding の場合は artifact read/write 前に invalid result を返す。
- real write では、変更対象 artifact と contract の writable preflight を先に行い、その後 artifact write、最後に planning source binding を更新した `.assurance.json` を書く。
- `ArtifactStore` は symlinked planning artifact、repo 外 path、issue dir 外 path を拒否する。
- `tests/cli_runtime/test_assurance_compose.py` は all compose、single artifact compose、dry-run、second run unchanged、missing/invalid/stale/symlink fail-closed、changed paths reporting を固定している。
- `tests/unit/domain/test_artifact_composer.py` は profile selection、Lite candidate 非 authority、idempotence、downgrade が強い section を削除しないこと、marker conflict を固定している。
- `tests/unit/application/test_assurance.py` は changed artifact を全て preflight してから write することを固定している。
- `tests/cli_runtime/test_new.py` は新規 Issue の `design.md` / `plan.md` が awaiting-compose placeholder として作成され、最初から managed section を含まないことを固定している。

## inference / 推測 (必須)
- 事実から推測したこと:
  - この Issue の主目的は、profile 別 `design.md` / `plan.md` scaffold prose の source-of-truth を JSON string から Markdown files へ移し、編集性、preview、review、dogfooding 適合性を上げること。
  - 変更の本質は artifact output の大幅変更ではなく、template source storage model の変更である。
  - `report.md` は execution evidence ledger で append-oriented の性格が強く、`design.md` / `plan.md` と同じ body-template materialization に含めると scope と migration risk が増える。
  - `profile-sections.json` を完全に削除するか、path index / metadata manifest として縮小するかは設計判断だが、少なくとも design/plan prose を JSON body に残すと Issue の目的に反する。
  - 現行 tests の多くは section id と marker を前提にしているため、Markdown template 化後も managed-section id または同等の idempotency mechanism を残す必要がある。
- 推測の根拠:
  - 既存 research の推奨は `Markdown-template-first hybrid` であり、full-file replacement は非推奨としている。
  - 現行 code/test は safety behavior に厚く投資しており、これを外すと regression surface が大きい。
  - 親 Epic は profile-specific planning output を要求しており、template source の表現形式までは固定していない。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - 実際の implementation diff。
  - `assurance compose` の live command 実行による現行 output の golden snapshot。
  - profile 別 Markdown template files の具体的な文面。
  - `report.md` を同時に移したいという明示的なユーザー意図があるかどうか。
- 確認できない理由:
  - この段階は requirement authoring 前の clarification であり、まだ実装・テスト変更を行っていない。
  - `report.md` の同時移行は product/workflow scope 判断だが、source-grounded facts と ChatGPT advisory は defer で一致しているため、現時点では blocking question にしない。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - なし。`report.md` をこの Issue で必ず同時移行したい場合だけ、scope を再確認する必要がある。
- pressure-test question として切り出すべき候補:
  - 現時点ではなし。
- 質問せずに解決できた候補:
  - `lite_candidate` は template selection authority にしない。既存 Epic design と tests が明示している。
  - full-file replacement は採用しない。既存 research と code/test safety contract が反対している。
  - provider-side `src/spec_dock/assets/spec_dock/...` が実装 source of truth であり、dogfooding `spec-dock/...` は validation target。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `profile sections` / `profile templates` / `policy fragment` / `artifact template`
  - `lite_candidate` / `lite_authorized` / `authorized_profile`
  - `materialize` / `compose` / `append managed section`
- 既存 docs / code / tests / discussions での使われ方:
  - 親 Epic は `policy fragment` と `design / plan / report fragment` の合成という言い方をしている。
  - 現行 code は `ProfileSectionManifest` と `ManagedSection` として JSON section body を扱う。
  - 既存 research は `Markdown-template-first hybrid` と呼び、profile/artifact 別 Markdown body template を提案している。
  - `lite_candidate` は shadow measurement、`authorized_profile` は実行 authority として親 Epic design / tests が固定している。
- 判断が必要な理由:
  - 要件定義では「template source を Markdown に移す」と書くと full-file replacement と誤読される可能性がある。
  - `profile-sections.json` を廃止するのか、prose-less manifest として残すのかで設計とテストが変わる。
  - `report.md` を同時対象にするかで受け入れ条件と regression scope が変わる。

## edge cases / 具体シナリオ (必須)
- edge case:
  - profile template file が missing / unreadable / invalid UTF-8。
  - profile template が wrong artifact 用の managed section id を含む。
  - profile template 内に duplicate / malformed managed marker がある。
  - `authorized_profile=standard` かつ `lite_candidate=true` の issue。
  - compose dry-run。
  - compose が複数 artifact を変更予定だが、後続 artifact または `.assurance.json` が writable でない。
  - materialized 後に再 compose する。
  - strict/critical から standard へ profile downgrade する。
  - placeholder ではない substantive `design.md` / `plan.md` が存在する。
  - provider-side template は更新済みだが dogfooding mirror が古い。
- その edge case が requirement / design / plan に与える影響:
  - missing/invalid template は write 前に fail-closed とする acceptance が必要。
  - template selection authority は `authorized_profile` と artifact kind だけに限定する acceptance が必要。
  - idempotence / no-overwrite / downgrade no-delete を明示する必要がある。
  - provider-side asset と installed/dogfooding mirror の検証を plan に含める必要がある。

## implications / 判断への含意 (必須)
- `requirement.md` には、「なぜ JSON string ではなく Markdown template source が必要か」を編集性・reviewability・dogfooding 適合性として書く。
- `requirement.md` の MUST は、design/plan template source、selection authority、safety behavior、tests、provider/dogfooding validation に分ける。
- `requirement.md` の MUST NOT は、full-file replacement、substantive content overwrite、Lite candidateによる obligation reduction、runtime network dependency、template prose の JSON body 残留を含める。
- `design.md` では、`ArtifactStore` が profile/artifact template を読む責務、`artifact_composer` が安全な materialization / marker validation を担う責務に分けるのが自然。
- `plan.md` では、domain unit tests、application preflight tests、CLI compose tests、init/update scaffold tests、dogfooding inspection を closure にする。
- `report.md` を同時移行しない場合、その判断は Issue-local design/scope decision として `report.md` Decision Ledger に採用証跡を残す必要がある。

## リスク/制約 (任意)
- Markdown file 化により profile 間の重複が増え、drift が起きる。
- Convention-only layout は単純だが、全 profile/artifact の存在検証や diagnostics が弱くなる可能性がある。
- Manifest を残す場合は二重 authority になりやすい。残すなら prose-less path index / validation metadata に限定する必要がある。
- `report.md` を同時に動かすと append-oriented evidence ledger の semantics まで変更する可能性がある。

## 反映先 (任意)
- reflected_to:
  - `20260629t043420z-disc-template-source-scope-decision-synthesis.md`
  - future `requirement.md`
  - future `report.md` Evidence Adoption Ledger / Spec Authoring Gate

## 参考（References） (任意)
- Existing issue research: `20260629t022552z-research-profile-markdown-template-management.md`
- ChatGPT advisory prompt: `/private/tmp/iss-00247-chatgpt-prompt.md`
- ChatGPT advisory session: `iss-247-template-scope`
