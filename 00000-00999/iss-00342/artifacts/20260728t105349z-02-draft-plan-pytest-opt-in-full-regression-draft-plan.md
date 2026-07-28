---
種別: 実装計画ドラフト（Issue）
ID: "iss-00342"
タイトル: "Pytest Opt-In Full Regression Draft Plan"
Issue Grade: "standard"
状態: "draft"
作成者: "ChatGPT authoring candidate / main orchestrator preserved summary"
最終更新: "2026-07-28"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
親: ["epic-00080", "init-00079"]
authority: "evidence_only"
adoption_status: "unreviewed"
reflected_to: []
---

# Pytest opt-in full regression — 実装計画ドラフト

## 証跡

- Detailed candidate: `specdock-authoring-pack/drafts/plan.md`
- ZIP SHA-256: `511b81980c67da9d7e6b9290c20e59959e7d0835496aecee86f170bdc4402212`
- Source commit: `2513c943fee26de16d0c0371eafeaa5a484cfd43`

この文書はChatGPT詳細候補の採用判断用要約であり、正本ではない。

## 実装順序

### P00 — 正本改訂

- 本ドラフト、ADR候補、既存accepted Option A ADRを照合する。
- 旧`addopts=-m fast`、mandatory Make facade、custom flag非採用の記述を置換する。
- requirement/design/plan/reportを更新し、assuranceを再bindする。
- fresh spec reviewer gateが完了するまで実装を開始しない。

### S00 — baseline characterization

- current root collectionとrequired-fast exact nodesを同一SHAで記録する。
- existing static/dynamic skip、skipif、xfail、collection skip、known flakyを区別して記録する。
- source/configは変更しない。

### S01 — contract test Red

- `--run-full-regression` help。
- early marker visibility。
- exactly-one classification。
- focused collection safety。
- ordinary/focused policy skip。
- `-m full_regression` alone非許可。
- flagありfull、failure propagation、legitimate skip preservation。
- workflow event matrix、identity、non-shipping。

production hook/config/workflow変更前に期待するRedを確認する。

### S02 — pytest hook/config Green

- `tests/conftest.py`へoption、early classification、conditional policy skipを実装する。
- `pyproject.toml`へmarker registry/strictnessだけを追加する。
- default `addopts=-m fast`を追加しない。
- Make wrapperを要求しない。
- focused/root/marker/flag/legitimate skipを検証する。

### S03 — workflow Green

- PR provider workflowをPR-only lint + `uv run pytest`へ変更する。
- main/manual full workflowを追加し、`uv run pytest --run-full-regression`を直接実行する。
- non-main push、schedule、duplicate eventを拒否する。
- identity、concurrency、summary、failure propagation、non-shippingを契約テストで固定する。

### S04 — documentation

- READMEとAGENTSへ通常、full、focused、marker-only非許可、collection caveat、incident、rollbackを記載する。
- Makefileをcanonical interfaceとして案内しない。

### S05 — integrated ordinary gate

- `uv run pytest`
- `uv run pytest tests/unit`
- focused fast
- focused heavy without flag
- `-m full_regression` without flag
- lint、root verifier、workflow contract、SpecDock validate

このstepではformal fullを実行しない。

### S06 — paired measurement

- 同一stateでordinary/fullをexactly 3 pairs実行する。
- ordinaryのH body実行数0、fullのpolicy skip 0、selection parity、durationを記録する。
- known legitimate skip/xfailとfailureをpolicy skipから分離する。

### S90 — final local gate

- focused tests、ordinary gate、workflow tests、docs、non-shipping、diff check。
- code review、QA review、fresh spec review。
- reportのclosure/EAL/decision/measurement/rollback欄を更新する。

### S110以降 — delivery

- Pull Requestを作成し、同一reviewed SHAのPR gateを観測する。
- human-only merge boundaryで停止する。
- human merge後、main full workflowのevent/SHA/outcomeを観測する。
- post-merge failure時はsame-SHA focused/full reproductionをincidentとして扱う。

## 主要テストカード

| ID | 検証 |
|---|---|
| TC-TL-001 | helpにexact optionがある |
| TC-TL-002 | dynamic markerが`-m`評価前に見える |
| TC-TL-003 | marker conflict/exactly-one違反がcollection error |
| TC-TL-004 | focused subsetがglobal inventory不足で失敗しない |
| TC-TL-005 | root `F∩H=∅`, `F∪H=C`, `U=0`, `H>0`, required-fast |
| TC-TL-006 | bare ordinaryはF実行、H policy skip |
| TC-TL-007 | `tests/unit`も同じpolicy |
| TC-TL-008 | focused H without flagはbody未実行、exit 0、stable reason |
| TC-TL-009 | focused H with flagはbody実行 |
| TC-TL-010 | `-m full_regression` aloneはpermissionでない |
| TC-TL-011 | flag + long-onlyはrunnable H |
| TC-TL-012 | root fullはpolicy skip 0 |
| TC-TL-013 | failing Hはnormal nonzero |
| TC-TL-014 | legitimate skip/skipif/xfail不変 |
| TC-TL-015 | policy skipはcollection/import failureを隠さない |
| TC-TL-016 | required-fast 7 exact nodes保持 |
| TC-TL-017 | PR identity、lint + ordinary pytest、fullなし |
| TC-TL-018 | exact event matrix |
| TC-TL-019 | concurrencyとduplicate防止 |
| TC-TL-020 | provider-only workflow非shipping |
| TC-TL-021 | summaryにevent/SHA/count/outcome/duration/rerun |
| TC-TL-022 | README/AGENTS direct command guidance |
| TC-TL-023 | 3 paired measurements |
| TC-TL-024 | PR commandをfullへ戻すrollback rehearsal |

## path ownership

| Path | Operation |
|---|---|
| `tests/conftest.py` | add |
| `tests/unit/test_provider_test_lanes.py` | add |
| `tests/unit/infra/test_init_update.py` | bounded modify |
| `pyproject.toml` | marker registry/strictness only |
| `.github/workflows/provider-ci.yml` | PR direct ordinary command |
| `.github/workflows/provider-full-regression.yml` | add |
| `README.md` | direct commands/operations |
| `AGENTS.md` | agent guidance |
| Issue `report.md` | observed evidence only |

`Makefile`、product source、shipped assets、unrelated workflowsは原則read-only。

## Stop条件

- owner decisionと異なるcommand semanticsが必要
- hook lifecycle assumptionが現行pytestで成立しない
- legitimate skip/xfailを保全できない
- PR check identityを維持できない
- consumer shippingが必要になる
- classificationに未解決の漏れ/重複がある
- baselineやpaired measurementで説明できないdriftがある

上記ではorigin phaseへ戻り、canonical plan amendmentとfresh reviewを行う。
