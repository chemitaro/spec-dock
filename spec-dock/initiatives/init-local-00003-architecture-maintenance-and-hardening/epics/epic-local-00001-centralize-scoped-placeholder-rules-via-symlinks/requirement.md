---
種別: 要件定義書（Epic）
ID: "epic-local-00001"
タイトル: "Centralize scoped placeholder rules via symlinks"
関連GitHub: [""]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-26"
親: ["init-local-00003"]
---

# epic-local-00001 Centralize scoped placeholder rules via symlinks — 要件定義（WHAT / WHY）

## 目的（Initiative との紐づき）
- initiative goal / metric:
  - `init-local-00003` の architecture hardening として、scaffold 配下の空ディレクトリ維持と placeholder 管理を壊れにくい contract に置き換える。
  - `Metric-002` の「architecture cleanup 対象を明確な issue として切り出す」に対応し、wrapper script 依存の脆い生成構造を閉じる。
- この epic が提供する能力:
  - initiative / epic / issue の scope 配下にある managed child directories が、実体ファイルのコピーではなく `docs/rules/` 配下の中央管理 rule sheet への symlink で保持される。
  - `new epic` / `new issue` は directory-local wrapper に依存せず runtime command を正本にしたまま運用できる。

## ユースケース
- happy path:
  - maintainer が新しい initiative / epic / issue を作成すると、`epics/` `issues/` `discussions/` が空にならず、各 directory には `rules.md` symlink だけが配置される。
  - 利用者は wrapper を探さず、`./spec-dock/scripts/spec-dock new epic ...` / `new issue ...` / `new doc ...` を直接使う。
- exception / operation scenario:
  - `spec-dock init/update` 後に `docs/rules/` の原本が配布され、新しく作られる node だけがその原本へ向く symlink を持つ。
  - validate / doctor / new doc の既存挙動は、`rules.md` symlink が存在しても誤作動しない。

## Epic requirements
- E-RQ-001:
  - scope child directories の placeholder は、directory-local 実体ファイルや wrapper script ではなく、`spec-dock/docs/rules/` 側の中央管理ファイルを正本とする symlink で提供されること。
- E-RQ-002:
  - `initiative/epics/`, `epic/issues/`, `initiative|epic|issue/discussions/` の各 managed directory で、空ディレクトリ保持のための `rules.md` が一貫して存在すること。
- E-RQ-003:
  - provider assets、installer `init/update`、runtime node creation、docs、tests がすべて新規生成向け symlink contract を前提に整合すること。

## Epic acceptance criteria
- E-AC-001:
  - Given:
    - 新しい repo に `spec-dock init` または既存 repo に `spec-dock update` を実行する。
  - When:
    - managed assets と runtime scaffold が配置される。
  - Then:
    - `docs/rules/` に中央管理の rules sheet 実体が配置され、新規生成フローがそれを参照できる。
  - 観測点:
    - `docs/rules/` のファイル配置、関連 docs、後続 create flow の前提。
- E-AC-002:
  - Given:
    - runtime で initiative / epic / issue を新規作成する。
  - When:
    - child directories を inspect する。
  - Then:
    - `epics/`, `issues/`, `discussions/` に wrapper script はなく、必要な `rules.md` symlink だけがある。
  - 観測点:
    - CLI/runtime tests、新規生成 node 実体。
- E-AC-003:
  - Given:
    - 既存の `new doc` / validate / sync 系コマンドを実行する。
  - When:
    - symlink 化後の scope directory を対象にする。
  - Then:
    - discussion 採番・検証・active pointer など既存フローが退行しない。
  - 観測点:
    - 関連 regression tests。

## スコープ
- MUST:
  - `new-epic` / `new-issue` wrapper を scaffold から外す。
  - `epics/`, `issues/`, `discussions/` の `rules.md` を `docs/rules/` の中央管理ファイルへの symlink に統一する。
  - provider-side assets の正本を `docs/rules/` として修正する。
  - 新規 node 作成時に `rules.md` symlink を明示配置する設計にする。
- MUST NOT:
  - `discussions/` 以外に別名 placeholder を増やさない。
  - 実体ファイルのコピーで見かけ上だけ同じ状態を作らない。
  - active manifest や GitHub workflow など無関係な architecture cleanup を混ぜない。
- OUT OF SCOPE:
  - `rules.md` の全面的な文面刷新
  - `new doc` 以外の command UX 再設計
  - 既存 checked-in scope tree の wrapper / 実体 rules の移行
  - symlink 非対応環境への fallback

## 境界
- Always:
  - canonical な user-facing rules source-of-truth は `spec-dock/docs/rules/**` とし、provider-side `src/spec_dock/assets/spec_dock/docs/rules/**` は package に同梱する authoring/source files として扱う。
  - node 配下の placeholder は symlink としてのみ materialize する。
  - user-facing create flow は runtime command を supported execution path とする。
- Ask:
  - `docs/rules/` の subtree 名と粒度が docs 体系に自然か。
  - `rules.md` の本文を「directory の役割 + 作成方法」までに留めるか、命名規約まで含めるか。
- Never:
  - wrapper を残したまま `rules.md` を追加して二重運用にしない。
  - 既存 node まで自動移行する複雑な互換処理を足さない。

## 非機能要件
- performance:
  - node 作成時の追加コストは symlink 作成と最小限の preflight に留める。
- reliability / consistency:
  - `init/update` で `docs/rules/` 原本が揃い、`new` で同じ symlink contract が生成されること。
- security:
  - symlink target は repo 内の `docs/rules/` に限定し、外部パスを指さないこと。
- operations:
  - maintainer が `find -type l` で契約を確認でき、rules の修正は中央実体だけで済むこと。

## 依存 / 影響範囲
- impacted components:
  - `src/spec_dock/assets/spec_dock/docs/rules/`
  - `src/spec_dock/assets/spec_dock/templates/`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/cli.py`
  - `tests/cli_runtime/`, `tests/test_init_update.py`
  - `spec-dock/docs/`, `src/spec_dock/assets/spec_dock/docs/`
- external dependency:
  - OS/filesystem の symlink サポート
- compatibility:
  - 既存 node の wrapper script は残ってよく、本 epic の主眼は新規 scaffold contract の整備である。

## 未確定事項
- なし:
  - `docs/rules/` は最小の役割説明と runtime command 導線に留め、詳細規約は既存 docs 参照へ寄せる方針で確定する。
