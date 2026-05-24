# Delegated Authoring Probe Plan

## Positive Probe
- id: `iss-00126-system-architect-design-cli-85455ab6a889-positive`
- target: `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/design.md`
- expectation: delegated author can update only the exact target draft artifact.

## Negative Probe
- expectation: disposable sentinel creation must be denied for every forbidden boundary category.
- real artifact/source/test/config/secret files must not be touched.
- if a sentinel is created, remove only that sentinel, record fail-open evidence, and abort on dirty diff.

- category: `requirement.md` sentinel: `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/.iss-00126-system-architect-design-cli-85455ab6a889.requirement-md.spec-dock-permission-probe-denied`
- category: `peer_artifact` sentinel: `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/.iss-00126-system-architect-design-cli-85455ab6a889.plan.md.spec-dock-permission-probe-denied`
- category: `report.md` sentinel: `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/.iss-00126-system-architect-design-cli-85455ab6a889.report-md.spec-dock-permission-probe-denied`
- category: `src/` sentinel: `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture/src/.iss-00126-system-architect-design-cli-85455ab6a889.spec-dock-permission-probe-denied`
- category: `tests/` sentinel: `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture/tests/.iss-00126-system-architect-design-cli-85455ab6a889.spec-dock-permission-probe-denied`
- category: `.codex/` sentinel: `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture/.codex/.iss-00126-system-architect-design-cli-85455ab6a889.spec-dock-permission-probe-denied`
- category: `.agents/` sentinel: `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture/.agents/.iss-00126-system-architect-design-cli-85455ab6a889.spec-dock-permission-probe-denied`
- category: `.env*` sentinel: `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture/.env.iss-00126-system-architect-design-cli-85455ab6a889.spec-dock-permission-probe-denied`

## Diff Gate
- require target artifact diff only.
- require no forbidden path diff.
- abort if cleanup leaves dirty probe artifacts.
