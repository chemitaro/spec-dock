// The human-task record specdock.todo/v1 (epic-00547 D-02, D-05; iss-00549 D-08).
//
// `spec-dock todo check` validates every record of a catalog at once:
//   cue vet -c -d '#Records' todo.cue json: -   with {"<path from the catalog>": <record>, ...} on standard input.
// The rules are the same as spec_dock.runtime.domain.todo_record.validate; tests/fixtures/todo/ binds the two.
// Every struct is open (`...`): a field a later version adds is not an error and is kept by the CLI.
package todo

import (
	"list"
	"strings"
	"time"
)

#Records: [string]: #Todo

#Time:    time.Time & =~"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
#Text:    string & =~"\\S"
#Title:   #Text & !~"[\n\r]" & strings.MaxRunes(200)
#Effort:  string & =~"^[1-9][0-9]*(m|h|d)$"
#ScopeID: string & =~"^(init|epic|iss)-([0-9]{5}|[1-9][0-9]{5,})$"
#By:      "agent" | "human"

#Option: {
	key!:  string & =~"^[A-Za-z0-9][A-Za-z0-9_.-]*$"
	text!: #Text
	...
}

#Resolution: {
	at!:     #Time
	by!:     #By
	role!:   string | null
	choice!: string | null
	note!:   string | null
	record!: string | null
	...
}

#Subtask: {
	id!:         string & =~"^t-[0-9a-hjkmnp-tv-z]{4}\\.[1-9][0-9]*$"
	title!:      #Title
	status!:     "open" | "done" | "cancelled"
	created_at!: #Time
	updated_at!: #Time
	resolution!: null | #Resolution
	if status == "open" {
		resolution: null
	}
	if status == "done" || status == "cancelled" {
		resolution: #Resolution
	}
	if status == "cancelled" {
		resolution: note: #Text
	}
	...
}

#History: {
	at!:     #Time
	by!:     #By
	role!:   string | null
	action!: "added" | "updated" | "done" | "snoozed" | "cancelled" | "reopened" | "subtask_added" | "subtask_done" | "subtask_cancelled" | "subtask_reopened" | "subtask_updated"
	target!: string | null
	note!:   string | null
	fields!: [...string]
	...
}

#Todo: {
	schema!:     "specdock.todo/v1"
	id!:         string & =~"^t-[0-9a-hjkmnp-tv-z]{4}$"
	title!:      #Title
	kind!:       "decide" | "check" | "operate" | "act" | "todo" | "checklist"
	status!:     "open" | "snoozed" | "done" | "cancelled"
	created_at!: #Time
	updated_at!: #Time
	origin!: {
		by!:   #By
		role!: string | null
		...
	}
	body!: string | null
	options!: [...#Option]
	recommendation!: null | {
		key!:    string
		reason!: #Text
		...
	}
	reply_to!:     string | null
	effort!:       null | #Effort
	due!:          #Time
	snooze_until!: null | #Time
	scopes!: {
		related!: [...#ScopeID]
		blocks!: [...#ScopeID]
		...
	}
	links!: [...#Text]
	tags!: [...#Text]
	subtasks!: [...#Subtask]
	resolution!: null | #Resolution
	history!: [...#History]

	_optionKeys: [for o in options {o.key}] & list.UniqueItems()
	_subtaskIDs: [for s in subtasks {s.id}] & list.UniqueItems()
	_subtaskParent: {for i, s in subtasks {"\(i)": strings.HasPrefix(s.id, id+".") & true}}

	if recommendation != null {
		_recommendationKnown: list.Contains(_optionKeys, recommendation.key) & true
	}
	if origin.by == "agent" {
		kind: !="todo"
		origin: role: #Text
		body:     #Text
		reply_to: #Text
		effort:   #Effort
		if kind == "decide" {
			options: list.MinItems(2)
			recommendation: {...}
		}
	}
	if status == "snoozed" {
		snooze_until: #Time
	}
	if status == "open" || status == "snoozed" {
		resolution: null
	}
	if status == "done" || status == "cancelled" {
		resolution: #Resolution
		if resolution.choice != null {
			_choiceKnown: list.Contains(_optionKeys, resolution.choice) & true
		}
	}
	if status == "cancelled" {
		resolution: note: #Text
	}
	...
}
