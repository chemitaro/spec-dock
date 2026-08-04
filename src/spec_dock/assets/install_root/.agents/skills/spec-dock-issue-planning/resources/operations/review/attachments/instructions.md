# Issue Planning Review Detailed Instructions

Use the exact `Reviewed identity` value from the minimal body as `reviewed_identity`. Use the
exact `Reviewed identity SHA-256` value from the minimal body as `reviewed_identity_sha256`.

Set `verdict` to `fail` if and only if at least one finding is `p0` or `p1`; otherwise set it to
`pass`. Make findings unique. Each finding uses only `id`, `severity`, `exact_location`,
`violated_requirement_or_contradiction`, and `concrete_impact`. Allowed severities are `p0`,
`p1`, `p2`, and `p3`.

For an onboarding companion, report only actual canonical contradiction, wrong current status,
wrong direct-Oracle/exact-branch/Human-authority statement, missing mandatory section or diagram
role, invalid or materially misleading PlantUML, Runtime-to-Reviewer adapter bypass, missing
fresh exact-branch inspection, or missing closed-JSON return boundary. Style preferences, optional
rewording, aesthetics, and unsolicited redesign are not defects and cannot independently fail
review.

Return one closed JSON object only. Do not mutate canonical files, approve or adopt planning,
authorize implementation, or include raw transcripts, credentials, session or conversation
identifiers, private URLs, or private host paths.
