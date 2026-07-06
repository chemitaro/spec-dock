---
種別: artifact
ID: "20260706t141506z-requirement-onboarding-guide"
タイトル: "epic-00283 要件定義書 — 新メンバー向け読み解きガイド"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-06"
親: ["epic-00283"]
template: "blank"
authority: "raw"
derived_from:
  - "../requirement.md（canonical / この Epic の正本）"
reflected_to: []
---

# epic-00283 要件定義書 — 新メンバー向け読み解きガイド

> **位置づけ**
> この資料は `epic-00283` の canonical 要件定義書 [`../requirement.md`](../requirement.md) を、
> 初見のメンバーでも一読で構造を掴めるように**再構成**したものです。
> 表現は分かりやすく変えていますが、**原文の情報は一つも削っていません**。
> 迷ったときは必ず `requirement.md` 本文を一次情報として参照してください。
> 本資料自体は canonical docs でも ADR でもなく、read-only の**理解補助 artifact**です。

---

## 0. まず結論だけ知りたい人向け（3分要約）

| 論点 | 結論 |
|---|---|
| このEpicは何をする？ | ChatGPT（GPT-5.5 Pro Extended）に、SpecDockの要件/設計/計画のドラフトをZIPファイルで大量生成させ、それを**安全に検証してから**人間が採否判断する仕組みを、まずは実験（dogfood）スクリプトとして作る |
| ChatGPTの出力は正本（canonical）になる？ | **ならない。** どこまで行っても「検証が必要な証拠（evidence）」止まり。正本の書き換えは main orchestrator だけが行う |
| ChatGPTがIssueのgrade（Lite/Standard/Strict/Critical）を決めていい？ | **決めない。** 決めるのはローカルの `.assurance.json` / `assurance classify`。ChatGPTは「おすすめ」を言えるだけ |
| ChatGPTが生成したZIPをリポジトリに直接展開していい？ | **しない。** 必ず「隔離(quarantine) → 検証 → 差分確認(dry-run diff) → staged配置 → 人間/orchestratorの採否判断 → 新規のspec-reviewer通過」という順番を通す |
| 今すぐ本番導入（shipped runtime）する？ | **しない。** v1は `manual-tests/oracle-zip-authoring/` 配下の実験専用スクリプト群。本番化は後続のEpic/ADRでの判断に委ねる |
| ChatGPTが使えない時は？ | 「動かないから失敗扱い」ではなく「blocked/skipped評価」として記録し、**必ず手動の既存ワークフローで続行できる**ようにする |

一言で言うと：

> **「ChatGPTに“長い文章を書かせる”のは良い。ChatGPTに“判断させる”のは良くない。」**
> という原則を、ZIPの取り扱い・Issueのgrade決定・テンプレート選択・reviewer合否のすべてに徹底する、というのがこのEpicの骨格です。

---

## 1. 用語集（このEpicで頻出する言葉）

新メンバーがつまずきやすい用語を先にまとめます。本文を読む前にここだけでも目を通してください。

| 用語 | 意味 |
|---|---|
| **ZIP authoring pack** | ChatGPTが返す、複数ファイルをディレクトリ構造ごと含んだダウンロード可能なZIP。要件ドラフト・設計ブリーフ・計画ブリーフなどをまとめて含む |
| **evidence（証拠） / evidence-only** | 「まだ採用されていない参考情報」という位置づけ。正本ではない。ZIP、ChatGPTの発言、research artifactなどは全部これ |
| **canonical（正本）** | `requirement.md` / `design.md` / `plan.md` / accepted ADR / `report.md` の Evidence Adoption Ledger。SpecDockにおいて「正しい」と認められた唯一の情報 |
| **quarantine（隔離）** | ZIPを展開する前に、リポジトリの外側の安全な場所に一旦保存し、中身を検査するための領域 |
| **dry-run diff** | 「もしこのZIPの内容をcanonical docsに反映したら、どこがどう変わるか」を**実際には書き換えずに**表示する差分プレビュー |
| **staged artifact** | 検証を通ったZIPの中身を、無害化（サニタイズ）した上でEpic配下の `artifacts/` に一次保管したMarkdown |
| **adoption（採用） / Evidence Adoption Ledger（EAL）** | staged artifactの内容のうち、実際にcanonical docsへ取り込むと決めた範囲を `report.md` に記録する台帳。状態は adopted / partially_adopted / rejected / deferred / stale / blocked のいずれか |
| **profile（プロファイル） / authorized_profile** | IssueのグレードのようなものでLite/Standard/Strict/Critical。誰がどれだけ厳格にレビューするかを決める。`.assurance.json` と `assurance classify`（ローカルの仕組み）だけが決定権を持つ |
| **profile recommendation** | ChatGPTが「このIssueはStrictが良さそう」と“提案”すること。あくまで参考情報で、`authorized_profile` そのものではない |
| **section-map / missing-section-report** | ChatGPTが設計書・計画書の「どの見出し（section）を埋めたか／埋め損ねたか」を報告するファイル。テンプレートの骨格と一致しているかを機械的に照合するために使う |
| **skeleton（スケルトン）** | ローカルの `assurance compose` が生成する、選ばれたprofile用の空テンプレート（骨組み）。ChatGPTはこの骨組みの中身を埋めるだけで、骨組み自体は作らない |
| **stale_if / stale condition** | 「この情報はどんな時に古くなる（信頼できなくなる）か」の条件。例：ソースファイルのハッシュが変わった、ブランチが変わった、など |
| **branch-sensitive mode / default-ref mode** | ZIP生成時に「現在の作業ブランチの状態」を前提にするか（branch-sensitive）、しないか（default-ref）というモード。前者は厳しい前提条件（clean worktree等）を必要とする |
| **denylist** | ZIPに含めてはいけないパスや内容（secret、`.git`、`.ssh`、`.env`など）のブロックリスト |
| **fresh spec-reviewer** | 「毎回新しく」レビューを行うSpecDockのreviewer gate。ChatGPTの自己レビューや「reviewer視点でのコメント（reviewer-focus）」はこれの代わりにはならない |
| **dogfood** | 本番導入前に、まず自分たち（開発チーム）が実際に使ってみて安全性・有用性を検証すること |

