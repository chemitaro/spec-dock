from spec_dock.runtime.domain.active_links import LinkPlan, plan_links


def test_issue_selection_links_every_role_to_its_scope_directory() -> None:
    chain = (
        ("initiative", "initiatives/init-00001-a"),
        ("epic", "initiatives/init-00001-a/epics/epic-00002-b"),
        ("issue", "initiatives/init-00001-a/epics/epic-00002-b/issues/iss-00003-c"),
    )
    assert plan_links(chain) == (
        LinkPlan("initiative", "initiatives/init-00001-a"),
        LinkPlan("epic", "initiatives/init-00001-a/epics/epic-00002-b"),
        LinkPlan("issue", "initiatives/init-00001-a/epics/epic-00002-b/issues/iss-00003-c"),
    )


def test_roles_below_the_direct_scope_and_empty_selection_use_active_none_fallback() -> None:
    epic_chain = (("initiative", "initiatives/init-00001-a"), ("epic", "initiatives/init-00001-a/epics/epic-00002-b"))
    assert plan_links(epic_chain)[2] == LinkPlan("issue", "system/active-none/issue")
    assert plan_links(()) == (
        LinkPlan("initiative", "system/active-none/initiative"),
        LinkPlan("epic", "system/active-none/epic"),
        LinkPlan("issue", "system/active-none/issue"),
    )
