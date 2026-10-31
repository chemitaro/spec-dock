// SpecDock spec type specdock/v1: the requirement document (requirement.cue).
package spec

// Optional sections. Every file's top level stays open, so a Scope may add fields of its own.
purpose?:    #Text
background?: #Text
includes?: [...#Text]
excludes?: [...#Text]
constraints?: [...#Text]
decisions?: [...#Text]
questions?: [...#Text]

// Observable requirements, keyed by number (R-01, R-02, ...). Only numbered keys are allowed.
requirements: close({[=~"^R-[0-9]{2,}$"]: #Requirement})

#Requirement: {
	title!: #Title
	text?:  #Text
	// Observable acceptance conditions; required from standard (see the level table below).
	acceptance?: [...#Text]
	...
}

// Failure and boundary conditions, keyed by number (F-01, ...). Tests, steps and designs may refer to them.
failures: close({[=~"^F-[0-9]{2,}$"]: #Failure})

#Failure: {
	title!:    #Title
	text?:     #Text
	impact?:   #Text
	recovery?: #Text
	...
}

// Fields the assurance level makes required (design.md of iss-00472, "保証レベルごとの必須の項目").
if _rank >= 1 {
	requirements: [_]: acceptance!: [#Text, ...#Text]
}
if _rank >= 2 {
	failures: [_]: {
		impact!:   #Text
		recovery!: #Text
	}
}
