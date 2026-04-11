---
title: User-facing doc gap analysis after dependency metadata unification
status: approved
kind: disc
author: Codex CLI
created_at: 2026-04-11T00:00:00Z
updated_at: 2026-04-11T00:00:00Z
---

# User-facing doc gap analysis after dependency metadata unification

## 目的

`.meta.json` への dependency metadata 統合と、dependency mutation の command-first 運用への移行が完了した前提で、利用者向け情報がどこまで追従しているかを整理する。

この資料では、要件化や設計化の前段として次を明確にする。

- 現状の利用者向け情報の到達点
- 理想状態
- 理想に対して不足しているギャップ
- どこから直すべきか

## 対象範囲

- docs 正本
  - `src/spec_dock/assets/spec_dock/docs/**`
- dogfooding mirror
  - `spec-dock/docs/**`
- skill / adapter
  - `src/spec_dock/assets/codex_skills/**`
  - `.agents/skills/**`
- CLI help
  - `./spec-dock/scripts/spec-dock --help`
  - `./spec-dock/scripts/spec-dock deps --help`

## 現状分析（As-Is）

### 1. 中核 reference は概ね更新済み

依存関係の新しい正本はかなり明確に書かれている。

- [reference_deps.md](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/docs/reference_deps.md)
  - canonical storage が node 直下 `.meta.json` の top-level `depends_on` であることを明記している
  - reader は `.meta.json` のみを読み、`deps.json` dual-read / auto-migration を行わないと明記している
  - `deps add` / `deps remove` の command contract を明記している
  - duplicate add は success/no-op、remove not-found は `edge_not_found` error と整理されている
- [reference_sync.md](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/docs/reference_sync.md)
  - sync が `.meta.json` を SSOT として走査することを明記している
  - hard cutover owner split を `iss-00062` / `iss-00063` で説明している
- [workflow_issue.md](/srv/mount/spec-dock/spec-dock/docs/workflow_issue.md)
  - `sync` / `validate` / review 証跡を report に残す運用が明文化されている
- [spec-dock-issue-execution skill](/srv/mount/spec-dock/.agents/skills/spec-dock-issue-execution/SKILL.md)
  - complete 判定に `sync` / `validate` / review pass が必要であることが反映されている

### 2. CLI help も mutation command 自体は露出している

- `./spec-dock/scripts/spec-dock --help`
  - `deps` サブコマンドは表示される
- `./spec-dock/scripts/spec-dock deps --help`
  - `check`, `add`, `remove` が表示される

つまり、実装の存在自体がユーザーから完全に隠れている状態ではない。

### 3. ただし入口 docs に旧表現が残る

利用者が最初に見る入口の一部には、現在 contract と食い違う表現が残っている。

- [docs README](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/docs/README.md)
  - 最短コマンドが `./spec ...` のまま
  - 現在の実行経路 `./spec-dock/scripts/spec-dock ...` と不一致
- [dogfooding sync.md](/srv/mount/spec-dock/spec-dock/docs/sync.md)
  - `spec-dock/initiatives/**/meta.json` と legacy 名で記載されている
  - 現在の `.meta.json` contract と不一致
- [dogfooding old guide](/srv/mount/spec-dock/spec-dock/docs/spec-dock-guide-old.md)
  - old 入口として残っており、誤誘導のリスクがある

### 4. docs の深さによって更新度合いにばらつきがある

- 深い reference は比較的新しい
- README / guide / old guide / 補助 docs の一部は古い
- provider 正本と dogfooding mirror の一部で整合が崩れている

このため、詳しい利用者ほど正しい情報に辿り着ける一方、初見ユーザーほど古い案内を踏みやすい状態になっている。

## 理想状態（To-Be）

理想状態は次の 4 条件を同時に満たすこと。

### 1. 入口から正しい実行経路へ導かれる

README / guide / workflow / help の最初の経路で、現在サポートされる command surface に最短で辿り着けること。

具体的には次が必要。

- 実行例は `./spec-dock/scripts/spec-dock ...` に統一されている
- `deps add/remove/check` が入口 docs から発見できる
- `sync`, `validate`, `active set` との関係がすぐ分かる

### 2. storage / mutation / downstream parity の境界が一貫している

ユーザーが docs を横断しても、次の理解がぶれないこと。

- dependency metadata の正本は `.meta.json`
- raw storage は `depends_on`
- mutation は command-first
- `deps.json` は legacy であり fallback しない
- rollback は compatibility mode ではなく revert ベース

### 3. host / agent 利用者にも同じ contract が伝わる

skills / adapters / workflow docs / generated state guidance が同じ前提で揃っていること。

### 4. 古い導線が残る場合でも「旧情報」と分かる

削除しない文書がある場合でも、現行の案内と混同しないように明示されていること。

## ギャップ整理（不足しているもの）

