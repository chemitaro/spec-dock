---
種別: disc
ID: "20260329t053816z-disc"
タイトル: "test-realignment-scope-and-acceptance"
状態: "completed"
作成者: "Codex CLI"
最終更新: "2026-03-29"
親: ["iss-00040"]
関連: ["20260329t053816z-01-research"]
---

# 20260329t053816z-disc test-realignment-scope-and-acceptance

## 議題 (必須)
- `iss-00040` を「runtime contract を戻す issue」ではなく「現行 contract に対する tests / checked-in parity の realignment issue」としてどう切るかを確定する。
- current-contract fixture と legacy fixture をどう使い分けるか、acceptance criteria を `sync` / `wrappers` / `domain` / parity までどう広げるかを整理する。

## 背景 (必須)
- epic-00033 では GitHub-backed identity / `origin` basis の current repo scope / fail-closed posture を導入済みである。
- `tests/cli_runtime/test_new.py` は既に新 contract に追随済みだが、`test_active.py` / `test_deps.py` / `test_sync.py` には stale fixture が残っている。
- `test_wrappers.py`、`test_runtime_domain_s01.py`、`tests/test_init_update.py` にも、同じ contract shift に未追随の expectation が残っている。
- sync は legacy checked-in data の read path を完全には捨てていないため、legacy/local-only behavior を検証したい test 自体は still meaningful である。
- ユーザー確認により、本 issue は broader scope、つまり stale tests と dogfooding mirror parity まで含めて閉じる方針になった。

## 選択肢 (必須)
- Option A:
  - 内容:
    - runtime 側を緩め、normal path でも `new --no-github` が再び成功するよう戻す。
  - Pros:
    - 既存テストの修正量は少ない。
  - Cons:
    - epic-00033 の GitHub mandatory contract に反する。
    - local-only create path を再導入し、fail-closed posture を弱める。
- Option B:
  - 内容:
    - normal path tests は GitHub-backed fixture に揃え、legacy/local-only を検証したい tests だけ explicit legacy fixture に切り替える。あわせて wrappers / domain / parity も current source of truth へ realign する。
  - Pros:
    - epic-00033 の contract と整合する。
    - `active` / `deps` / `sync` の現行 behavior と legacy read-path coverage を両立できる。
    - current stale-contract cluster を 1 issue で coherent に扱える。
  - Cons:
    - fixture 戦略の切り分けが必要で、単純置換より設計負荷がある。
- Option C:
  - 内容:
    - `active` / `deps` / `sync` だけ直し、`wrappers` / `domain` / parity は別 issue へ送る。
  - Pros:
    - 今回の変更面積は小さくなる。
  - Cons:
    - current stale-contract cluster を 1 回で閉じられない。
    - issue title と user intent から外れる。

## 推奨案 (必須)
- Option B を採る。
- 理由:
  - `iss-00040` の成功条件は runtime rollback ではなく regression / parity の realignment である。
  - `test_new.py` と `harness.py` に current-contract の参照パターンがあり、流用しやすい。
  - legacy/local-only の read path を検証したいケースは unsupported create CLI ではなく explicit fixture で表現するのが筋である。
  - full suite の red cluster は `active` / `deps` / `sync` / `wrappers` / `domain` / parity にまたがる同一ドリフトであり、今回の issue でまとめて閉じるのが妥当である。

## 未決事項 (任意)
- 実装中に true product defect が新たに見つかった場合は、この issue 内で最小修正まで扱うか、別 issue に切るかを都度判定する。
  - 現時点の推奨は「test realignment では閉じない defect なら別 issue 化」である。

## 次アクション (必須)
- research の結論を requirement / design / plan に反映する。
- acceptance criteria に current-contract fixture / legacy fixture / wrappers / domain / parity / final regression を明示する。
- 仕様書 3 点が揃ったら spec reviewer に回し、pass まで修正ループする。