---

## 2. このEpicは何をするものか

### 2.1 目的（親Initiativeとの関係）

`epic-00283` は、親Initiative `init-local-00003 Architecture Maintenance and Hardening` の一部です。

**やること**：ChatGPT Use / GPT-5.5 Pro Extended を、SpecDockの「仕様執筆（authoring）の裏方（backend）」として実験的に使えるようにする。ChatGPTが返すZIPパックやstructured outputを、**正本ではなく「未検証の証拠」として安全に受け取り→検証→staged evidenceに変換→main orchestratorが正本への採否を判断する**、という一連のworkflow / script / prompt / skillの土台を整える。

**やらないこと**：ChatGPTに正本を書かせること、reviewer gateをChatGPTに置き換えさせること、Issueのgrade/profileをChatGPTに決めさせること。SpecDockの「正本は誰が持つか（source-of-truth）」「artifactの権限」「profileの決定権」「毎回フレッシュなreviewer gate」は**そのまま維持**した上で、ChatGPTの「長文・複数ファイルを一括生成する能力」だけを安全に活用する。

### 2.2 背景・なぜ今やるのか（Why now）

- これまでの調査で、ChatGPT Use / GPT-5.5 Pro Extendedが「高度な分析」「設計・計画のドラフト作成」「Issueの切り分け（slicing）」「reviewer視点でのコメント」「ZIPによる複数ファイル出力」に有効であることが確認できた。
- 一方で、ChatGPTの出力は次のようなSpecDockの信頼の根拠（authority）を保証できない：ローカルのgitの状態、untrackedファイル、fresh reviewerの独立性、`.assurance.json`、テンプレートのハッシュ、実行時バリデーション、テスト実行。
  - → だからChatGPTの出力をそのままcanonical docsやreviewer合格として扱うと、SpecDockの権限境界が崩れてしまう。
- 特に今回のユーザー実験で、**ChatGPTがディレクトリ構造を保ったダウンロード可能なZIPを出力でき、それを展開できる**ことが分かった。これはEpic設計/計画と複数のIssueドラフトを一括生成する手段として有望。
  - ただし、ZIPは「パストラバーサル」「隠しファイル」「シンボリックリンク」「バイナリ」「secret」「古くなったソース」「不正な権限主張（unsafe authority claim）」などの検査を必ず通す必要がある。
- そのため、まずは本番導入（shipped runtime）ではなく、`manual-tests/oracle-zip-authoring/` 配下の**dogfood専用スクリプト群**として、ZIPの事前準備（preflight）・プロンプト生成・取り込み・検証・差分・staging・採用ハンドオフを検証する。

---

## 3. できること／できないこと（capability envelope）

新メンバーが最も混同しやすいのがこの境界線です。表で整理します。

### 3.1 対象capability（このEpicでやること）

- ChatGPT Use / GPT-5.5 Pro Extendedに、複数ファイル・長文のauthoring outputをZIPパックまたはstructured packとして生成させる。
- ZIPパックをリポジトリ外のquarantineに取り込み、安全検査・スキーマ検証・ソースハッシュ/古さ（stale）検証・dry-run diff・staged artifact描画に通す。
- Epic→Issue候補生成、Issueのselected-profileでの設計/計画の穴埋め、mismatch/staleの検出、をdogfoodシナリオとして扱う。
- `adoption-map`、`eal-proposal`、`reviewer-focus`、`profile recommendation`、`section-map`、`missing-section-report`を機械可読な証拠（evidence）として扱う。
- ChatGPTの手動プロンプト実行そのものをdogfoodとして使い、将来のscript/skillに必要な事前準備・プロンプトの形・出力の形・失敗パターンを抽出する。

### 3.2 モデル／ライフサイクルの境界線（守るべきルール）

