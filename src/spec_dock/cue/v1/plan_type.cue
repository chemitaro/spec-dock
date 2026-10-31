// SpecDock spec type specdock/v1: the plan document (plan.cue).
//
// An Issue plan holds its own steps and tests. An Epic or Initiative plan holds slices: the child Scopes
// it hands its requirements to (R-B3). Every map below exists for every kind and stays empty where the
// kind does not use it.
package spec

// Optional sections.
goal?:         #Text
verification?: #Text
// How to roll back; required at critical once the plan has a step or a slice (rule rollback-missing).
rollback?: #Text
exit?:     #Text

// Issue: implementation steps, the work ledger the agent updates while working (R-D1, R-D2).
// The display order is the number order; `after` names the steps that come first.
steps: close({[=~"^S-[0-9]{2,}$"]: #Step})

#Step: {
	title!: #Title
	text?:  #Text
	// Numbers of the requirements and failure conditions this step realizes.
	realizes!: [...string]
	// A pattern after the default keeps the error for a wrong status short.
	status: *"todo" | (string & =~"^(todo|doing|done|dropped)$")
	after?: [...string]
	// The execution session that does this step (R-D3).
	session?: string
	...
}

// Issue: tests.
tests: close({[=~"^T-[0-9]{2,}$"]: #Test})

#Test: {
	title!: #Title
	text?:  #Text
	// Numbers of the requirements and failure conditions this test verifies.
	verifies!: [...string]
	...
}

// Epic and Initiative: slices keyed by child Scope ID. The child's title lives on GitHub and its
// assurance level in its own requirement.cue (R-C4), so neither is written here.
slices: close({[=~"^(epic|iss)-[0-9]{5,}$"]: #Slice})

#Slice: {
	// Numbers of the requirements and failure conditions handed to the child.
	covers!: [...string]
	text?: #Text
	after?: [...string]
	session?: string
	...
}

// Optional execution assignment (R-D3). SpecDock checks only the references (rule execution-reference);
// model and effort are plain strings whose meaning belongs to the user's workflow (R-D4).
execution?: {
	sessions?: [string]: #Session
	reviews?: [string]:  #Review
	...
}

#Session: {
	task?:      #Text
	model?:     string
	effort?:    string
	rationale?: #Text
	...
}

#Review: {
	role?: string
	// The step (Issue) or slice (Epic, Initiative) this review follows.
	after?:  string
	model?:  string
	effort?: string
	...
}

if _specdock.issue {
	slices: [string]: error("Issue の plan.cue には slices を書かない。実装の手順は steps に、テストは tests に書く")
}
if !_specdock.issue {
	steps: [string]: error("Epic と Initiative の plan.cue には steps を書かない。子の Scope への切り分けは slices に書く")
	tests: [string]: error("Epic と Initiative の plan.cue には tests を書かない。確かめることは、slices の covers で子の Scope に任せる")
}
