# Prompt composition reference

## Purpose

Define how SpecDock scripts should build ChatGPT-first planning prompts without over-constraining ChatGPT's reasoning.

## Composition Order

1. Repository and branch.
2. GitHub sync state.
3. Target type and target id.
4. Operator intent.
5. Development background.
6. Planning objective.
7. Required artifact list.
8. Input context and source artifact references.
9. Input context type when target is Issue Planning.
10. Information insufficient policy.
11. Output format request.

## Free-form Fields

`operator_intent` and `development_background` are important. They preserve why the human wants the work and why previous attempts were insufficient. The script should not reduce these fields to fixed flags.

## Issue Context Types

The script may infer or accept:

- `requirement-heavy`
- `draft-heavy`
- `context-heavy`

These labels help ChatGPT orient itself. They are not modes and must not change the artifact contract.

## Required Artifact List

The script should explicitly list paths and purposes. ChatGPT should know what files are expected, but should not be forced into local token-saving workflow steps.

## Information Insufficient

The prompt must allow ChatGPT to stop with `information_insufficient` when formal artifacts would be speculative.

## Prohibited Prompt Content

- Automatic fallback to manual workflow.
- Separate Issue Planning workflow modes for different input sources.
- Claims that ChatGPT can approve reviewer gates.
- Claims that generated artifacts are automatically execution-ready.
