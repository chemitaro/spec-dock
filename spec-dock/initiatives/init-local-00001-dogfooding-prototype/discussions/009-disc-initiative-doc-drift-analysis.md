---
種別: disc
ID: "009-disc"
タイトル: "Initiative Docs Drift Analysis Before Refresh"
状態: "open"
作成者: "Codex CLI"
最終更新: "2026-03-25"
親: ["init-local-00001"]
関連: [
  "../requirement.md",
  "../design.md",
  "../plan.md",
  "004-adr-runtime-cli-layered-architecture.md",
  "005-disc-review-loop-and-outcome-matrix-lessons.md",
  "006-disc-repo-scope-and-create-state-lessons.md",
  "007-disc-manual-rerun-current-state.md",
  "008-note-spec-deps-curation-log.md"
]
---

# 009-disc Initiative Docs Drift Analysis Before Refresh

## 目的
- 2026-03-14 時点で作成した initiative の `requirement.md` / `design.md` / `plan.md` が、現在の実装状況とどこでずれているかを先に可視化する。
- いきなり initiative 正本を更新するのではなく、何を更新し、何を維持するかの叩き台を作る。
- issue-28 の一時的な corrective trace を再演せず、initiative レベルの durable な変化だけを抽出する。

## 対象文書
- current initiative docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
- durable discussion / ADR:
  - `004-adr-runtime-cli-layered-architecture.md`
  - `005-disc-review-loop-and-outcome-matrix-lessons.md`
  - `006-disc-repo-scope-and-create-state-lessons.md`
  - `007-disc-manual-rerun-current-state.md`

## 2026-03-14 時点の前提

### requirement の前提
- dogfooding prototype はまだ roadmap 固定の段階であり、主要成果は「product backlog の中核テーマを定めること」にある。
- 中心テーマは `status lifecycle`、`link/unlink`、`machine-readable status contract`、`doctor/dry-run/explain`、repo-safe GitHub mutation である。
- prototype はまだ不安定で、dogfooding から課題を投入し続けること自体が主要スコープである。

### design の前提
- hybrid layered architecture は狙いとして書かれているが、実装として十分に固定されたものではなく、段階導入の守るべき方針として置かれている。
- `status contract -> local mutation -> authority transfer -> remote mutation -> diagnostics` が主たる staged rollout とされている。
- repo-safe preflight、projection/cache と authority の分離、stale の可視化が、これから整備する guardrail として書かれている。

### plan の前提
- Epic は将来 roadmap の束ねとして置かれており、まだ実装済み capability の棚卸しよりも「これから分割できること」を重視している。
- `status and authority foundation`、`link and github lifecycle`、`operability and diagnostics`、`discovery and hardening` の 4-epic で prototype completion までを見通す構成になっている。
- milestone の出口も、実装達成というより issue 分割 readiness に寄っている。

## 現在の実装・運用 reality

### 1. prototype は「これから始める」段階ではなく、主要 blocker を潰して使える段階に入っている
- `007-disc-manual-rerun-current-state.md` が示す通り、current runtime は major path で利用可能と判断できる状態まで来ている。
- overlap 環境でも canonical URL と `--id` による exact resolution は成立している。
- no-origin 下でも already-normalized metadata は continuity を保つ。
- stale active recovery、readonly `.meta.json` non-mutation、checked-in parity は実運用観点で再確認済みである。

### 2. dogfooding で見つかった blocker は、抽象 roadmap ではなく具体的 runtime contract としてかなり収束した
- `doctor` は将来施策ではなく、すでに surface として成立している。
- create/import/sync/validate/active/deps の failure guidance も、issue 単位の補修を経てかなり実装済みである。
- provider-side / checked-in runtime parity は、重要な guardrail として実装・検証済みの前提になっている。

### 3. repo-scope / legacy metadata / no-origin continuity は、単なる future concern ではなく現在の運用 contract になった
- `006-disc-repo-scope-and-create-state-lessons.md` と `007-disc-manual-rerun-current-state.md` に沿って、現在は「危険な自動補完より fail-closed を優先する」方針が確定している。
- legacy unscoped current-repo link は、自動 self-heal ではなく manual remediation 別スコープとして整理された。
- overlap-heavy workspace では bare numeric selector を convenience ではなく hazard とみなす前提が明確になった。

### 4. architecture は aspirational ではなく accepted design に近づいた
- `004-adr-runtime-cli-layered-architecture.md` によって、hybrid layered architecture は initiative の方向性メモではなく durable decision として読むべき状態になっている。
- `005-disc-review-loop-and-outcome-matrix-lessons.md` は、review loop の原因が単発 bug ではなく outcome matrix 不足と parity drift にあったことを示している。
- つまり現在の設計論点は「どの機能を足すか」だけでなく、「contract をどう閉じるか」「provider/check-in parity をどう維持するか」に重心が移っている。

## 文書ごとの主なズレ

### requirement のズレ
- 現在の requirement は roadmap 宣言としては妥当だが、prototype がすでに到達した成果を反映できていない。
- `doctor`、repo-safe preflight、repo-aware targeting、checked-in parity discipline が「scope に含める予定」のように読めるが、現状はすでに product contract の一部になっている。
- `status lifecycle` と `link lifecycle` が中心テーマであること自体は妥当だが、実際の課題は create state、repo scope、manual remediation、operator guidance まで広がっている。
- success 指標が readiness 寄りで、usable dogfooding runtime に到達した事実を表現していない。

