---
種別: 要件定義書（Epic）
ID: "epic-00074"
タイトル: "Multi host agent and config asset expansion"
関連GitHub: ["#74"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-15"
親: ["init-local-00002"]
---

# epic-00074 Multi host agent and config asset expansion — 要件定義（WHAT / WHY）

## 目的（Initiative との紐づき）
- initiative goal / metric:
  - `init-local-00002` の feature expansion として、installer が配布できる agent-tooling を thin adapter baseline から一段広げ、Harness Engineering 向けの orchestrator と specialist agent/subagent 群を host-native asset として扱えるようにする。
  - `epic-00067` が確立した `install_root` 基盤を前提に、feature initiative 側では「何を追加配布できるか」という利用価値の拡張に集中する。
  - `Metric-001` の「feature value 中心の portfolio」に対して、Harness Engineering で継続利用しやすい host-managed setup を追加する。
- この epic が提供する能力:
  - Codex では main agent の project-scoped `config.toml` に orchestrator developer instructions を与え、main session 自体が orchestrator responsibility を担える。
  - GitHub Copilot では `orchestrator` custom agent を primary entrypoint として配布できる。
  - SpecDock 操作用 specialist agent は `spec-manager` へ改名され、primary user-facing agent ではなく sibling specialist として配布される。
  - Codex 用 config、specialist agents/subagents、shared skills を installer 管理下で配布できる。
  - GitHub Copilot 用 orchestrator および specialist agents/subagents を installer 管理下で配布できる。
  - 既存の `install_root` / managed sync-prune の仕組みを使い、将来 host や agent pack を追加できる拡張点を持つ。
- 位置づけ:
  - `epic-00048` は completed baseline として保持し、protocol / thin adapter / native shim の完了済み契約を再定義しない。
  - `epic-00067` は prerequisite architecture groundwork として扱い、source-of-truth ownership や installed layout cleanup 自体は本 epic で再所有しない。

## 問題定義
- `spec-dock` という製品名と、SpecDock を操作する specialist agent の名前が同じだと、tool 自体と specialist の区別がつきにくく、Harness-oriented multi-agent 運用で混乱しやすい。
- 現状は `install_root` 配下に shared skill や host-native shim を追加できる基盤はあるが、Harness として使う orchestrator と specialist agent/subagent 群を、host ごとの実際の制約に沿った project asset layout へ配布する契約が未固定である。
- そのため Codex / Copilot の初期セットアップは部分的にしか自動化できず、Harness Engineering のように複数 host / 複数 specialist を使う運用では install 後の手作業が残る。
- `epic-00048` で整えた thin adapter / native shim baseline をそのまま活かしつつ、Codex では main-agent config、GitHub Copilot では direct custom agent、という host 差分を踏まえた上で orchestrator、specialist agent、shared skill、必要最小限の host config を同じ installer contract で管理できないと、host ごとに追加方法や prune safety がばらつく。
- 一方で `epic-00067` で閉じた authority / layout / cleanup ルールをここで触り直すと、feature expansion ではなく architecture maintenance に逆流する。
- 必要なのは、新しい architecture cleanup ではなく、既存 `install_root` 機構の上に「orchestrator と specialist 群を host-pack 単位で増やせる」feature contract を載せることである。

## ユースケース
- happy path:
  - maintainer が `spec-dock init` / `spec-dock update` を実行すると、Codex では main-agent 用 `config.toml` bootstrap asset と specialist agent 群が、GitHub Copilot では `orchestrator` と specialist agent 群が host ごとの正しい project path に配置される。
  - Codex では project-scoped `config.toml` に orchestrator developer instructions が初回 bootstrap asset として配置され、その後の user edit は update で強制上書きされない。
  - shared skills は Codex 側 source から `.agents/skills/` に集約配置され、host 固有ディレクトリに重複配置しない。
  - maintainer は provider-side `install_root` に asset を追加し、consumer repo では host ごとの正しい target path へ install/update で反映できる。
  - 将来の新しい host や agent pack は、既存 host を壊さずに managed asset entry を追加するだけで拡張できる。
- exception / operation scenario:
  - 既存 repo に user-authored な host config や custom agent file がある場合、managed/unmanaged 境界に従って overwrite / prune の対象を誤らない必要がある。
  - Codex `config.toml` は bootstrap 後に user が編集しうるため、managed asset ではなく user-owned override として尊重する必要がある。
  - 旧 managed asset 名や旧 pack 構成から更新する場合でも、obsolete managed path だけが prune され、未知の custom file は保持される必要がある。
  - GitHub Copilot では `config` / `mcp-config` のような unsupported install target を project asset として前提にしない必要がある。
  - Host ごとの native config 仕様差分があっても、runtime protocol を shim 側へ再実装せず、`epic-00048` の thin delegation boundary を維持する必要がある。

## Epic requirements
- E-RQ-001:
  - SpecDock は host capability に応じて Harness-oriented orchestrator entrypoint を配布できること。
  - Codex では direct custom agent を primary entrypoint にできない制約を前提に、main agent の project-scoped `config.toml` developer instructions に orchestrator responsibility を与えること。
  - GitHub Copilot では `orchestrator` custom agent を primary entrypoint として配布できること。
  - SpecDock 操作用 specialist agent は `spec-manager` を canonical name とし、canonical filename を Codex では `.codex/agents/spec-manager.toml`、GitHub Copilot では `.github/agents/spec-manager.agent.md` に固定したうえで、primary entrypoint ではなく sibling specialist へ位置づけを変更し、installer contract と docs でその役割差を説明できること。
- E-RQ-002:
  - SpecDock は Codex 用 specialist agents/subagents を managed asset として配布・更新できること。
  - `epic-00048` の thin adapter / native shim baseline を壊さず、main-agent config bootstrap と sibling specialist から成る Codex host pack を追加できること。
  - Codex host pack は direct `.codex/agents/orchestrator.toml` を含めず、orchestrator responsibility は main-agent `config.toml` のみが担うこと。
- E-RQ-003:
  - SpecDock は shared skills を `.agents/skills/` 配下へ配布できること。
  - shared skill source は Codex 側提供ファイルを正本とし、host 固有ディレクトリへ重複配置しないこと。
- E-RQ-004:
  - SpecDock は GitHub Copilot 用 subagents/custom agents を managed asset として配布・更新できること。
  - GitHub Copilot host pack は `.github/agents/` 配下の agent assets を中心に構成し、`config` / `mcp-config` ファイルを install target として要求しないこと。
- E-RQ-005:
  - Codex `config.toml` は project-scoped bootstrap/template asset として初回 setup 時に配置できること。
  - 以後の update では user edit を尊重し、force-managed overwrite 対象にしないこと。
- E-RQ-007:
  - managed asset model は Codex / Copilot 個別実装に閉じず、将来 host や agent pack を追加できる拡張点を existing `install_root` mechanism 上に持つこと。
  - future host support は「新しい managed host pack を追加可能であること」を要求し、本 epic で全 future host を実装することは要求しない。
- E-RQ-008:
  - `epic-00067` の source-of-truth ownership、installed layout、cleanup safety を再定義しないこと。
  - `epic-00048` の completed baseline scope を reopen せず、protocol / native shim の完了済み責務分離を前提条件として扱うこと。
- E-RQ-009:
  - sync/prune は current managed file set と explicit obsolete managed file set のみに作用し、user-authored config / custom agent file を巻き込まないこと。
  - backward compatibility は要求しないが、update path では pre-epic state からの additive rollout と obsolete managed path cleanup の両方を検証できること。
- E-RQ-010:
  - provider docs、dogfooding workspace、installer behavior、tests の contract が一致し、maintainer がどの asset が managed で、どの asset が host-specific / user-authored なのか判断できること。
  - rollout と validation の checkpoint が epic plan に固定され、final close-out で cross-host parity を確認できること。

## Epic acceptance criteria
- E-AC-001:
  - Given:
    - clean target repo に `spec-dock init` または `spec-dock update` を実行する
  - When:
    - Codex host pack の managed assets を同期する
  - Then:
    - Codex では main agent の `config.toml` developer instructions が orchestrator responsibility を与える bootstrap asset として配置される
    - `spec-manager` を含む Codex specialist agents/subagents と shared skills が sibling asset として正しい project path に生成・更新される
    - Codex host pack は direct `.codex/agents/orchestrator.toml` を生成しない
    - Codex `config.toml` は初回 setup 時に bootstrap asset として配置され、既存 user edit がある場合は強制上書きされない
    - `epic-00048` の thin adapter / native shim baseline と矛盾せず、runtime protocol を新たに再実装しない
    - unknown custom Codex file は prune されない
  - 観測点:
    - installer integration tests
    - managed/unmanaged boundary assertions
    - docs parity
- E-AC-002:
  - Given:
    - clean target repo または既存 repo に `spec-dock update` を実行する
  - When:
    - GitHub Copilot host pack の managed assets を同期する
  - Then:
    - GitHub Copilot では `orchestrator` custom agent が primary entrypoint として生成され、`spec-manager` specialist は sibling agent として共存する
    - Copilot subagents/custom agents が `.github/agents/` 配下へ生成・更新される
    - GitHub Copilot `config` / `mcp-config` を install target として要求しない
    - obsolete managed Copilot path は prune できる
    - unknown custom Copilot file は保持される
  - 観測点:
    - installer integration tests
    - sync/prune evidence
    - docs parity
- E-AC-003:
  - Given:
    - requirement / design / plan と managed asset metadata を確認する
  - When:
    - future host または future agent pack の追加方法をレビューする
  - Then:
    - existing `install_root` mechanism のまま、新しい host root または pack entry を追加できる拡張点が説明されている
    - Codex / Copilot 実装が future host 全実装を前提にしていない
    - source-of-truth ownership を再定義していない
  - 観測点:
    - design review
    - managed asset metadata review
    - epic final spec review
- E-AC-004:
  - Given:
    - provider-side assets、dogfooding workspace、tests、plan の checkpoint を確認する
  - When:
    - epic close-out evidence をレビューする
  - Then:
    - `epic-00067` prerequisite と `epic-00048` baseline を前提にした additive rollout になっている
    - orchestrator、specialist agent、shared skill、bootstrap config の契約が host 間で整合している
    - validation / rollout checkpoint が完了条件として明示されている
  - 観測点:
    - final spec review
    - rollout checklist
    - dogfooding validation record

## スコープ
- MUST:
  - host capability に応じた orchestrator entrypoint 配布
  - Codex main-agent config bootstrap と specialist agents/subagents の managed deployment
  - GitHub Copilot subagents/custom agents の managed deployment
  - shared skills の `.agents/skills/` への集約配布
  - Codex `config.toml` の bootstrap/template 配布
  - existing `install_root` mechanism を使った extensible managed asset model
  - sync/prune safety、docs parity、dogfooding validation
- MUST NOT:
  - future host を全部この epic で実装する
  - GitHub Copilot `config` / `mcp-config` を install target に含める
  - core runtime protocol semantics を再設計する
  - completed `epic-00048` を reopen する
  - completed `epic-00067` の architecture cleanup を再所有する
- OUT OF SCOPE:
  - Claude Code など追加 host の即時実装
  - implementation-start prompt / workflow shortcut の project-scoped asset 配布
  - active/index/deps/context-pack の意味論変更
  - installer layout policy の全面見直し
  - host-native runtime logic の肥大化

## 境界
- Always:
  - `install_root` を唯一の provider-side authority として扱う
  - `epic-00048` の thin delegation boundary を維持する
  - managed/unmanaged 判定と prune safety を docs / tests / metadata で一致させる
  - Codex では main agent config が orchestrator responsibility を担い、GitHub Copilot では `orchestrator` custom agent を primary entrypoint として扱う
  - SpecDock 操作用 specialist は host を問わず `spec-manager` として扱う
  - shared skills は `.agents/skills/` に集約し、Codex 側 source を正本にする
  - future host 拡張は additive pack 追加として扱う
- Ask:
  - host-specific config file が managed default なのか bootstrap-only なのか user-owned override なのか曖昧なときは ownership を先に確定する
  - obsolete managed path の判定に人手 migration が必要かどうか
- Never:
  - source-of-truth ownership を feature epic 側で再定義する
  - shim / config 側へ runtime protocol 読み順や state 再実装を埋め込む
  - user-authored custom agent file を managed cleanup の convenience で削除する

## 非機能要件
- performance:
  - host pack 追加によって `spec-dock init/update/validate` の通常運用を不必要に遅くしない
- reliability / consistency:
  - same source tree から same managed host pack layout が再現できること
  - update 時の sync/prune が idempotent であること
- security:
  - host config / custom agent の overwrite と prune は managed ownership に限定すること
  - bootstrap-only config には user-specific / secret-bearing information を含めないこと
- operations:
  - maintainer が「どの host pack が何を配布するか」「何が managed / bootstrap-only / user-owned か」を docs と asset tree から追跡できること
  - implementation-start prompt/workflow shortcut のような host-dependent convenience asset は current implementation scope ではなく future extensibility note として扱うこと

## 依存 / 影響範囲
- impacted components:
  - `src/spec_dock/assets/install_root/.agents/`
  - `src/spec_dock/assets/install_root/.codex/`
  - `src/spec_dock/assets/install_root/.github/`
  - `src/spec_dock/cli.py`
  - managed asset metadata / sync-prune logic
  - `tests/test_init_update.py`
  - `tests/test_cli.py`
  - `spec-dock/` dogfooding workspace
- external dependency:
  - Codex CLI project config / specialist agent discovery contract
  - GitHub Copilot custom agent discovery contract
- compatibility:
  - additive rollout を基本とするが、backward compatibility は本 epic の要求に含めない
  - 旧 `spec-dock` specialist 名称との compatibility は維持しない
  - Codex `config.toml` は初回 bootstrap 後の user edit を尊重する
  - `epic-00067` install-shaped layout contract を前提にする

## 未確定事項
- なし:
  - parent initiative、dependency positioning、scope exclusion は本 epic で固定する
