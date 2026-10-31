// SpecDock spec type specdock/v1: the design document (design.cue).
package spec

// Optional sections.
goals?: [...#Text]
current?:       #Text
target?:        #Text
compatibility?: #Text
risks?: [...#Text]

// Design units (responsibility, interface, data, ...), keyed by number (D-01, ...).
design: close({[=~"^D-[0-9]{2,}$"]: #Design})

#Design: {
	title!: #Title
	text?:  #Text
	// Numbers of the requirements and failure conditions this unit satisfies; checked by the rules.
	satisfies!: [...string]
	...
}
