---
種別: 要件定義書（Initiative）
ID: "init-local-00003"
タイトル: "Architecture Maintenance and Hardening"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-27"
---

# init-local-00003 Architecture Maintenance and Hardening — 要件定義（WHAT / WHY）

## 目的（Outcome）
- Primary:
  - `spec-dock` の継続開発を支える architecture maintenance / governance / hardening の受け皿を、open-ended initiative として運用する。
  - source-of-truth、identity、sync、naming、state boundary など、構造的な architecture issue を継続的に取り込み、epic / issue として分解できる状態を維持する。
- Secondary:
  - feature expansion と architecture cleanup の backlog を混線させず、architecture concern を独立した投資単位として管理する。
  - 当面の milestone として、`spec-dock` を「ちゃんと使える状態」に到達させる。

## initiative の定義
- この initiative は open-ended である。
- 将来見つかる architecture issue を継続的に受け入れる。
- ただし無制限に scope を広げるのではなく、「構造健全性」「運用可能性」「dogfooding 継続性」に関わる論点だけを取り込む。
- feature value の拡張、operator-facing feature、product surface の拡張は別 initiative に置く。

## 背景と Why now
- 現状の課題:
  - 現在の dogfooding workspace は旧 contract を前提にしており、今回の identity / naming / sync contract 変更で壊れる前提になる。
  - 一方で、その旧 workspace を無理に延命することは architecture cleanup の足かせになる。
  - node identity の GitHub mandatory 化、local-only 廃止、discussion / ADR の timestamp naming、ADR mirror sync などは、現在の runtime / docs / tests 全体にまたがる基盤変更である。
- 方針:
  - 現在の古い dogfooding workspace は放棄してよく、後で新しい workspace を再構築してからデータ移し替えする。
  - したがって、今回は無理に後方互換性を維持しない。
  - initiative / epic planning docs 自体は current legacy workspace 上の artifact として一時的に `*-local-*` path に存在しうるが、これは runtime policy の例外ではなく、再構築までの planning container とみなす。
- なぜ今やるか:
  - いま contract を揃えないと、今後の epic / issue 運用そのものが local collision と stale contract を抱え続ける。
  - single GitHub repo 前提に寄せるなら、早い段階で identity policy を固定したほうが実装の手戻りが小さい。

## 成功指標
- Metric-001:
  - Baseline:
    - architecture issue の受け皿はあるが、open-ended initiative としての運用方針が明文化されていない。
  - Target:
    - architecture issue を継続的に取り込む initiative definition と epic portfolio が docs に固定されている。
  - 計測方法:
    - initiative requirement / design / plan が open-ended initiative として整合していること。
- Metric-002:
  - Baseline:
    - node identity、doc naming、sync-generated views の contract が旧 dogfooding workspace に引きずられている。
  - Target:
    - GitHub-backed identity と ADR mirror workflow を扱う epic が起票され、issue 分解まで完了している。
  - 計測方法:
    - 対象 epic の requirement / design / plan が存在し、実装 issue が定義されていること。
- Metric-003:
  - Baseline:
    - backward compatibility を守るべきかどうかが曖昧で、cleanup の強度を決めにくい。
  - Target:
    - 「旧 workspace は再構築前提」「無理に後方互換を維持しない」が明記されている。
  - 計測方法:
    - initiative / epic docs に移行前提が明記されていること。

## スコープ
- MUST:
  - architecture issue を継続的に受け入れる open-ended initiative として運用定義を固定する。
  - source-of-truth、identity、sync、naming、state boundary の architecture concern を扱う。
  - single GitHub repo 前提の contract を扱う。
  - dogfooding workspace の再構築前提と、後方互換を無理に維持しない前提を明記する。
- MUST NOT:
  - feature value 拡張の受け皿にしない。
  - temporary workaround を architecture goal と誤認しない。
  - 旧 workspace の延命をこの initiative の目的にしない。
- OUT OF SCOPE:
  - feature backlog
  - 外部連携や multi-repo strategy
  - user-facing feature expansion

## 境界
- Always:
  - architecture initiative は open-ended だが、architecture concern だけを受け入れる。
  - source-of-truth を曖昧にしない。
  - backward compatibility より、使える新 contract を優先する。
- Ask:
  - その課題は architecture contract の問題か、feature 要求か。
  - その変更は docs で閉じるか、runtime / scaffold 実装変更まで必要か。
- Never:
  - 旧 dogfooding workspace の保守を優先して architecture cleanup を止めること。
  - cross-repo 前提を持ち込むこと。

## ステークホルダー / 影響範囲
- 利用者:
  - `spec-dock` を同一 product repo に組み込んで運用する coding agent / maintainer
- 運用者:
  - dogfooding workspace を再構築し、後からデータ移し替えを行う maintainer
- 影響システム / 領域:
  - `src/spec_dock/`
  - `spec-dock/`
  - `tests/`

## 非交渉制約
- single GitHub repo 前提で進める。
- initiative / epic / issue は GitHub issue mandatory とする。
- local-only は完全廃止する。
- discussion / ADR は timestamp-prefix naming へ移行する。
- `spec-dock/adrs/` は sync 再生成の symlink mirror のみとする。

## リスク / 依存
- R-001:
  - open-ended を理由に scope が無制限化する。
- R-002:
  - backward compatibility を切る前提が曖昧だと、変更強度が中途半端になる。
- R-003:
  - dogfooding workspace 再構築の手順が曖昧だと、移行時に混乱する。
- D-001:
  - 新 contract を受け入れる epic / issue 分解が先に必要。

## 未確定事項
- Q-001:
  - 質問:
    - dogfooding workspace の再構築手順を別 epic/issue として切るか、各 epic 内で局所対応するか。
  - 選択肢:
    - A:
      - 各 epic 内で局所対応
    - B:
      - 再構築専用 epic / issue を持つ
  - 推奨案:
    - A。まずは各 epic の rollout boundary に閉じ込める。
  - 影響範囲:
    - migration / rollout planning
