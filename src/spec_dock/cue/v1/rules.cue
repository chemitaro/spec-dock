// SpecDock spec type specdock/v1: connection rules (R-B3; rule table of design.md, contract K2).
//
// Work units are the steps of an Issue and the slices of an Epic or Initiative; the map the kind does
// not use is empty, so one formula serves every kind. A dropped step counts for nothing but its
// references are still checked. References are plain strings: a missing target is a finding, not a
// shape error, because a disjunction over every existing number makes unreadable errors.
package spec

import "list"

_specdock: {
	requirementIDs: [for k, _ in requirements {k}]
	failureIDs: [for k, _ in failures {k}]
	targets: list.Concat([requirementIDs, failureIDs])
	stepIDs: [for k, _ in steps {k}]
	sliceIDs: [for k, _ in slices {k}]
	unitIDs: list.Concat([stepIDs, sliceIDs])

	// Numbers that a live work unit realizes or covers.
	realized: list.Concat([
		[for _, s in steps if s.status != "dropped" for r in s.realizes {r}],
		[for _, s in slices for r in s.covers {r}],
	])
	designed: [for _, d in design for r in d.satisfies {r}]
	// Numbers verified: an Issue's tests, or what an Epic or Initiative hands to a child.
	verified: list.Concat([
		[for _, t in tests for r in t.verifies {r}],
		[for _, s in slices for r in s.covers {r}],
	])

	sessionNames: [if execution != _|_ if execution.sessions != _|_ for name, _ in execution.sessions {name}]
	sessionUsers: list.Concat([
		[for k, s in steps if s.session != _|_ {id: k, session: s.session}],
		[for k, s in slices if s.session != _|_ {id: k, session: s.session}],
	])
	usesExecution: execution != _|_ || len(sessionUsers) > 0

	// Words for hints, by kind.
	unitField: [if _specdock.issue {"steps"}, "slices"][0]
	unitLink: [if _specdock.issue {"realizes"}, "covers"][0]
	testField: [if _specdock.issue {"tests"}, "slices"][0]
	testLink: [if _specdock.issue {"verifies"}, "covers"][0]

	// Findings sorted by id, then message, so the same documents give the same list.
	sort: {
		x:    _
		y:    _
		less: x.id < y.id || (x.id == y.id && x.message < y.message)
	}
}