| # | ルール |
|---|---|
| 1 | ChatGPTのZIPは**evidence-onlyである**（＝それ自体では何も確定しない） |
| 2 | ChatGPTはprofileの**推奨（recommendation）は出せるが、`authorized_profile`を決定しない** |
| 3 | ChatGPTは選ばれたスケルトンのsectionを埋められるが、**テンプレート選択・`.assurance.json`更新・canonical composeは行わない** |
| 4 | ChatGPTの自己レビュー／reviewer-focusは**reviewer入力ではあるが`spec-reviewer`合格ではない** |
| 5 | Canonical採用は**main orchestratorが**`requirement.md`/`design.md`/`plan.md`/`report.md`へ再記述し、**fresh `spec-reviewer`を通す** |
| 6 | ZIP生成とcanonicalへの昇格（phase promotion）は別物 — **「bundle生成 ≠ bundle採用」を不変条件とする** |

### 3.3 cross-Issue invariant（後続のIssue全体に共通で効く不変条件の種）

- ZIPの検証は**fail-closed**（＝疑わしきは通さない）。
- Canonical docsへの**直接上書きは禁止**。
- `profile recommendation` ≠ `authorized_profile`。
- `template rendering`（テンプレート生成） ≠ `section fill`（中身の穴埋め）。
- 生のtranscript・secret・credential・token・cookie・個人情報は、パック／artifactに**含めない**。
- 提案されたコマンド（proposed commands）は、本番昇格するまで**dogfood専用**。
- ChatGPT／ブラウザ／GitHub connectorが使えない場合は「劣化成功（degraded success）」ではなく「**blocked/skipped**」として扱う。

### 3.4 対象外のcapability（このEpicではやらない）

- reviewer gateの置き換え。
- 本番runtimeコマンドの即時導入。
- provider registry／汎用の外部oracleアダプタ。
- ChatGPTによる`.assurance.json`の作成・更新。
- ChatGPTによる全profile分のテンプレート variant生成。
- 生ZIP／展開後のツリーをリポジトリのcanonical artifact化すること。
- GitHub PRレビュー／マージ準備の置き換え。
- Deep Researchのライブ信頼性の改善。

---

## 4. 全体の流れ（ライフサイクル）

正常系ユースケースを1本の流れとして図示します（詳細は次章）。

```
① oracle-authoring-preflight
   repo / ref / source_paths / source_hashes / denylist / profile state / stale_if を固定
            │
            ▼
② oracle-authoring-prompt-pack
   ChatGPTに渡すprompt・source manifest・selected skeleton・ZIP schema・authority boundaryを生成
            │
            ▼
③ ChatGPT (GPT-5.5 Pro Extended)
   "specdock-authoring-pack/" をrootに持つZIPを返す
            │
            ▼
④ oracle-zip-capture / oracle-zip-intake
   リポジトリ外のquarantineへ保存し、central directoryを検査（まだ展開しない）
            │
            ▼
⑤ oracle-zip-validate
   path / schema / manifest / provenance / source hash / 不正な権限主張 / profile不一致 を検査
            │
            ▼
⑥ oracle-zip-diff
   canonicalを一切書き換えないdry-run diffを作成
            │
            ▼
⑦ oracle-zip-stage
   scope-localな artifacts/ に、無害化(sanitized)されたMarkdown evidenceを作成
            │
            ▼
⑧ main orchestrator が adoption-map を確認
   採否を report.md の Evidence Adoption Ledger に記録
            │
            ▼
⑨ 採用された内容だけをcanonical docsへ再記述
   → 各phaseで fresh spec-reviewer gate を通す
```

①〜⑦は「証拠を作る／検証する」フェーズ、⑧〜⑨だけが「正本に反映する」フェーズです。この境界線がこのEpic全体で最も重要な考え方です。

---

## 5. ユースケース

### 5.1 正常系（うまくいく場合の流れ）

1. Maintainerが、Epic/Issueの要件、ソースパス、スコープ、対象外、stale条件をpreflightに渡す。
2. `oracle-authoring-preflight`（提案コマンド）がrepo/ref/source_paths/source_hashes/denylist/profile state/stale_ifを固定する。
3. `oracle-authoring-prompt-pack`（提案コマンド）がChatGPTに渡すprompt、source manifest、selected skeleton、ZIP schema、authority boundaryを生成する。
4. ChatGPTが`specdock-authoring-pack/`をrootに持つZIPを返す。
5. `oracle-zip-capture` / `oracle-zip-intake`（提案コマンド）がZIPをリポジトリ外quarantineに保存し、central directoryを検査する。
6. `oracle-zip-validate`（提案コマンド）がpath、schema、manifest、provenance、source hash、不正な権限主張、profile不一致を検査する。
7. `oracle-zip-diff`（提案コマンド）がcanonical上書きなしのdry-run diffを作る。
8. `oracle-zip-stage`（提案コマンド）がscope-localな`artifacts/`にsanitized Markdown evidenceを作る。
9. Main orchestratorがadoption-mapを確認し、採否を`report.md`のEvidence Adoption Ledgerへ記録する。
10. 採用内容だけをcanonical docsへ再記述し、fresh `spec-reviewer` gateを通す。

### 5.2 例外・運用シナリオ（うまくいかない／注意が必要な場合）

