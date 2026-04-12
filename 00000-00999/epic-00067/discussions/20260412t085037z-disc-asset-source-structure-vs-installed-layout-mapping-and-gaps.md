---
種別: disc
ID: "20260412t085037z-disc"
タイトル: "asset source structure vs installed layout mapping and gaps"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-12"
親: ["epic-00067"]
関連: []
---

# 20260412t085037z-disc asset source structure vs installed layout mapping and gaps

## 議題
- spec-dock の provider-side asset 構造を、実際の導入先ディレクトリ構造と対応する形に整理する。
- `.agents` 配下の共通スキル、`.codex` 配下の Codex 用設定、`.github` 配下の GitHub Copilot 用設定を、同じ設計原則で扱えるようにする。
- 既存の asset 配置が「実際の install 後の姿」をそのまま表していないため、source tree と installed tree の対応を明確にする。

## 背景
- 現状の provider-side assets は `src/spec_dock/assets/codex_skills/...` と `src/spec_dock/assets/spec_dock/...` に分かれているが、実際の導入先は `.agents/skills`、`.agents/host-adapters`、`.codex/agents`、`.github/agents`、`.github/workflows` に分散している。
- そのため、source 側のディレクトリ構造だけを見ても、どのファイルがどの install 先に対応するのかが直感的に追いづらい。
- スキル自体は `.agents/skills` に集約し、host 固有の agent / shim / workflow / 初期設定は `.codex` と `.github` に分離して整理したい。
- 目的は、インストール時の変換処理を複雑化することではなく、provider-side の assets を「実際の install 後の構造を保った正本」に寄せることにある。

## As-Is
- provider-side の source は、実装都合でまとまったディレクトリに置かれており、installed layout と 1 対 1 で見比べにくい。
- たとえば、Codex / Copilot の host-native agent 由来のファイルと、共通スキルや host adapter の資産が同じ束として見えやすく、役割の境界が曖昧になっている。
- GitHub workflows を含む周辺資産も、導入先の構造と source 側の構造が完全には一致していない。
- その結果、「何が共通資産で、何が host 固有資産で、何が installer の変換対象か」が読み取りづらい。

## To-Be
- source 側に、実際の install 後のディレクトリ構造を意識した root を用意し、その配下に共通資産と host 固有資産を対応づけて置く。
- 共通スキルは `.agents/skills`、共通メタデータは `.agents/host-adapters`、Codex 固有は `.codex/agents`、GitHub Copilot 固有は `.github/agents`、GitHub workflows は `.github/workflows` のように、導入先の構造を保ったまま管理する。
- installer は複雑な変換器ではなく、基本的には構造を保ったまま asset を写す役割に寄せる。
- Claude Code は将来的な拡張候補として残すが、この epic では本格導入対象にしない。

## ユーザー確認結果
- Q1: yes。install 後構造に対応する仮想ルートを source 側に新設する方針を採用する。
- Q2: yes。`.agents` は共有資産、`.codex` は Codex 固有、`.github` は GitHub 固有として分離する。
- Q3: yes。GitHub workflows も `.github` にまとめる方向で整理する。
- Q4: yes。Claude Code は今回は非対象だが、後続で拡張しやすい構造を前提にする。
- Q5: yes。installer は最小変換に留め、構造を保持したまま同期する。

## 既存 epic ではなく新規 epic にした理由
- これは単一の asset 追加ではなく、provider-side source layout、install layout、installer の同期方針、host 別の責務分離をまたぐ構造課題だから。
- 既存 epic の背骨に押し込むと、別テーマの契約や rollout 順と混ざってしまい、設計の焦点がぼやける。
- 今回の論点は「どの issue をどう直すか」よりも、「assets の正本構造をどう切るか」という architecture-level の整理にある。
- そのため、architecture initiative 配下に新規 epic を立て、以後の requirement / design / plan をこの構造契約に合わせて展開するのが妥当。

## 主な調査観点
- provider-side の正本をどこに置くか。
- install 後のディレクトリ構造を source 側にどこまで忠実に写すか。
- `.agents` の共通資産と `.codex` / `.github` の host 固有資産をどう分離するか。
- GitHub workflows を同じ asset 契約で扱うか、別の契約として分けるか。
- installer が「コピー」なのか「変換」なのかをどこまで厳密に定義するか。
- 今後 Claude Code を追加する場合に、今回の構造がそのまま拡張しやすいか。

## Out-of-scope 仮置き
- Claude Code の本格導入は後続扱いにする。
- 今回は requirement / design / plan の本格起草までは行わない。
- host ごとの実装詳細や runtime の再設計は、この discussion では扱わない。
- GitHub workflow の個別ロジック変更は、必要なら別 issue で切り出す前提にする。

## 次の設計で決める点
- source 側の root 名と配置をどうするか。
- 共通資産と host 固有資産を source tree でどう見せるか。
- GitHub workflows を `.github` 配下でどこまで共通契約として管理するか。
- installer の例外ケースをどこまで許容し、どこから manifest 化するか。
- 今回の構造を Claude Code 用の拡張点へどう接続するか。

## 次アクション
- 認識が揃ったため、次は epic 直下の requirement / design / plan に構造契約を落とし込む。
- その前に、source tree と installed tree の inventory を research doc で固定して、設計の前提をブレなくする。
- その後、assets の source tree と installer の同期方針を一致させる issue 分割へ進む。
