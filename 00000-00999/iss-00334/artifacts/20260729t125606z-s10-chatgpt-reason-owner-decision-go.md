# S10 ChatGPT reason owner decision — GO

## Evidence identity

- Session: `iss00334-s10-reason-decision-cooldown11`
- Wrapper: `/Users/iwasawayuuta/.agents/skills/chatgpt-use/scripts/oracle-chatgpt`
- Browser model selection: `requested=Pro`, `resolved=Pro`, `status=already-selected`, `strategy=select`, `verified=yes`
- Repository: `chemitaro/spec-dock`
- Branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
- Source HEAD: `7636c139565da1249ec45264e3f0b3d607ee1fce`
- GitHub comparison: `identical`, `ahead_by=0`, `behind_by=0`
- Review mode: read-only bounded decision; decision review waived

## Decision

**GO.** `kind == "paths"` の場合に限り、期待する reason を
`review_identity_rejected` から `review_result_rejected` へ変更してよい。
S10 を停止する必要はない。

production、仕様、設計、S11、fixture、parameter、status、path、その他の
semantic contract は変更しない。

## Source evidence

`tests/unit/application/test_issue_planning_apply.py` の対象テストは、
`kind` を `head` と `paths` で parameterize する。

- `paths` は、resolved Issue directory を `/iss-other/` に置き換えた誤った
  canonical target paths を review result に直列化する。
- apply は repository から解決した正しい target paths を
  `PlanningReviewResult.from_json_bytes` へ渡す。
- `ReviewedPlanningIdentity.__post_init__` から
  `validate_canonical_target_paths` が呼ばれ、直列化された paths が resolved
  target と異なるため `ValueError` になる。
- apply はこの parse failure を
  `status="rejected"`, `reason="review_result_rejected"` に正規化する。
- 後段の `review_identity_rejected` は、review result と human decision の
  parse が成功した後の identity comparison を所有する。
- `head` は canonical paths が有効なまま `identity.source_head` と
  `request.expected_head` を不一致にするため、後段の
  `review_identity_rejected` を維持する。

したがって `paths` case は後段へ到達せず、現在の production が返す
`review_result_rejected` が fail-closed stage owner として正しい。

## Exact allowed edit

対象は
`tests/unit/application/test_issue_planning_apply.py` の共通 assertion 1行だけ。

```python
    _assert_not_ready(result, ("rejected", "review_result_rejected" if kind == "paths" else "review_identity_rejected"))
```

## Required verification

```bash
uv run pytest tests/unit/application/test_issue_planning_apply.py::test_pa_nf_06_wrong_review_identity_is_rejected
uv run pytest tests/unit/application/test_issue_planning_apply.py
uv run pytest
```

ChatGPT は read-only decision を担当し、これらのコマンドは実行していない。

## Bounded worker instruction

exact source HEAD
`7636c139565da1249ec45264e3f0b3d607ee1fce` で、上記 assertion 1行だけを変更する。
`kind == "paths"` では `review_result_rejected`、`kind == "head"` では
`review_identity_rejected` を期待する。production code、test name、
parameterization、status、fixture construction、canonical paths、mutation
assertion、他の expectation、仕様、設計、S11 material は変更しない。
必須テストが失敗した場合は scope を広げず停止して報告する。