| シナリオ | 扱い |
|---|---|
| GitHub connector／repo／target refが利用不可 | branch-sensitiveなパック生成は**hard fail**する |
| current branchが利用不可 | default-ref modeへfallback可能。ただしbranch-sensitiveな主張は**adoption対象外 or stale条件付き** |
| ZIPに絶対パス、`..`、隠しパス、symlink、hardlink、デバイスファイル、バイナリ、入れ子アーカイブ、実行権限、`.env*`、token、cookie、secret、`.git`、`.ssh`、`.codex`、`.agents`、`.github`が含まれる | **reject（拒否）** |
| `manifest.json`が`authority: evidence_only`、`adoption_status: unreviewed`を示さない | **reject** |
| `profile_resolution.status`がstale／blocked | 設計/計画ドラフトは**adoption対象外** |
| `authorized_profile`とZIPのselected profileが不一致 | section fillとしては**reject**。自然言語の主張だけはsalvage（拾い上げ）候補にできる |
| Strict／Critical | ZIP bundle生成自体は許可するが、canonical採用は**force staged**とし、specialist／fallback evidence gateを残す |
| ChatGPT利用不可／ZIP生成失敗 | **手動authoring pathを継続する**（詰まない） |

---

## 6. Epic要件一覧（E-RQ-001〜E-RQ-013）

まず全体の索引、その後に各要件の詳細です。

| ID | 要件名 | ひとことで言うと |
|---|---|---|
| E-RQ-001 | Dogfood専用のスクリプト面 | まずは実験専用スクリプトとして置き、正本は書き換えない |
| E-RQ-002 | Preflight／source manifest契約 | 検証に必要な前提情報（repo/ref/hash/stale等）を固定する |
| E-RQ-003 | Prompt pack生成 | ChatGPTに渡す指示・素材をallowlistベースで作る |
| E-RQ-004 | ZIP packのスキーマ | ZIPの構造・必須ファイルを定義する |
| E-RQ-005 | 安全なZIP取り込み／検証 | 展開前に危険なファイルを弾く |
| E-RQ-006 | Dry-run diff／staging | canonicalを直接書き換えず、差分とstaged evidenceを作る |
| E-RQ-007 | Artifact権限境界 | 何がevidenceで何がcanonicalかを明確にする |
| E-RQ-008 | Issue profileの制御 | profileの決定権はローカルのassuranceにあると明記する |
| E-RQ-009 | テンプレート生成と穴埋めの分離 | スケルトンを作るのはローカル、埋めるのはChatGPT |
| E-RQ-010 | Bundle生成とstaged採用の分離 | ZIPに全部入っていても、採用はrequirement→design→planの順に段階的に行う |
| E-RQ-011 | Dogfoodシナリオとメトリクス | A/B/Cのシナリオを実行し、指標を取る |
| E-RQ-012 | 手動フォールバック | ChatGPTが使えなくても既存ワークフローが続く |
| E-RQ-013 | 将来の本番昇格基準 | v1では本番化しない。判断は後続のIssue/ADRに委ねる |

### E-RQ-001：Dogfood専用のスクリプト面

- 初期スクリプト群は`manual-tests/oracle-zip-authoring/`配下に置く。
- 提案コマンドはruntime contract（本番の契約）として扱わない。
- スクリプトはcanonical docsを書き換えない。

### E-RQ-002：Preflight／source manifest契約

- repo、requested ref、fallback ref、scope id、source paths、source hashes、添付ファイルhashes、denylist結果、stale_if、profile stateを記録する。
- branch-sensitive modeでは、clean worktree、pushed head、PR head SHA一致を要求する。
- default-ref modeでは`branch_sensitive=false`を明示する。

### E-RQ-003：Prompt pack生成

- ChatGPTに渡すsource packはallowlistベースにする。
- Promptには、ZIP schema、authority boundary、profile control、template fill制約、禁止される主張（forbidden claims）、output rootを明記する。
- Promptは、リポジトリのartifactに含まれる「命令のような文章」を**データとして扱わせる**（＝プロンプトインジェクション対策）。

### E-RQ-004：ZIP packのスキーマ

- ZIPは単一root `specdock-authoring-pack/`を持つ。
- 必須ファイル：`manifest.json`、`provenance.json`、`stale-if.json`、source hash／source manifest、`adoption/adoption-map.json`、validation report。
- Issue-aware packは、profile request／resolution／recommendation／assurance snapshot／template source／bundle policy／section-map／missing-section-reportを持つ。
- Candidate-only packは、Issue候補ごとに`candidate.json`、`profile.json`、`requirement-draft.md`、`design-brief.md`、`plan-brief.md`、classification inputs、creation command suggestionを持てる。

### E-RQ-005：安全なZIP取り込み／検証

- リポジトリへの直接展開を禁止する。
- central directory inspection の後に安全な展開を行う。
- パストラバーサル、隠しパス、symlink、hardlink、デバイスファイル、実行権限、バイナリ、入れ子アーカイブ、oversize、denylist対象のパス／内容を拒否する。
- スキーマ不正、source hash不一致、stale_if欠落、不正な権限主張、未列挙sourceへの依存は**adoption対象外**とする。

