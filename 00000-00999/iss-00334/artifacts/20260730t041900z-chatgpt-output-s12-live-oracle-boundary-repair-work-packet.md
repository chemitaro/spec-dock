# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6ace62-02d0-83ee-86f0-54f3dd0e517e

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached repair brief as the authoritative task. Inspect the exact GitHub branch first, then the attached implementation, tests, and reference transport code. Return only the bounded implementation work packet requested by the brief.

## Answer

# Bounded Implementation Work Packet

## Source lock

GitHub connector inspection succeeded for `chemitaro/spec-dock`. The mandatory branch `iss-00334-implement-chatgpt-issue-planning-workflow` is identical to exact HEAD `d3473ee3d56b6f12a34952b4b426657b3269a0aa` with ahead `0` and behind `0`; the default branch was not used. The inspected commit is the required source commit.

The attached repair brief is authoritative.

## 1. Root cause for each failure

### RC-1 — Public `oracle_session_recovery_required` is a secondary classification, not the initiating defect

The adapter’s submission argv contains browser mode, wait, attachment, slug, prompt, and file arguments, but no explicit model selector or managed-Chrome attachment arguments.

After any nonzero Oracle exit, the adapter sets `needs_recovery=True`. A missing or nonterminal session then enters same-session harvest; if that does not produce a terminal session, the public result becomes `blocked/oracle_session_recovery_required`.

Therefore the public result masked two earlier pre-submit failures:

1. Oracle rejected the inherited model configuration.
2. After the model was overridden manually, Oracle attempted to launch a second Chrome rather than attach to the authenticated managed Chrome.

No change to Candidate, Review, Human-decision, apply, or publication semantics is implicated.

### RC-2 — The adapter inherits an unusable browser-model default

The adapter does not pass `--model`. Its sanitized environment retains `HOME` and `ORACLE_HOME_DIR`, allowing Oracle’s user configuration to remain effective.

The supplied Oracle browser source does not recognize `gpt-5.6-pro` among the accepted current browser variants. It does recognize the version-independent UI selector `Pro`, mapping the browser target to the Pro picker.

The repair must therefore pass the literal selector:

```text
--model Pro
```

It must never pass either `gpt-5.6-pro` or `gpt-5.5-pro`. Live evidence may state only:

```text
requested=Pro
resolved=Pro
verified=yes
```

It must not claim that the selected underlying model is an exact GPT-5.6 or GPT-5.5 version.

An explicit model strategy is also required so Oracle user configuration cannot select “current” behavior instead of selecting the requested Pro picker target:

```text
--browser-model-strategy select
```

### RC-3 — The adapter does not attach to the managed Chrome endpoint

The current argv omits `--remote-chrome`, so Oracle follows its launch/default configuration and attempted a second manual-login Chrome at the ephemeral port reported in the live failure.

The supplied Oracle source has a dedicated `remoteChrome` host/port option and separately models cookie synchronization. It also shows that `--browser-attach-running` is a different mode with conflicts against explicit cookie/profile/port controls.

The product repair must therefore use:

```text
--remote-chrome <validated-loopback-endpoint>
--browser-no-cookie-sync
```

It must not use `--browser-attach-running`.

The dedicated persistent profile remains an attribute of the already-running managed Chrome process. SpecDock must not receive or pass its filesystem path. Adding a profile-path contract would recreate the prohibited operator-filesystem dependency.

### RC-4 — Existing capability and fake-transport tests do not cover the live boundary

The Oracle capability preflight currently checks neither model selection nor managed-Chrome arguments.

The primary direct-argv test verifies one prompt and the absence of `--write-output`, but it does not require `Pro`, `select`, `remote-chrome`, or no-cookie-sync.

The fake Oracle used by the full Issue Planning integration chain advertises only the original flags, and the integration assertion likewise does not enforce the missing live arguments.

## 2. Minimal file allowlists

### Production allowlist