### design のズレ
- staged rollout の順序は大筋で有効だが、現在の設計上の主要 guardrail である outcome matrix、checked-in parity、fail-closed selector contract、manual remediation 境界が明文化されていない。
- `artifact は projection/cache` の原則は残すべきだが、現在は `.meta.json` や active manifest の recovery/non-mutation contract まで具体化されているため、設計の粒度が足りない。
- `repo-safe preflight` と `diagnostics` は future principle ではなく、設計済み capability として位置づけ直す必要がある。

### plan のズレ
- 4-epic 構成は大枠の整理としては有効だが、現状の実装済み領域と remaining work の境界が不明瞭である。
- Epic 3 `operability and diagnostics` は多くが「これから」ではなく「すでに一部成立」に変わっている。
- Epic 4 `discovery and hardening` も、hardening の一部は issue-28 corrective scopes で前倒し実装されている。
- plan は readiness based な書き方なので、現在の「何が done で、何が remaining か」を読めない。

## 逆に、維持すべき前提
- `spec-dock` 自身を `spec-dock` で dogfooding する、という initiative の目的。
- provider/source と generated workspace の責務分離。
- `1 issue = 1 authority`、artifact は authority ではなく projection/cache とみなす原則。
- additive migration と fail-safe / fail-closed を優先する姿勢。
- prototype 完成後の extras は別 initiative / epic へ切り出す、という境界。

## 現在の initiative-level 論点

### 論点 1: initiative の成功条件を readiness から usability へ寄せ直すか
- 現状:
  - requirement / plan は「roadmap と epic が切れること」を強く評価している。
- 変更要因:
  - manual rerun により、主要 path の usability が確認された。
- 更新示唆:
  - success 指標と milestone exit に「usable runtime / validated dogfooding path」を入れるべき。

### 論点 2: diagnostics を future scope ではなく established capability として再配置するか
- 現状:
  - `doctor`、failure guidance、recovery は plan 上で将来テーマ寄りに見える。
- 変更要因:
  - 実装済みかつ manual rerun でも確認済み。
- 更新示唆:
  - plan では done / ongoing / remaining を分ける必要がある。

### 論点 3: repo-scope / no-origin / legacy metadata を initiative の恒久テーマとして昇格するか
- 現状:
  - GitHub mutation や link/unlink の一部論点として散っている。
- 変更要因:
  - repo-aware exact resolution、fail-closed numeric ambiguity、manual remediation 境界が durable lesson になった。
- 更新示唆:
  - requirement/design に operator guidance と manual remediation gap を反映すべき。

### 論点 4: checked-in parity を explicit guardrail にするか
- 現状:
  - provider/source と consumer/generated workspace の分離はあるが、checked-in parity discipline は plan 上で弱い。
- 変更要因:
  - repeated review loop の重要原因として parity drift が確認された。
- 更新示唆:
  - design / plan に parity maintenance を guardrail / verification として明記すべき。

## requirement/design/plan 更新の叩き台

### requirement で見直しが必要そうな点
- prototype の現在地を「roadmap planning phase」から「usable dogfooding runtime with caveats」へ更新する。
- scope に、repo-scope exact resolution、fail-closed selector behavior、checked-in parity、manual remediation gap を追加する。
- success 指標を readiness 偏重から、実利用 path の成立と durable guidance へ寄せる。

### design で見直しが必要そうな点
- current guardrail として次を明文化する:
  - outcome matrix closure
  - checked-in parity discipline
  - repo-aware exact targeting
  - fail-closed ambiguity
  - no-origin continuity for normalized metadata
  - legacy unscoped metadata は auto-heal しない
- diagnostics / recovery を principle ではなく established design surface として書き直す。

### plan で見直しが必要そうな点
- 4-epic 構成自体は維持候補だが、各 epic に対して:
  - already done
  - validated in manual rerun
  - remaining follow-up
  を分けて書くべき。
- Epic 3 と Epic 4 は、diagnostics/hardening の一部完了を反映する必要がある。
- follow-up は「さらなる自動化」ではなく、manual remediation / operator guidance / remaining discovery に寄せ直すのが妥当である。

## 推奨 narrative
- この initiative は、当初の「dogfooding prototype を成立させるための roadmap 定義」フェーズを越えた。
- 現在は、主要 runtime contract を実装・補修・manual rerun で再確認し、「使えるが caveat を伴う prototype」へ移行した段階にある。
- したがって、initiative 正本の次の更新では、将来計画だけを語るのではなく、すでに成立した contract と残課題の境界を明確化するべきである。
- 残課題の中心は、根本的な correctness bug ではなく、manual remediation、operator guidance、remaining hardening の整流にある。

## 次にやること
- この discussion を正本として、initiative の `requirement.md` / `design.md` / `plan.md` を refresh する。
- refresh では issue-28 の細かい corrective history は入れず、durable lesson と current contract だけを initiative 文書へ昇格する。