### E-RQ-006：Dry-run diff／staging

- ZIPの内容をcanonical docsへ直接配置しない。
- Dry-run diffは、意図されたcanonical targetとstaged artifact targetを分けて示す。
- `artifacts/`へ置くのは、sanitizedなフラットMarkdownの要約／disc／research／decision-candidate evidenceとする。
- 生ZIP／展開後ツリーの永続的なリポジトリ保存は**v1のスコープ外**。必要なら後続のartifact-pack ADRへ送る。

### E-RQ-007：Artifact権限境界

- ZIP、ChatGPT transcript、research、disc、onboarding brief、validation reportは**adoption前のevidence**とする。
- Canonical authorityは、採用済みcanonical docs、accepted ADR、または`report.md`のEvidence Adoption Ledger／Spec Authoring Gateに限る。
- Evidence Adoption Ledgerなしに、委譲された／ChatGPT由来のevidenceの採用を主張しない。

### E-RQ-008：Issue profileの制御

- `authorized_profile`は`.assurance.json` / `assurance classify`が決定する。
- `--profile auto`はローカルのprofile resolutionを意味し、**ChatGPTのrecommendationを意味しない**。
- ChatGPTは`minimum_safe_profile`、Lite disqualifier、Strict/Critical triggerをrecommendation evidenceとして返せる。
- ChatGPTは`.assurance.json`を作成・更新しない。

### E-RQ-009：テンプレート生成とsection穴埋めの分離

- `assurance compose`が選ばれたprofileのスケルトンを生成し、template hash／skeleton hash／section inventoryを固定する。
- ChatGPTは選ばれたスケルトンのsectionを埋め、section-mapとmissing-section-reportを返す。
- All-profile variants（全profile分のバリエーション生成）は、candidate-only brief以外では**invalid**とする。

### E-RQ-010：Bundle生成とstaged採用の分離

- ZIPにrequirement／design／planが同梱されていても、canonical採用はrequirement→design→planの順に**staged**で行う。
- 各phaseでfresh `spec-reviewer` passが必要である。
- Self-review／reviewer-focusはreviewer入力であり、reviewer passではない。

### E-RQ-011：Dogfoodシナリオとメトリクス

- v1では少なくとも次の3シナリオを実行する：
  - A：Candidate-only Epic→Issue ZIP
  - B：Existing Issue selected-profile ZIP
  - C：Mismatch probe
- メトリクスは、validation失敗率、adoption比率、人間の編集負担、fresh reviewerの手戻り回数、profile mismatchによるblock、canonical上書き防止の実績、手動fallback成功率を含む。

### E-RQ-012：手動フォールバック

- ChatGPT／ブラウザ／GitHub connector／ZIP生成が利用不可な状態は「劣化成功」ではない。
- 手動authoring pathと既存のSpecDockワークフローは常に継続可能でなければならない。

### E-RQ-013：将来の本番昇格基準

- 本番runtimeコマンド、provider docs、optional adapter、artifact-pack contract、reviewer gate backendは**v1のacceptance対象ではない**。
- Dogfoodのevidenceが安全性・有用性を示した場合だけ、後続のIssue／ADRで本番昇格を検討する。

---

## 7. Epic受け入れ条件（E-AC-001〜E-AC-012）

各条件は「前提 → 操作 → 期待結果 → 観測点」の4点セットで書かれています。

| ID | 検証すること |
|---|---|
| E-AC-001 | Preflightがbranch/repo/source manifestを固定する |
| E-AC-002 | ZIP intakeが危険なアーカイブを拒否する |
| E-AC-003 | 必須のmanifest／provenance／adoption mapが検証される |
| E-AC-004 | 不正な権限主張（unsafe authority claim）がblockされる |
| E-AC-005 | Profile制御がローカルassurance所有として守られる |
| E-AC-006 | 選ばれたスケルトンの穴埋めがsection-mapと一致する |
| E-AC-007 | Candidate-only Epic→Issue ZIPがprofile固有テンプレートを出さない |
| E-AC-008 | Dry-run diffとstaged artifactがcanonical上書きを防ぐ |
| E-AC-009 | Evidence Adoption Ledgerへのhandoffが可能である |
| E-AC-010 | Fresh spec-reviewer gateが維持される |
| E-AC-011 | Dogfood A/B/Cが完了する |
| E-AC-012 | 手動fallbackが引き続き機能する |

### E-AC-001：Preflightがbranch／repo／source manifestを固定する

- 前提：current branchが利用不可、またはdefault-ref mode。
- 操作：提案`oracle-authoring-preflight`を実行する。
- 期待結果：inspected repo/ref、branch_sensitive、source_paths、stale_if、denylist結果が記録される。
- 観測点：preflight JSON／summary artifact。

### E-AC-002：ZIP intakeが危険なアーカイブを拒否する

- 前提：パストラバーサル、隠しパス、symlink、バイナリ、実行可能ファイル、入れ子アーカイブを含むfixture。
- 操作：提案`oracle-zip-intake` / `oracle-zip-validate`を実行する。
- 期待結果：安全な展開の前にreject（拒否）され、リポジトリにcanonical／artifactへの副作用が出ない。
- 観測点：validation report、git status／filesystem検査。

