# Delegated Authoring Probe Plan

## Positive Probe
- id: `iss-00126-system-architect-design-desktop-be50b225875f-positive`
- target: `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/design.md`
- expectation: delegated author can update only the exact target draft artifact.

## Negative Probe
- sentinel: `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00126-write-capable-delegated-draft-authoring-correction/discussions/.iss-00126-system-architect-design-desktop-be50b225875f.spec-dock-permission-probe-denied`
- expectation: disposable sentinel creation must be denied.
- real artifact/source/test/config/secret files must not be touched.
- if the sentinel is created, remove only the sentinel, record fail-open evidence, and abort on dirty diff.

## Diff Gate
- require target artifact diff only.
- require no forbidden path diff.
- abort if cleanup leaves dirty probe artifacts.
