---
種別: 要件定義書（Epic）
ID: "epic-00283"
タイトル: "ChatGPT ZIP 仕様作成パック自動化"
関連GitHub: ["#283"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["init-local-00003"]
---

# epic-00283 ChatGPT ZIP 仕様作成パック自動化 — 要件定義（何を、なぜ行うか）

## 目的

この Epic は、ChatGPT Use / GPT-5.5 Pro Extended が生成する ZIP 形式の仕様作成パックを、SpecDock の正本ではなく「未信頼の証跡」として安全に受け取り、検証し、採用候補へ変換する仕組みを作る。

狙いは、ChatGPT の長文・複数ファイル生成能力を活用しながら、SpecDock 側の正本、プロファイル決定権、レビュアーゲート、Git / ファイルシステム上の事実確認を維持することである。

この Epic では、次のことを行う。

- Epic の要件定義書から、Epic 設計書、Epic 計画書、複数 Issue のドラフト要件・ドラフト設計・ドラフト実装計画をまとめて受け取れる形を検証する。
- ZIP の安全な受け入れ、スキーマ検証、ソース検証、期限切れ判定、危険な権威主張の検出、段階配置、採否判断の流れを定義する。
- Issue のグレード / プロファイルは ChatGPT に決定させず、ローカルの `assurance classify` と `.assurance.json` を権威として扱う。
- ChatGPT のセルフレビューやレビュアー注目点は、正式な `spec-reviewer` 通過として扱わない。

## 背景

これまでの調査と実験により、ChatGPT Use は SpecDock の高度分析、設計案、計画案、Issue 分割、レビュアー観点、ZIP による複数ファイル出力に有効であることが分かった。

一方で、ChatGPT はローカルの未追跡ファイル、最新の Git 状態、テンプレートハッシュ、`.assurance.json`、テスト実行結果、独立したレビュアー判定を保証できない。したがって、ChatGPT 出力をそのまま正本やレビュアー通過として扱うと、SpecDock の権威境界が崩れる。

そのため、この Epic では `scripts/authoring-pack/` 配下のドッグフード専用スクリプト群として開始し、配布ランタイムへの昇格は後続判断に残す。`manual-tests/` は tracked workspace / fixture / evidence を置かない既存方針を維持する。

## 不変条件

- ZIP 生成は正本昇格ではない。`bundle_generation_not_promotion: true` を守る。
- ZIP、ChatGPT transcript、調査レポート、検証レポートは採用前の証跡である。
- 正本は、採用済みの `requirement.md` / `design.md` / `plan.md`、承認済み ADR、または `report.md` の Evidence Adoption Ledger / Spec Authoring Gate に限る。
- ChatGPT はプロファイルを推奨できるが、`authorized_profile` は決めない。
- `assurance compose` が選択済みスケルトンを作り、ChatGPT は与えられたセクションだけを記入する。
- ZIP はリポジトリへ直接展開しない。必ずリポジトリ外の隔離領域で検査する。
- 正本ファイルへの直接上書きは禁止する。採用は差分確認と台帳記録を通す。
- 各フェーズの正本昇格には fresh `spec-reviewer` が必要である。

## 対象範囲

- 事前確認: 対象リポジトリ、ブランチ、ソースファイル、ハッシュ、期限切れ条件、プロファイル状態を固定する。
- プロンプトパック生成: ChatGPT に渡す権威境界、出力スキーマ、禁止事項、ZIP ルート、採用条件を明示する。
- ZIP 受け入れ: central directory を先に検査し、危険なパスやファイル種別を拒否する。
- スキーマ検証: `manifest.json`、`provenance.json`、`stale-if.json`、`adoption/adoption-map.json` などを確認する。
- 段階配置: 正本を変更せず、検証済みの証跡だけをスコープ内 `artifacts/` または Issue local artifact へ置く。
- 採用台帳: 採用、部分採用、却下、保留、期限切れ、ブロックを `report.md` に記録できるようにする。
- ドッグフード: Epic から Issue 候補を作るケース、既存 Issue の選択済みプロファイルを埋めるケース、不一致・期限切れをブロックするケースを確認する。

## 対象外

- `spec-reviewer`、`code-reviewer`、`qa-reviewer` の置換。
- 配布ランタイムコマンドとしての即時提供。
- ChatGPT による `.assurance.json` の作成・更新。
- ChatGPT による全プロファイル分のテンプレート生成。
- raw ZIP / 展開済みツリーを正本 artifact として保存する契約。
- GitHub PR レビュー、マージ準備、自動修正の置換。

## 要件

- E-RQ-001: 初期実装は `scripts/authoring-pack/` のドッグフード専用スクリプトとして扱い、tracked fixture は `tests/fixtures/authoring_pack/` に置く。`manual-tests/` には tracked workspace / fixture / evidence を追加しない。
- E-RQ-002: 事前確認では repo、ref、source_paths、source_hashes、denylist、stale_if、profile state を記録する。
- E-RQ-003: プロンプトは ZIP スキーマ、権威境界、プロファイル制御、禁止主張、出力ルートを明記する。
- E-RQ-004: ZIP は単一 root `specdock-authoring-pack/` を持ち、必須メタデータと採用マップを含む。
- E-RQ-005: ZIP は安全検査後にのみ展開し、危険なパス、隠しパス、リンク、バイナリ、ネスト archive、秘密情報を拒否する。
- E-RQ-006: ZIP 内容は正本へ直接配置せず、ドライラン差分と段階配置を経由する。
- E-RQ-007: 採用判断は claim 単位で Evidence Adoption Ledger に記録できる。
- E-RQ-008: Issue プロファイルはローカル assurance が決める。ChatGPT の推奨は証跡に留める。
- E-RQ-009: 選択済みスケルトン記入では、テンプレートハッシュ、セクション一覧、セクション対応表、未記入セクション報告を検証する。
- E-RQ-010: 要件、設計、計画が ZIP に同梱されても、正本採用は段階的に行う。
- E-RQ-011: A/B/C のドッグフードシナリオと、失敗率、採用率、手直し量、レビュアー修正ループ数を測定する。
- E-RQ-012: ChatGPT / browser / GitHub connector / ZIP 生成が使えない場合も、既存の手動仕様作成フローを継続できる。
- E-RQ-013: ランタイム昇格は、この Epic の結果を見た後続 Issue / ADR で判断する。

## 受け入れ条件

- E-AC-001: 事前確認が repo / branch / source manifest / stale_if を固定して出力できる。
- E-AC-002: 危険な ZIP fixture が安全展開前に拒否され、正本や artifact に副作用を出さない。
- E-AC-003: 必須 manifest / provenance / adoption map が欠落した pack を採用不能にできる。
- E-AC-004: `adoption_status: adopted` や reviewer pass などの危険な権威主張をブロックできる。
- E-AC-005: ChatGPT のプロファイル推奨によって `.assurance.json` や authorized profile が変わらない。
- E-AC-006: 選択済みスケルトン記入が section-map と一致しない場合に採用不能にできる。
- E-AC-007: Epic から Issue 候補を作る pack は、プロファイル別の正本テンプレート本文を出さない。
- E-AC-008: valid pack からドライラン差分と段階配置 artifact を作れても、正本を直接上書きしない。
- E-AC-009: adoption-map から Evidence Adoption Ledger の候補を作れる。
- E-AC-010: セルフレビューやレビュアー注目点が `spec-reviewer` pass として扱われない。
- E-AC-011: A/B/C のドッグフードシナリオが実施され、成功・失敗・ブロック理由が記録される。
- E-AC-012: 結果から、ランタイム昇格、保留、却下の判断材料を作れる。

## Issue 分割の前提

- ZIP 受け入れ、安全検証、プロファイル制御に関わる Issue は `strict` 相当で扱う。
- 文書化、プロンプト、測定、レポートに関わる Issue は `standard` 相当で扱う。
- ただし最終的な `authorized_profile` は各 Issue のローカル assurance が決める。