### E-AC-003：必須のmanifest／provenance／adoption mapが検証される

- 前提：valid／invalidなZIP fixture。
- 操作：スキーマ検証を実行する。
- 期待結果：`manifest.json`欠落、`provenance.json`欠落、source hashes欠落、stale_if欠落、adoption-map欠落は**adoption対象外**。
- 観測点：schema validation report。

### E-AC-004：不正な権限主張がblockされる

- 前提：ZIPのmanifestまたはMarkdownが`authority: accepted`、`adoption_status: adopted`、reviewer pass、phase completion、implementation readinessを主張している。
- 操作：validationを実行する。
- 期待結果：packはreject、またはadoption対象外になり、canonical docsは更新されない。
- 観測点：validation report、staged artifactが存在しないこと。

### E-AC-005：Profile制御がローカルassurance所有として守られる

- 前提：`.assurance.json` / `assurance classify`でselected profileが解決済み。
- 操作：selected-profile ZIPをvalidateする。
- 期待結果：ZIPのprofile recommendationはadvisory（参考）のまま残り、authorized_profile／テンプレート選択は変更されない。
- 観測点：profile-resolution report、`.assurance.json`が変更されていないことの証跡。

### E-AC-006：選ばれたスケルトンの穴埋めがsection-mapと一致する

- 前提：ローカル`assurance compose`でskeleton hash／section inventoryが固定済み。
- 操作：ChatGPT ZIPの`drafts/issue/design.md` / `plan.md`と`section-map.json`をvalidateする。
- 期待結果：skeleton hash／section coverage／missing-section-reportが一致しないpackは**adoption対象外**。
- 観測点：profile-validation-report。

### E-AC-007：Candidate-only Epic→Issue ZIPがprofile固有テンプレートを出さない

- 前提：Epicレベルの分解（decomposition）pack。
- 操作：candidate validationを実行する。
- 期待結果：Issue候補はrequirement draft／design brief／plan brief／profile recommendation onlyを持ち、profile固有のcanonical design／planテンプレート本文を出さない。
- 観測点：candidate validation report。

### E-AC-008：Dry-run diffとstaged artifactがcanonical上書きを防ぐ

- 前提：validなZIP pack。
- 操作：提案`oracle-zip-diff` / `oracle-zip-stage`を実行する。
- 期待結果：canonicalファイルは直接変更されず、scope-localな`artifacts/`にsanitized evidenceが作成される。
- 観測点：git diff、artifact frontmatter、diff report。

### E-AC-009：Evidence Adoption Ledgerへのhandoffが可能である

- 前提：staged artifactとadoption-mapが存在する。
- 操作：main orchestratorが採否判断を記録する。
- 期待結果：adopted／partially_adopted／rejected／deferred／stale／blockedという、claim単位の台帳を`report.md`に書ける情報を持つ。
- 観測点：EAL proposal、report update candidate。

### E-AC-010：Fresh spec-reviewer gateは維持される

- 前提：ChatGPT ZIP由来のcontentをcanonical docsに採用した。
- 操作：design／planそれぞれでfresh `spec-reviewer`を実行する。
- 期待結果：ChatGPTの自己レビューやreviewer-focusはpassとして扱われず、fresh reviewerの結果だけがphase gate evidenceになる。
- 観測点：Spec Authoring Gate／reviewer evidence。

### E-AC-011：Dogfood A/B/Cが完了する

- 前提：dogfood fixture、または実際の低リスクなscope。
- 操作：Candidate-only Epic→Issue ZIP、Existing Issue selected-profile ZIP、Mismatch probeを実行する。
- 期待結果：A/Bはevidence-onlyのartifactを生成し、Cはvalidatorがstale／mismatchな配置をblockする。
- 観測点：dogfood report、validation reports、manual summary。

### E-AC-012：手動fallbackが引き続き機能する

- 前提：ChatGPT／ZIP capture／GitHub connectorが利用不可。
- 操作：ワークフローを続行する。
- 期待結果：利用不可は「劣化成功」ではなく、blocked／skipped evidenceとして残り、手動authoring pathへ戻れる。
- 観測点：report evidence、fallback summary。

---

## 8. 証跡の権限境界（artifact authority）

「これはevidenceか、canonicalか」を混同しないための一覧です。

| 区分 | 該当するもの |
|---|---|
| **Raw evidence（未採用の証拠）として扱うもの** | `epic-00283/artifacts/`配下のresearch／disc／onboarding／decision-candidate、ChatGPT ZIP pack、quarantineされた展開後ツリー、validation report、dry-run diff、adoption-map／eal-proposal、reviewer-focus／self-review、dogfood run summary |
| **Canonical authority（正本）として扱うもの** | `requirement.md`（このEpicの目的・scope・非scope・受け入れ条件・Issue seed）、`design.md`（ZIPライフサイクル・スキーマ境界・profile制御・validationアーキテクチャ）、`plan.md`（Issue分割・dogfood順序・依存グラフ・昇格基準）、accepted ADR（artifact-packの永続保存、remote reviewer gate backendなど長期判断が必要な場合）、`report.md`のEvidence Adoption Ledger（ChatGPT／ZIP／artifact evidenceの採否とstale／blocked状態） |
| **禁止事項** | 生ZIPをcanonical docsとみなすこと／artifactパスが存在するだけでadoptionとみなすこと／ChatGPT出力の自己申告をaccepted authorityとみなすこと／生transcriptをcanonical docsへ貼ること |

