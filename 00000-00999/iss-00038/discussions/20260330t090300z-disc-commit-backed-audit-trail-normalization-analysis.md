# Commit Backed Audit Trail Normalization Analysis

## 対象の問題
- epic-level spec review finding:
  - `iss-00038/report.md` の S06 corrective update が `working tree` only と記録され、committed branch-diff review の監査証跡になっていない。

## 現在の状態
- S06 は spec reviewer の initial fail と follow-up pass を記録している。
- しかし S06 のコミット欄は `なし（working tree 上の corrective report update）` のまま。
- 一方で plan の final quality gate は `git diff <base>...HEAD` を対象にしている。

## あるべき状態
- branch-diff review に使う evidence は committed history から再現できること。
- `report.md` の commit 欄は、actual commit hash か、真に diff がない no-op のどちらかで説明できること。

## ギャップ
- S05 では commit normalization を行ったが、S06 自体の commit-backed auditability までは contract 化されていない。
- working-tree review を許してしまうと、branch-diff spec review で artifact を根拠にできない。

## 修正案
- Option A:
  - 実装時に S06 commit 欄だけ actual hash へ差し替える。
  - 長所:
    - 最短。
  - 短所:
    - 再発防止の contract が残らない。
- Option B:
  - requirement/design/plan に「review gate に使う doc change は commit 済みであること。no-op は diff ゼロ時のみ」と追加し、S06 は actual commit を記録する。
  - 長所:
    - 再発防止になる。
    - branch-diff review の前提と一致する。
  - 短所:
    - issue docs の corrective scope が少し増える。
- Option C:
  - working-tree review をそのまま許容し、committed branch-diff review では補足説明で逃がす。
  - 長所:
    - 追加作業が少ない。
  - 短所:
    - 監査性が壊れるので非推奨。

## consultant の客観分析
- consultant 観点では、重要なのは「各 step ごとの separate commit」ではなく「branch-diff evidence に入る変更が actual commit から追えること」。
- したがって contract 側に committed-audit-trail rule を追加した上で、実装時に S06 hash を記録するのが最も安定。

## 推奨案
- Best practice:
  - Option B
- 理由:
  - 今回の finding だけでなく、今後の corrective review でも同じ問題を防げる。
  - `report artifact normalization` を S04/S05 に限定せず、branch-diff review quality gate まで接続できる。

## 実装計画への反映ポイント
- plan に committed audit-trail normalization step を追加する。
- final exit contract に「branch-diff review で使う report/update は committed history に存在する」を明記する。
- report の corrective step には actual commit hash を必ず残す。

## 備考
- current branch review は committed delta only を対象としていたため、この問題は単なる wording issue ではなく review scope violation に近い。
