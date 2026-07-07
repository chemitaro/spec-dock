# ChatGPT Use planning summary for iss-00291

## Session

- session slug: `specdock-iss00291-docs-planning`
- model surface: ChatGPT Use / GPT-5.5 Pro Extended via Oracle wrapper
- result: completed
- full browser conversation log: not committed

## Adopted recommendations

- Expand `scripts/authoring-pack/README.md` as the Japanese-first entry point for dogfood-only authoring-pack workflow.
- Keep `spec-dock/docs/**` out of scope unless a direct contradiction is found.
- Add Issue-local artifacts for:
  - authoring-pack workflow,
  - prompt contract,
  - Evidence Adoption Ledger examples,
  - manual fallback notes.
- Record backend command adapter / Oracle wrapper decoupling as deferred to `iss-00293`, not implemented in `iss-00291`.
- Avoid raw transcripts, host-local absolute paths, personal wrapper paths, and shipped-runtime claims in canonical docs.

## Rejected or deferred items

- Do not implement `SPECDOCK_CHATGPT_COMMAND` / `ORACLE_CHATGPT_COMMAND` adapter in this Issue.
- Do not promote dogfood helpers to SpecDock runtime commands in this Issue.
- Do not store raw ChatGPT transcript as repo evidence.

## Verification focus from ChatGPT Use

- `git diff --check`
- `./spec-dock/scripts/spec-dock validate`
- docs inspection for unsafe authority claims and host-local path leakage
- focused authoring-pack manual tests if helper behavior is touched

## Adoption boundary

This summary is advisory evidence only. The implemented docs and report updates are the canonical local adoption record after local verification and fresh reviewer gates.