---

## 9. スコープ

| 区分 | 内容 |
|---|---|
| **必須（やる）** | `manual-tests/oracle-zip-authoring/`のdogfoodスクリプト／ZIP schema・JSON schema fixtures／ZIP安全intake・validation・diff・stageスクリプト／Prompt pack生成runbook／Source manifest・stale_if・denylistの取り扱い／Profile resolution snapshot・selected skeleton穴埋めのvalidation／Dogfood A/B/Cシナリオ／サニタイズされたartifact描画／`report.md`のEALproposal構造／日本語ファーストのdocs／README／prompt guidance |
| **禁止（やらない）** | 本番runtimeコマンドとして最初から公開すること／canonical docsへの直接書き込み／reviewer gateの置き換え／`.assurance.json`のChatGPTによる作成・更新／全profile分のvariant生成／Strict／Criticalのspecialist／fallback gateの省略／ZIP自己検証をローカル検証の代替にすること／secrets・tokens・cookies・本番データダンプ・個人顧客データの添付／host-local wrapper pathの本番runtimeへのハードコード |
| **対象外（このEpicの範囲外）** | provider registry／汎用oracleアダプタ／remote final reviewer gate／Deep Researchのライブ信頼性／artifact-packの永続ZIP保存契約／GitHub PR repair loop／自動Lite既定ロールアウト／既存Issue全量移行 |

---

## 10. 境界（常に／要判断／絶対にしない）

| 区分 | 内容 |
|---|---|
| **常に行う** | repo／ref／source_paths／stale_ifを記録する／ZIPはquarantineしてから検証する／ローカルのassuranceがprofile／テンプレートを決める／ChatGPTはevidence producerとして扱う／Adoptionはmain orchestratorが`report.md`に記録する／Fresh reviewer gateを維持する |
| **判断が必要（今は未確定）** | 生ZIP／展開後ツリーをリポジトリに保存する将来contract／dogfoodメトリクスが本番昇格に十分か／candidate issueのprofile recommendationとローカルclassifyが食い違った場合のsalvage policy／Strict／CriticalでChatGPT Useをnamed specialist evidenceとして扱う将来path |
| **絶対にしない** | ZIPをrepo rootやcanonical pathへ直接展開しない／ChatGPTにprofile決定を委ねない／ChatGPTにテンプレート選択を委ねない／自己レビューを`spec-reviewer`合格と表現しない／利用不可・stale・スキーマ不正を劣化成功にしない |

---

## 11. 非機能要件

| 観点 | 内容 |
|---|---|
| **信頼性／一貫性** | 同じpreflight input・source hashes・schema versionからdeterministicなvalidation結果を返す／Validationはfail-closed／source hash不一致・stale condition・schema drift・不正な権限主張はadoption対象外 |
| **セキュリティ** | ZIP inspectionは安全な展開の前に行う／denylistパスと内容を検査する／生transcript・secret・credential・token・cookie・個人情報をartifactに残さない／スクリプトらしきファイルはplain textの提案とし、実行権限を持たせない |
| **運用** | Dogfoodスクリプトはrepo-localな手動テストとして使える／ChatGPTが使えない時も手動workflowが成立する／提案コマンドはhelp／READMEでproposed／dogfood-onlyと明記する |
| **可読性** | Maintainer向けdocs／artifactsは日本語ファースト／パス・コマンド・schema key・固定のSpecDock用語は原文を保持する |
| **性能** | ZIP validationはローカルのdeterministicなプロセスとし、validation自体はネットワークアクセスを要求しない／oversizeなZIP・ファイル数・ファイルサイズの上限を持つ |

---

## 12. 依存関係／影響範囲