findings: {
	"unknown-reference": list.Sort(list.Concat([
		[for k, d in design for r in d.satisfies if !list.Contains(_specdock.targets, r) {
			id:      k
			message: "design.\"\(k)\".satisfies の \"\(r)\" は、requirements と failures にない番号です"
			hint:    "requirement.cue に \"\(r)\" を足すか、design.cue の design.\"\(k)\".satisfies から外す"
		}],
		[for k, s in steps for r in s.realizes if !list.Contains(_specdock.targets, r) {
			id:      k
			message: "steps.\"\(k)\".realizes の \"\(r)\" は、requirements と failures にない番号です"
			hint:    "requirement.cue に \"\(r)\" を足すか、plan.cue の steps.\"\(k)\".realizes から外す"
		}],
		[for k, s in steps if s.after != _|_ for r in s.after if !list.Contains(_specdock.stepIDs, r) {
			id:      k
			message: "steps.\"\(k)\".after の \"\(r)\" は、steps にない手順です"
			hint:    "plan.cue の steps に \"\(r)\" を足すか、steps.\"\(k)\".after から外す"
		}],
		[for k, t in tests for r in t.verifies if !list.Contains(_specdock.targets, r) {
			id:      k
			message: "tests.\"\(k)\".verifies の \"\(r)\" は、requirements と failures にない番号です"
			hint:    "requirement.cue に \"\(r)\" を足すか、plan.cue の tests.\"\(k)\".verifies から外す"
		}],
		[for k, s in slices for r in s.covers if !list.Contains(_specdock.targets, r) {
			id:      k
			message: "slices.\"\(k)\".covers の \"\(r)\" は、requirements と failures にない番号です"
			hint:    "requirement.cue に \"\(r)\" を足すか、plan.cue の slices.\"\(k)\".covers から外す"
		}],
		[for k, s in slices if s.after != _|_ for r in s.after if !list.Contains(_specdock.sliceIDs, r) {
			id:      k
			message: "slices.\"\(k)\".after の \"\(r)\" は、slices にない切り分けです"
			hint:    "plan.cue の slices に \"\(r)\" を足すか、slices.\"\(k)\".after から外す"
		}],
	]), _specdock.sort)

	"requirement-without-step": list.Sort([for k in _specdock.requirementIDs if !list.Contains(_specdock.realized, k) {
		id: k
		if _specdock.issue {
			message: "\(k) を満たす手順がありません（取り下げた手順は数えません）"
		}
		if !_specdock.issue {
			message: "\(k) を任せた子の Scope がありません"
		}
		hint: "plan.cue の \(_specdock.unitField) に、\(_specdock.unitLink) に \"\(k)\" を含む項目を足す"
	}], _specdock.sort)

	if _rank >= 1 {
		"requirement-without-design": list.Sort([for k in _specdock.requirementIDs if !list.Contains(_specdock.designed, k) {
			id:      k
			message: "\(k) を満たす設計がありません"
			hint:    "design.cue の design に、satisfies に \"\(k)\" を含む項目を足す"
		}], _specdock.sort)

		"requirement-without-test": list.Sort([for k in _specdock.requirementIDs if !list.Contains(_specdock.verified, k) {
			id: k
			if _specdock.issue {
				message: "\(k) を確かめるテストがありません"
			}
			if !_specdock.issue {
				message: "\(k) を確かめる子の Scope がありません"
			}
			hint: "plan.cue の \(_specdock.testField) に、\(_specdock.testLink) に \"\(k)\" を含む項目を足す"
		}], _specdock.sort)
	}

	if _rank >= 2 {
		"orphan-step": list.Sort(list.Concat([
			[for k, s in steps if s.status != "dropped" if len(s.realizes) == 0 {
				id:      k
				message: "\(k) は、どの要件にも結び付いていません"
				hint:    "plan.cue の steps.\"\(k)\".realizes に、この手順が満たす要件の番号を書く（要らない手順なら status を \"dropped\" にする）"
			}],
			[for k, s in slices if len(s.covers) == 0 {
				id:      k
				message: "\(k) は、どの要件も任されていません"
				hint:    "plan.cue の slices.\"\(k)\".covers に、この子に任せる要件の番号を書く"
			}],
		]), _specdock.sort)

		"failure-without-test": list.Sort([for k in _specdock.failureIDs if !list.Contains(_specdock.verified, k) {
			id: k
			if _specdock.issue {
				message: "\(k) を確かめるテストがありません"
			}
			if !_specdock.issue {
				message: "\(k) を確かめる子の Scope がありません"
			}
			hint: "plan.cue の \(_specdock.testField) に、\(_specdock.testLink) に \"\(k)\" を含む項目を足す"
		}], _specdock.sort)
	}

	if _rank >= 3 {
		"rollback-missing": [if rollback == _|_ if len(_specdock.unitIDs) > 0 {
			id:      "rollback"
			message: "戻し方（rollback）がありません"
			hint:    "plan.cue に rollback を書く"
		}]
	}

	if _specdock.usesExecution {
		"execution-reference": list.Sort(list.Concat([
			[for user in _specdock.sessionUsers if !list.Contains(_specdock.sessionNames, user.session) {
				id:      user.id
				message: "\(user.id) の session \"\(user.session)\" は、execution.sessions にありません"
				hint:    "plan.cue の execution.sessions に \"\(user.session)\" を足すか、\(_specdock.unitField).\"\(user.id)\".session を直す"
			}],
			[if execution != _|_ if execution.reviews != _|_ for name, r in execution.reviews if r.after != _|_ if !list.Contains(_specdock.unitIDs, r.after) {
				id:      "execution.reviews.\(name)"
				message: "レビュー \(name) の after \"\(r.after)\" は、\(_specdock.unitField) にありません"
				hint:    "plan.cue の execution.reviews.\(name).after を、\(_specdock.unitField) にある番号にする"
			}],
		]), _specdock.sort)
	}
}