### Gap A: 入口コマンドの不統一

現状:
- [README.md](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/docs/README.md) と dogfooding 側の [README.md](/srv/mount/spec-dock/spec-dock/docs/README.md) に `./spec ...` が残っている
- [reference_deps.md](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/docs/reference_deps.md) / [reference_sync.md](/srv/mount/spec-dock/spec-dock/docs/reference_sync.md) にも `./spec ...` が残る箇所がある

不足:
- 現在の supported execution path を入口文書まで反映し切れていない

影響:
- 初見ユーザーが最初の 1 コマンド目で迷う
- deep reference は正しくても adoption friction が高い

優先度:
- 高

### Gap B: `.meta.json` 統合の説明が全 docs で均一ではない

現状:
- reference_deps / reference_sync は `.meta.json` only を説明できている
- ただし [sync.md](/srv/mount/spec-dock/spec-dock/docs/sync.md) には `meta.json` 表記が残る
- GitHub / guide / 補助 docs にも旧表記の可能性がある

不足:
- `.meta.json` only contract が入口から補助文書まで均一に反映されていない

影響:
- 利用者が「legacy 名でもよいのか」を誤解しやすい
- hard cutover 後の fail-fast 方針が弱く見える

優先度:
- 高

### Gap C: command-first mutation の発見性がまだ弱い

現状:
- `deps add/remove` は reference と help にはある
- しかし README / guide の最短導線では強く露出していない

不足:
- 「依存変更は `.meta.json` 直編集ではなく command で行う」という運用原則の露出が弱い

影響:
- 変更後アーキテクチャの価値が利用者に伝わりにくい
- 旧運用の癖で metadata 直編集に戻りやすい

優先度:
- 高

### Gap D: old / secondary docs の整理不足

現状:
- [spec-dock-guide-old.md](/srv/mount/spec-dock/spec-dock/docs/spec-dock-guide-old.md) が残っている
- [sync.md](/srv/mount/spec-dock/spec-dock/docs/sync.md) は current reference_sync と役割が重なりつつ内容が古い

不足:
- 現行 docs と旧 docs の役割分離が明示されていない

影響:
- 入口が複数になり、どれを信じるべきか分かりにくい

優先度:
- 中

### Gap E: provider 正本と dogfooding mirror の整合確認が未整理

現状:
- provider 側ではかなり整理されている
- dogfooding 側にも mirror があるが、一部旧文書が混ざっている

不足:
- 「どの文書が provider-side source of truth か」が docs メンテナ視点では明確でも、利用者視点では分かりにくい
- mirror の drift を検出・是正する運用が docs 全体ではまだ見えにくい

影響:
- 修正漏れが再発しやすい

優先度:
- 中

### Gap F: help は存在するが、説明密度が薄い

現状:
- CLI help は `deps {check,add,remove}` を表示する
- ただし help だけでは `.meta.json` 統合や no dual-read の思想までは伝わらない

不足:
- help と docs の間をつなぐ短い説明導線が弱い

影響:
- help は実装露出としては十分だが、利用者教育としては不十分

優先度:
- 中

## まとめ判定

### すでに十分と言えるもの

- dependency metadata が `.meta.json` に統合されたこと自体の reference 契約
- `deps add/remove` command の存在と振る舞い
- no dual-read / no auto-migration / fail-closed の基本方針
- issue execution skill における証跡要求

### まだ十分と言えないもの

- README / guide / old docs を含む入口情報
- command-first mutation を利用者が最短経路で理解できる導線
- `.meta.json` only を全資料で一貫して説明すること
- provider 正本と dogfooding 側の表現統一

## 推奨アクション

### 第1優先

- docs README の最短コマンドを current runtime path に統一する
- reference_deps / reference_sync の command examples から `./spec ...` を除去する
- `.meta.json` / `depends_on` / command-first mutation を README / guide でも明示する

### 第2優先

- `sync.md` の旧表記を current contract に揃えるか、reference_sync への誘導文書に縮退する
- old guide を archival 扱いにするか、現行導線から外す

### 第3優先

- skills / adapters / docs の「利用者向け契約」を横断する checklist を設け、`.meta.json` / command-first / no dual-read の 3 点を確認可能にする

## 要件化前の論点

この分析を要件・設計・計画へ落とす前に、次の論点を決めるとよい。

- 今回の対象を「利用者入口 docs の是正」に絞るか
- old docs を残すか削除するか
- help の補強まで scope に含めるか
- provider 正本だけ直して mirror sync で閉じるか、dogfooding 側の旧文書整理まで含めるか

## 結論

現状は「深い reference はかなり正しいが、入口と旧導線がまだ弱い」である。

したがって、次の要求は「依存 metadata 統合と command-first mutation 運用を、利用者入口 docs / reference / 補助 docs / skills まで一貫して反映すること」として定義するのが自然である。