- **影響するcomponent**
  - `manual-tests/oracle-zip-authoring/`
  - `manual-tests/oracle-zip-authoring/schemas/`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/artifacts/`
  - `epic-00283/report.md`
  - （将来必要なら）`src/spec_dock/assets/spec_dock/docs/authoring/`のoracle evidence docs
  - （将来必要なら）`src/spec_dock/assets/install_root/.agents/skills/`のplanning skill prompt guidance

- **外部依存**
  - ChatGPT Use / GPT-5.5 Pro Extended / ブラウザ / GitHub connectorは**dogfood専用の外部依存**。
  - v1のvalidation／stagingはローカルのdeterministicなスクリプトをauthorityとする。

- **互換性**
  - 既存のSpecDockワークフローは維持する。
  - 既存の手動／delegated authoring pathを削除しない。
  - Shipped runtimeのサポートは、dogfood evidence後の後続判断とする。

---

## 13. 後続Issue seed（このEpicから生まれる予定のIssue一覧）

親requirementのtrace：E-RQ-001〜E-RQ-013。acceptance seed：E-AC-001〜E-AC-012。

各Issueが「どの要件（E-RQ）」と「どの受け入れ条件（E-AC）」をcloseする予定かをまとめると次の通りです（原文の`closes:`を集約したもの）。

| Issue名 | 目的 | closes（RQ） | closes（AC） | grade案 |
|---|---|---|---|---|
| Dogfood Oracle ZIP Authoring Preflight And Prompt Pack | repo/ref/source_paths/stale_if/denylist/profile snapshotを固定し、ChatGPT ZIP生成用のprompt packを作る | RQ-001, RQ-002, RQ-003 | AC-001 | strict |
| Implement Safe ZIP Intake And Schema Validation | ZIPのcentral-directory inspection、安全展開、path/content拒否、manifest/provenance/schema検証をdogfoodスクリプトとして作る | RQ-004, RQ-005 | AC-002, AC-003, AC-004 | strict |
| Implement Oracle ZIP Diff And Staged Artifact Rendering | validなZIPをcanonical上書きなしでdry-run diffし、scope-localなsanitized Markdown evidenceへstageする | RQ-006, RQ-007 | AC-008, AC-009 | strict |
| Implement Profile Controlled Selected Skeleton Fill Validation | ローカルassuranceのprofile resolution、template hash、section inventory、section-map、missing-section-reportを照合する | RQ-008, RQ-009 | AC-005, AC-006 | strict |
| Dogfood Candidate Only Epic To Issue ZIP Pack | Epicレベルのzipで複数Issue候補を出し、profile recommendation only／profile固有テンプレート非生成を検証する | RQ-011 | AC-007, AC-011 | standard |
| Dogfood Existing Issue Selected Profile ZIP Pack | レビュー済みIssue requirementから、ローカルassurance composeで作った済みskeletonをChatGPTに埋めさせ、staged adoption flowを検証する | RQ-008, RQ-009, RQ-010 | AC-005, AC-006, AC-010, AC-011 | strict |
| Dogfood ZIP Mismatch And Stale Probe | staleなprofile_resolution、profile mismatch、source hash mismatch、不正な権限主張をvalidatorがblockできることを検証する | RQ-005, RQ-008, RQ-010 | AC-002, AC-004, AC-005, AC-011 | strict |
| Document ZIP Authoring Pack Workflow And Adoption Ledger Examples | dogfood専用README、prompt規則、権限境界、EAL例、手動fallback規則を日本語ファーストで整備する | RQ-007, RQ-012, RQ-013 | AC-009, AC-012 | standard |
| Evaluate Dogfood Metrics And Runtime Promotion Criteria | adoption比率、validation失敗率、reviewer手戻り回数、人間の編集負担、fallback成功率を集計し、本番昇格／保留／却下を判断する材料を作る | RQ-011, RQ-013 | AC-011, AC-012 | standard |

**許可されているlocal delta**：dogfoodスクリプト名／schema詳細／fixture形状／report formatの具体化。

**触ってはいけない親の境界**：ChatGPTのauthority化、reviewer gateの置き換え、profile authorityの委譲、canonicalへの直接書き込み。

**期待されるevidence**：preflight JSON、validation report、dry-run diff、staged artifact、dogfood report、EAL proposal、manual fallback summary。

---

## 14. 未確定事項

- **Blocking question（今のままだと進めない問い）**：なし。
- **Non-blocking design questions（今後詰める設計上の論点）**
  - 生ZIP／展開後ツリーをリポジトリ外quarantineのみに残すか、将来artifact-packとしてリポジトリに保存するか。
  - 本番昇格（runtime promotion）の測定閾値。
  - Candidate profileのrecommendationとローカルclassifyが食い違った場合のsalvage policy。
  - ChatGPT UseをStrict／Criticalのnamed specialist evidenceとして扱う将来path。

---

## 付録：原文との対応

この資料はセクションの順序・見出しの粒度を読みやすさのために再構成していますが、次の対応で原文の**すべての項目**を含んでいます。

| 本資料の章 | 原文（`requirement.md`）の見出し |
|---|---|
| 2 | 目的（Initiativeとの紐づき）／背景とWhy now |
| 3 | 能力／モデルenvelope（capability / model envelope） |
| 4 | （新規追加：ライフサイクル図。原文の正常系ユースケースを図として再構成） |
| 5 | ユースケース |
| 6 | エピック要件（Epic requirements） |
| 7 | エピック受け入れ条件（Epic acceptance criteria） |
| 8 | 証跡の権限境界（artifact authority） |
| 9 | スコープ |
| 10 | 境界 |
| 11 | 非機能要件 |
| 12 | 依存／影響範囲 |
| 13 | 後続Issue seed |
| 14 | 未確定事項 |

原文のfront matter（種別、ID、タイトル、関連GitHub、状態、作成者、最終更新、親）はこの資料には転記していません。必ず[`../requirement.md`](../requirement.md)の1〜10行目を参照してください。
