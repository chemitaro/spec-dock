# Workflow: ADR（叩き台 → 決定 → accepted）

このドキュメントは、ADR（Architecture Decision Record）を **「議題が上がった時点」で起こし**、  
人間の最終決定で完成させるためのワークフローです。

関連:
- ツリー運用（Initiative/Epic/Issue）: `workflow-tree.md`
- 共通原則/チェックリスト（正）: `spec-dock-guide.md`

---

## 0. いつ ADR を作るか（トリガー）

次のような「後から理由が必要になる」「影響が広い」判断は ADR に残します。
- 境界/責務の切り方、データの正（SoR）、整合性モデル
- API/イベント/スキーマの契約、互換性方針、移行戦略
- セキュリティ/監査/PII、観測性の必須要件
- 代替案があり、Pros/Cons の比較が必要なもの

---

## 1. どこに置くか（スコープ選択）

原則: **影響範囲でレイヤーを決める**（最小スコープに閉じる）。

- Initiative ADR: 複数Epic/Issueに波及する決定（方針/ガードレール/全体アーキ）
- Epic ADR: そのEpic内の設計を支配する決定（契約/移行/整合性/観測性）
- Issue ADR: 局所的だが理由が必要な決定（実装方針のトレードオフ等）

迷ったら:
- まず Epic に置く（後で Initiative に昇格するのは容易）

---

## 2. ADR を作る（叩き台）

### 2.1 ADR の作成コマンド

```bash
./.spec-dock/scripts/spec-dock new adr --initiative init-0123 --title "..."
./.spec-dock/scripts/spec-dock new adr --epic epic-0124 --title "..."
./.spec-dock/scripts/spec-dock new adr --issue iss-0125 --title "..."
```

生成先:
- `<scope>/adrs/adr-xxxx-<slug>.md`

### 2.2 叩き台として埋める（結論は未決のまま）

- エージェントは **Decision（結論）を確定しない**
- まず Context / Options / Rationale / Consequences を整理する
- 必要に応じて UML（任意）を差し込む（図の形式は固定しない）

### 2.3 ヒアリングに使う（質問 → 回答 → 更新）

意思決定が必要になったら、ADR を **質問の叩き台（判断材料のパッケージ）** として使います。

推奨:
- Decision は **未決（TBD）** のままにし、まず判断材料を埋める
  - 「決めたいこと（質問）」「判断の観点」「不確実点（追加で確認したいこと）」を明示する
- Options は複数提示し、Pros/Cons と影響（移行/ロールバック/運用）まで書く
- 推奨案は書いてよいが、**結論（Decision）として確定しない**

ユーザー回答後:
- Decision を穴埋めして `状態: accepted` にする
- 仕様（requirement/design/plan）に決定内容を反映し、`TBD` を解消する（ADR↔仕様は相互リンク）

---

## 3. 人間が決める（決定 → accepted）

1. ユーザー/レビュアーが最終決定を下す
2. ADR の Decision を更新する
3. フロントマターの `状態:` を `accepted` にする
4. 関連仕様（requirement/design/plan/report）へ反映し、相互リンクを更新する

補足:
- 既存ADRを置き換える場合は `superseded` を使い、参照関係を残す

---

## 4. 仕様ツリーと整合させる（リンク規約）

ADR は単独では完結しません。仕様ツリーの正（requirement/design/plan/report）と相互リンクさせます。

推奨:
- requirement/design/plan 側に「関連ADRリンク」を貼る
- ADR 側の References に「関連仕様」「PR/実装」「フォローアップIssue」を貼る

---

## 5. よくある失敗（防止）

- エージェントが結論を勝手に書く → **Decision はユーザー決定後に更新**
- 選択肢が少ない/比較できない → Options を複数列挙し Pros/Cons を書く
- 影響（移行/ロールバック）が無い → Consequences に必ず残す
- ユーザーが決められない → 「決めたいこと（質問）/判断の観点/選択肢/影響」を短く揃えてから投げる
