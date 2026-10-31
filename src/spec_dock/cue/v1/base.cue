// SpecDock spec type, version specdock/v1: common fields.
//
// SpecDock evaluates every *.cue file of this directory, then the repository's own type files
// (spec-dock/cue/*.cue, optional), then the Scope's requirement.cue, design.cue and plan.cue as one
// instance of package spec (contract K1 of epic-00425):
//
//   cue export --out json -t kind=<initiative|epic|issue> <these files> <repository files> <Scope files>
//
// Once released, this version only grows in compatible ways: new optional fields or relaxed constraints.
// A change that would fail a document this version accepted, or change its findings, belongs in cue/v2/
// (contract K6). Repository types may read the public fields and _rank; names under _specdock are internal.
package spec

// The type version. Write it in requirement.cue.
schema!: "specdock/v1"

// The Scope kind comes from GitHub, the structure authority; SpecDock passes it as a tag.
kind: "initiative" | "epic" | "issue" @tag(kind)

// The assurance level is chosen by the impact of a failure and how hard recovery is (R-C1).
// Its one authority is this block in requirement.cue (R-C2).
assurance: {
	// A pattern instead of a disjunction keeps the error for a wrong value on one line.
	level!:  string & =~"^(light|standard|strict|critical)$"
	reason!: #Text
	...
}

// The assurance level as a number, for level-dependent fields and rules (light=0 ... critical=3).
// The default 0 applies only while the level is unreadable, so a top-level `if _rank >= n` reports the
// missing or wrong level instead of a cycle; the evaluation still fails on assurance.level.
_rank: *_specdock.levels[assurance.level] | 0

_specdock: {
	levels: {light: 0, standard: 1, strict: 2, critical: 3}
	// A document cannot move _rank away from the declared level: a different value conflicts here.
	rank: levels[assurance.level] & _rank
	// Kind switches read this, so a missing kind tag reports only `kind`, not every switch.
	issue: *(kind == "issue") | true
}

// Text that is not blank. Text fields may hold Markdown; renderers draw it as Markdown (contract K5).
// "Blank" follows Python's str.isspace(): RE2's \s covers only ASCII, so the class also excludes the
// Unicode separators (\p{Z}, such as U+3000) and \v, U+001C-U+001F and U+0085.
#Text: string & =~"[^\\s\\p{Z}\\x{0B}\\x{1C}-\\x{1F}\\x{85}]"

// One line of text that is not blank.
#Title: string & =~"^[^\\n]*[^\\s\\p{Z}\\x{0B}\\x{1C}-\\x{1F}\\x{85}][^\\n]*$"

// Connection findings, one list per rule. A rule that applies at this level always has a list, empty
// when nothing is wrong; a rule below its stage has no entry. Repository types may add rules.
findings: [rule=string]: [...{
	id:      string
	message: string
	hint?:   string
}]
