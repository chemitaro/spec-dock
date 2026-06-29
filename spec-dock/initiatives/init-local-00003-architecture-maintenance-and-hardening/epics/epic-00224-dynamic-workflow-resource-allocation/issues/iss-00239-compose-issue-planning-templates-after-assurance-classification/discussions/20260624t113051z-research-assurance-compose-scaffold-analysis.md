---
種別: research
ID: "20260624t113051z-research"
タイトル: "Assurance Compose Scaffold Analysis"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["iss-00239"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260624t113051z-research Assurance Compose Scaffold Analysis

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- 何を明らかにする調査かを記載する。

## sources / 調査方法 (必須)
- 参照先:
  - ...
- 検証手順:
  - ...
- 実験条件:
  - ...

## facts / 観測できた事実 (必須)
- 観測できた事実を記載する。

## inference / 推測 (必須)
- 事実から推測したこと:
  - ...
- 推測の根拠:
  - ...

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - ...
- 確認できない理由:
  - ...

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - ...
- pressure-test question として切り出すべき候補:
  - ...
- 質問せずに解決できた候補:
  - ...

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - ...
- 既存 docs / code / tests / discussions での使われ方:
  - ...
- 判断が必要な理由:
  - ...

## edge cases / 具体シナリオ (必須)
- edge case:
  - ...
- その edge case が requirement / design / plan に与える影響:
  - ...

## implications / 判断への含意 (必須)
- requirement / design / plan / adr へ影響する示唆を記載する。

## リスク/制約 (任意)
- ...

## 反映先 (任意)
- reflected_to:
  - ...

## 参考（References） (任意)
- ...
# Assurance Compose Scaffold Analysis

## 目的

Issue 作成直後から `design.md` / `plan.md` に通常の編集可能なテンプレートが存在することで、エージェントが `assurance classify` / `assurance compose` を通さずに設計書・実装計画書を書き始める問題を分析する。

この論点は、`iss-00238` の「動的 guidance を stdout で受け取る」問題と隣接しているが、主対象は issue 作成時の artifact lifecycle、Assurance 分類、テンプレート合成、preflight / validate の扱いである。そのため `iss-00238` には混ぜず、同一 Epic 配下の後続 Issue として扱う。

## 問題定義

Epic の設計段階では、Issue の `requirement.md` は共通テンプレートとして作成し、その後に lightweight / standard / strict / critical などの分類を行い、分類結果に応じて `design.md` / `plan.md` のテンプレートを合成する案が検討されていた。

しかし現状では、Issue 作成直後から `design.md` / `plan.md` が通常の編集可能なテンプレートとして存在する。この状態では、エージェントが以下の誤った順序で作業する可能性がある。

1. Issue を作成する。
2. `requirement.md` を十分に固める前に `design.md` / `plan.md` を開く。
3. `assurance classify` を実行しないまま設計・計画を書き始める。
4. 分類結果に応じたワークフロー切り替えや品質ゲートが効かない。

この挙動は、Epic の主目的である「タスクの重さに応じて動的に割り当てるリソースとワークフローを切り替える」ことを弱める。

## 現状観察

- `src/spec_dock/assets/spec_dock/templates/issue/requirement.md` / `design.md` / `plan.md` / `report.md` が Issue 作成時のテンプレートとして存在する。
- `design.md` / `plan.md` は、未分類状態であることを強く示す blocker ではなく、通常の設計・計画 scaffold として読める。
- `assurance compose` の仕組み自体は既に存在し、分類結果に基づいて `design.md` / `plan.md` / `report.md` の managed section を合成するテストも存在する。
- 一方で、Issue 作成時点のファイル構造は `assurance compose` を必須の通過点として見せられていない。
- `active/issue/design.md` / `active/issue/plan.md`、artifact preflight、tree validation、既存テストには `design.md` / `plan.md` の存在を前提とする箇所があるため、単純にファイルを作らない方式は影響が大きい。

## 選択肢

### A. Issue 作成時は `requirement.md` のみを作成する

Issue 作成直後は `requirement.md` と最小限の metadata のみを作成し、Assurance 分類後に `design.md` / `plan.md` を生成する。

利点:

- モデルに対して「まず要件定義だけを行う」ことを最も強く示せる。
- 分類前に設計・計画を書く誤操作を構造的に防ぎやすい。

欠点:

- 既存の active symlink、preflight、validate、テストが `design.md` / `plan.md` の存在を前提にしている。
- ファイル欠落を正常状態として扱うための runtime / validation / docs の変更が広範囲になる。
- 今回の改善としては blast radius が大きい。

### B. `design.md` / `plan.md` は作成するが、未合成プレースホルダーにする

Issue 作成直後からファイル名は存在させるが、中身は通常 scaffold ではなく「このファイルはまだ合成されていない。先に requirement と assurance classify / compose を完了せよ」という blocker にする。

利点:

- 既存の active symlink、preflight、validate、ファイル存在前提との互換性を保ちやすい。
- エージェントがファイルを開いた場合でも、正しい次アクションが明示される。
- `assurance compose` が placeholder を検出して置換・合成する流れにできる。
- 将来的に A へ移行する場合の中間段階にもなる。

欠点:

- ファイル自体は存在するため、極端に従わないエージェントが blocker を無視して本文を書き始める余地は残る。
- placeholder 状態を machine-readable に判定するための marker / front matter / preflight rule が必要になる。

### C. 現状維持し、guidance や skill の注意喚起だけで制御する

既存テンプレートを維持し、`guidance issue-planning` や skill 側で `assurance classify` / `compose` を促す。

利点:

- 実装影響は最小。

欠点:

- ファイル構造そのものが誤った作業順序を止めない。
- 今回の問題意識に対する対策として弱い。
- 「エージェントが読まないかもしれないファイルや注意書きに依存しない」という Epic の方針と合わない。

## 推奨方針

推奨は B である。

Issue 作成時には以下の状態にする。

- `requirement.md`: 共通の要件定義テンプレート。
- `design.md`: 未合成プレースホルダー。
- `plan.md`: 未合成プレースホルダー。
- `report.md`: 証跡・実施記録用の最小テンプレート。
- `.meta.json`: 通常通り。

`design.md` / `plan.md` の未合成プレースホルダーは、少なくとも以下を満たす。

- 人間にもエージェントにも「ここに本文を書いてはいけない」と分かる。
- `requirement.md` の具体化を先に要求する。
- `assurance classify --stage requirement` の実行を促す。
- その後に `assurance compose --artifact all` などの合成コマンドを実行するよう促す。
- machine-readable な状態 marker を持つ。

例:

```markdown
---
artifact_state: awaiting-assurance-compose
---

# Design

このファイルはまだ合成されていません。

先に `requirement.md` を具体化し、`assurance classify --stage requirement` を実行してください。
その後、`assurance compose --artifact all` を実行して、この Issue の分類に応じた設計書テンプレートを合成してください。

この状態のまま設計本文を書き始めないでください。
```

## 望ましい作業順序

1. `spec-dock new issue` で Issue を作成する。
2. `requirement.md` を具体化する。
3. `assurance classify --stage requirement` を実行する。
4. 分類結果を保存する。
5. `assurance compose --artifact all` を実行する。
6. 分類結果に応じて合成された `design.md` / `plan.md` を編集する。
7. reviewer / preflight / execution へ進む。

## 実装時の確認観点

- `assurance compose` が未合成プレースホルダーを安全に置換できること。
- `assurance compose` が、既に人間またはエージェントが実質本文を書いてしまった `design.md` / `plan.md` を不用意に上書きしないこと。
- `guidance issue-planning` が placeholder 状態を認識し、次アクションとして `assurance classify` / `assurance compose` を返せること。
- preflight / validate が placeholder 状態を「存在はするが planning 未完了」として扱えること。
- `active/issue/design.md` / `active/issue/plan.md` の symlink contract を壊さないこと。
- 既存の `assurance compose` テストに加え、Issue 作成直後の placeholder 状態を検証するテストを追加すること。

## スコープ判断

この変更は `iss-00238` と同じ Epic の目的に沿うが、直接の実装対象は異なる。

- `iss-00238`: agent が guidance を stdout から受け取り、生成済み workflow / runbook ファイルに依存しないようにする。
- `iss-00239`: Issue 作成直後の planning artifact lifecycle を見直し、Assurance 分類後に `design.md` / `plan.md` を合成する流れへ寄せる。

そのため、この論点は `iss-00238` に混ぜず、`iss-00239` として独立させる。