Provider authority:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
```

Generated managed projections only:

```text
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
.agents/skills/spec-dock-issue-planning/SKILL.md
```

The Skill change is limited to declaring the required managed-Chrome environment contract and its fail-closed precondition. Its existing execution boundary already requires the repo-local command and PATH Oracle, with no personal wrapper or API fallback.

No new installed executable, shell wrapper, browser launcher, profile helper, config file, public CLI option, domain contract, or application file is admitted.

### Test allowlist

```text
tests/unit/infra/test_issue_planning_chatgpt.py
tests/integration/test_issue_planning_e2e.py
```

The integration file is required because its installed-runtime fake Oracle help, environment, and exact submission assertions must implement the repaired contract.

### Explicitly excluded

```text
requirement.md
design.md
plan.md
domain/issue_planning_contracts.py
application/issue_planning.py
infra/issue_planning_oracle_artifact.py
oracle-chatgpt
browserConfig.ts
browserDefaults.ts
```

The attached wrapper and Oracle source files remain read-only references.

If official projection changes any additional managed path, stop rather than silently expanding this allowlist.

## 3. Exact argv and configuration contract

### Ownership decision

Use a **combination of the existing provider-owned direct adapter and one product-owned environment contract implemented by that adapter**.

Do not add an installed helper executable. Chrome lifecycle, authentication, and persistent-profile ownership remain outside SpecDock.

### Environment contract

Required parent-process variable:

```text
SPECDOCK_ORACLE_REMOTE_CHROME
```

Accepted values are limited to:

```text
127.0.0.1:<port>
localhost:<port>
```

where `<port>` is a decimal integer from `1` through `65535`.

Rules:

* No default value.
* No URL scheme.
* No path, credentials, query, fragment, whitespace, non-loopback host, or remote network address.
* Missing, empty, malformed, unreachable, or non-CDP values fail closed.
* The variable is read by `issue_planning_chatgpt.py` but is not added to `_SAFE_ENVIRONMENT_KEYS` and is not forwarded to the Oracle child.
* The value is not serialized into `PlanningInvocationResult`.
* Failure maps to existing `blocked/oracle_unavailable` with `backend_exit_code=None`.
* Missing Oracle flags continue to map to `blocked/oracle_capability_unsupported`.
* No new public status or reason is introduced.

### Managed-Chrome preflight

Before creating a prompt pack, session slug, or Oracle submission:

1. Parse the closed endpoint grammar.

2. Open a direct, proxy-independent HTTP connection with a bounded timeout.

3. Request:

   ```text
   GET /json/version
   ```

4. Require HTTP `200`.

5. Parse a bounded JSON object.

6. Require a nonempty `webSocketDebuggerUrl`.

7. Require that URL to identify a loopback host and the configured port.

8. Close the connection without opening or modifying a tab.

A syntax failure starts no Oracle process. A connectivity or CDP-validation failure may occur after Oracle version/help preflight but must submit no prompt and create no session.

### Oracle capability preflight

Extend `_ROOT_CAPABILITIES` to require:

```text
--model
--browser-model-strategy
--remote-chrome
--browser-no-cookie-sync
```

Retain all existing required flags and session capabilities.

### Exact submission argv

The single formal submission must be equivalent to:

```text
<PATH-resolved-final-oracle>
  --engine browser
  --model Pro
  --browser-model-strategy select
  --remote-chrome <SPECDOCK_ORACLE_REMOTE_CHROME>
  --browser-no-cookie-sync
  --wait
  --browser-attachments always
  --slug <new-session-id>
  --prompt <synthesized-prompt>
  --file <prompt-pack>
```

Argument order may follow the list above to make capture tests deterministic.

The submission must contain exactly one occurrence of each of:

```text
--model
--browser-model-strategy
--remote-chrome
--prompt
--file
--slug
```

The following must remain absent:

```text
gpt-5.6-pro
gpt-5.5-pro
--browser-attach-running
--browser-manual-login
--browser-manual-login-profile-dir
--browser-chrome-profile
--browser-cookie-path
--copy-profile
--browser-port
--browser-debug-port
--browser-inline-cookies
--browser-inline-cookies-file
--write-output
oracle-chatgpt
chatgpt-use
any personal absolute path
```

The running Chrome must already be authenticated and must itself own the dedicated persistent profile. SpecDock knows only the validated CDP endpoint.

## 4. Required negative and positive tests

### Unit negative tests

| Test                                                                 | Required assertion                                                                                                                                                                      |
| -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_missing_managed_chrome_contract_starts_no_oracle`              | Missing or blank variable returns `blocked/oracle_unavailable`; subprocess count `0`; session directory count unchanged.                                                                |
| `test_invalid_managed_chrome_contract_starts_no_oracle`              | Parameterize URL form, missing port, port `0`, port `65536`, nonnumeric port, non-loopback host, credentials, path, whitespace, and fragment; subprocess count `0`.                     |
| `test_unreachable_or_non_cdp_managed_chrome_submits_no_prompt`       | Connection refused, non-200 response, malformed JSON, missing websocket URL, wrong host, or wrong port returns `blocked/oracle_unavailable`; prompt count `0`; session count unchanged. |
| `test_required_model_and_remote_chrome_capabilities_are_preflighted` | Omitting any of the four new help flags returns `oracle_capability_unsupported`; prompt count `0`.                                                                                      |
| `test_managed_chrome_contract_is_not_forwarded_to_child`             | `SPECDOCK_ORACLE_REMOTE_CHROME` is absent from captured child environment, as are API and cookie credential variables.                                                                  |
| `test_user_model_config_cannot_override_product_selector`            | Even with a fixture user config containing `gpt-5.6-pro`, the captured argv contains only `--model Pro` and `--browser-model-strategy select`.                                          |
| `test_no_personal_profile_or_wrapper_argument_is_emitted`            | Captured argv contains none of the explicitly excluded profile, wrapper, cookie, or absolute-path arguments.                                                                            |
| Existing unknown-terminal recovery test                              | Still performs exactly one prompt submission and returns `oracle_session_recovery_required` without a second submission.                                                                |

### Unit positive tests

Update the existing direct-argv planner test to require the complete exact argv contract and a successful managed-Chrome preflight.

Retain and strengthen the existing timeout recovery test:

```text
managed-Chrome preflight count == 1
prompt submission count == 1
same-session harvest count == 1
new-session submission count after timeout == 0
```

The existing recovery test already establishes one prompt and one harvest and must continue to do so.

Run the same exact argv assertion for the reviewer path so planner, semantic revision, and reviewer cannot diverge.

### Integration test changes

Inside `tests/integration/test_issue_planning_e2e.py`:

1. Start an ephemeral loopback fake CDP HTTP server serving a valid `/json/version`.

2. Set:

   ```text
   SPECDOCK_ORACLE_REMOTE_CHROME=127.0.0.1:<ephemeral-port>
   ```

3. Extend fake Oracle `--help` with the four new flags.

4. Make fake Oracle exit before artifact creation unless all exact fixed arguments are present.

5. Assert the endpoint variable is absent from the fake Oracle child environment.

6. Assert the installed Skill names the environment variable, loopback-only rule, pre-existing authenticated browser requirement, and absence of profile/cookie transfer.

7. Preserve the existing create, semantic revision, archive review, git-bound review, Human decision, apply, rollback, and publication assertions unchanged.

Tests must fail on the current HEAD because the required flags and configuration contract are absent.

## 5. Live recovery sequence with duplicate-submission proof

1. Confirm the exact repair branch and pushed repair HEAD, clean worktree, synchronized upstream, and provider/projection byte parity.

2. Before any new Oracle run, snapshot the exact set of directories under the configured Oracle session root.

3. Inspect the two failed-run metadata records already identified by the live investigation. A new run is admitted only if both still prove:

   ```text
   promptSubmitted == null
   chromeTargetId absent
   conversationId absent
   tabUrl absent
   ```

   If any prior record shows a submitted prompt, conversation, or tab, stop and recover that exact session instead of starting a new planning run.

4. Start or verify the operator-owned managed Chrome using its dedicated persistent profile. Set only:

   ```bash
   export SPECDOCK_ORACLE_REMOTE_CHROME=127.0.0.1:9223
   ```

   Do not export a profile path, cookie, token, API key, wrapper path, or Project URL.

5. Run the repaired public command exactly once:

   ```bash
   ./spec-dock/scripts/spec-dock-chatgpt planning create \
     --issue iss-00334 \
     --output <external-create-dir> \
     --format json
   ```

6. Diff the pre-run and post-run session-directory inventories. Require exactly one new `specdock-planner-*` session. More than one new session is a stop condition.

7. For that exact session, require:

   ```text
   model selector requested as Pro
   resolved UI selector Pro
   model verification yes
   promptSubmitted non-null exactly once
   exactly one chromeTargetId
   at most one conversationId
   at most one tabUrl
   exactly one expected authoring ZIP
   ```

   Do not describe the selected underlying model as an exact numbered Pro release.

8. If the process times out or disconnects after `promptSubmitted` becomes non-null, do not rerun `planning create`. The adapter may execute only:

   ```text
   oracle session <same-session-id> --harvest --no-recover
   ```

   The existing recovery implementation revalidates the executable and uses only that same session.

9. If same-session harvest remains nonterminal, accept only `blocked/oracle_session_recovery_required` and stop. Do not create another session or resubmit the prompt.

10. A successful recovery proof requires:

    ```text
    prior failed prompt submissions == 0
    new formal prompt submissions == 1
    new ChatGPT planning turns == 1
    new matching browser tabs == 1
    published authoring ZIP count == 1
    published Candidate ZIP count == 1
    ```

11. Stop after Candidate creation unless the later exact Human planning decision separately authorizes Review and apply. This repair does not supply or infer that decision.

## 6. Stop conditions

Stop the repair immediately if any of the following is encountered:

* The mandatory branch or implementation HEAD changes before the bounded repair is applied.
* The fix requires invoking, importing, copying, or discovering the personal `chatgpt-use` wrapper.
* A personal home path, profile directory, Project URL, LaunchAgent, cookie, token, or API credential must enter product argv or configuration.
* A non-loopback Chrome endpoint or authenticated remote-browser service is required.
* Oracle 0.16.1 does not expose or honor `Pro`, `select`, `remote-chrome`, or no-cookie-sync through direct argv.
* `--remote-chrome` plus no-cookie-sync cannot attach to the already-running browser without also passing a profile path.
* Correctness requires launching or managing Chrome from SpecDock.
* Endpoint validation would require scanning the filesystem, process table, browser profiles, or Oracle home for a matching browser.
* Any test or live evidence records more than one prompt submission for one planning operation.
* A prior failed session is found to have submitted a prompt.
* Same-session recovery would require a new slug or a second formal submission.
* The repair requires a new public command, option, status, reason, schema, registry, database, or persistent session authority.
* Candidate inventory, Reviewer JSON, Human-decision binding, apply, rollback, or publication semantics must change.
* Any production or test path outside the allowlists is required.
* Provider/projection parity, focused tests, integration tests, full regression, distribution checks, or static checks fail.
* Live output is missing, ambiguous, unsafe, or not exactly one expected authoring ZIP.

## 7. Final disposition

**GO_BOUNDED_REPAIR**
