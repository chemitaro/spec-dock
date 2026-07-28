# Transport output contract

Return exactly one UTF-8 frame and no text outside it:

`<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=<planner|reviewer> source_head=<40-hex>>>`

Place the non-empty advisory payload after the start marker, then end with:

`<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>`

Do not include raw transcripts, credentials, secrets, remote URLs, or private host absolute paths.
