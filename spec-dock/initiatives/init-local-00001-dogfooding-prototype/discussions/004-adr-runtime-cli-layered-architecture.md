---
種別: ADR（Architecture Decision Record）
ID: "004-adr"
タイトル: "Runtime Cli Layered Architecture"
状態: "accepted"
作成者: "Codex CLI"
最終更新: "2026-03-25"
親: ["init-local-00001"]
関連: [
  "001-adr-adopt-dogfooding.md",
  "002-adr-agentic-cli-roadmap.md"
]
---

# 004-adr Runtime Cli Layered Architecture

## 目的
- `spec-deps` で一時管理していた設計判断のうち、現在も陳腐化していないものを initiative 側へ残す。
- とくに runtime CLI の責務分割は、今後の dogfooding や corrective patch の前提になるため、継続参照できる形で保持する。

## 結論
- runtime CLI は `commands / application / domain / infra / presentation` の hybrid layered architecture を維持する。
- user-facing entrypoint は command を保つが、第一級の設計境界は command 単位ではなく layer 単位に置く。
- orchestration は `application`、不変条件と core rule は `domain`、外部接続は `infra`、出力整形は `presentation` に置く。
- corrective patch を入れるときも monolithic command file へ逆戻りさせない。

## 背景
- 旧 monolithic runtime では、CLI dispatch、tree scan、deps、active、Git/GitHub、rendering が近接し、変更の影響範囲が大きかった。
- dogfooding 中に見つかった回帰の多くは、単純なロジック不備だけでなく、責務境界が曖昧なまま corrective patch が積み上がったことでも増幅された。
- 現在の shipped runtime 構造と test layout はこの layered 方針に整合している。

## この判断を残す理由
- 今後の feature 追加や bugfix で、短期的な convenience から command file へロジックを戻す誘惑がある。
- しかし dogfooding repo では provider/runtime と generated workspace の parity も管理対象であり、境界崩れは review loop と parity drift を招きやすい。
- そのため、この判断は historical note ではなく current guardrail として残す価値がある。

## 具体的な guardrail
- CLI bootstrap / parser / dispatch は `cli` または `commands` にとどめる。
- workflow ごとの判断、selector 解決、sync orchestration は `application` に寄せる。
- status/readiness/deps/active などの core rule は `domain` に寄せる。
- filesystem、git、github、active store、artifact write は `infra` に寄せる。
- markdown/json/puml/terminal surface は `presentation` に寄せる。

## 非目標
- pure domain-first へ振り切ること。
- command-first の薄い分割だけで設計改善したとみなすこと。

## 移設メモ
- 本 ADR は `spec-deps/current/adrs/adr-001-runtime-cli-layered-architecture.md` の durable な結論を initiative discussion に移したものである。
- 旧 `spec-deps` の削除後も、この initiative 側を継続参照の正本とする。
