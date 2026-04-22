# SESSION HANDOFF - YYYY-MM-DD [short title]

From: [agent/session name]
To: next agent / next session

---

## STATUS

- `DONE` | `PARTIAL` | `BLOCKED`

---

## SESSION GOAL

- What this session was trying to achieve.
- Keep this scoped and specific.

---

## MUST-READ CONTEXT FIRST

Mark what the next agent must read before changing anything important.

- [ ] `context.md`
- [ ] `[file/path]`
- [ ] `[previous handoff path]`
- [ ] `[any decision doc / issue / PR note]`

---

## SCOPE COMPLETED

- [ ] Completed item 1
- [ ] Completed item 2
- [ ] Completed item 3

---

## NOT COMPLETED

- [ ] Pending item 1
- [ ] Pending item 2

If blocked:

- Blocker:
- What is needed to unblock:

---

## DECISIONS LOCKED THIS SESSION

Use this section for decisions that future agents must not silently undo.

| # | Decision | Why | Files / Areas Affected |
|---|----------|-----|------------------------|
| 1 | [decision] | [reason] | [file/area] |
| 2 | [decision] | [reason] | [file/area] |

---

## BUGS FIXED THIS SESSION

Document every fix so the same bug is not “rediscovered” later.

| # | Symptom | Root Cause | Fix | Files |
|---|---------|------------|-----|-------|
| 1 | [what broke] | [why it broke] | [what changed] | [files] |
| 2 | [what broke] | [why it broke] | [what changed] | [files] |

---

## DO NOT REPEAT / DO NOT BREAK AGAIN

This is the anti-regression memory section.

- Do not [repeat wrong assumption].
- Do not [revert important behavior].
- Do not [touch file/logic] without checking [dependency/context].
- If changing [area], re-test [behavior].

Add anything that would save the next agent from wasting a round on a known trap.

---

## FILES CHANGED THIS SESSION

| File | Change Type | Why It Changed | Notes |
|------|-------------|----------------|-------|
| `path/file` | created / edited / generated | [reason] | [notes] |

If generated files were updated, say clearly whether they were:

- source-edited
- script-generated
- manually patched

---

## DATA / STATE / OUTPUTS TO KNOW

Use this when the session changed generated data, JSON shape, routes, storage files, or runtime assumptions.

- Canonical source now lives in:
- Generated output updated:
- Data shape changes:
- Route/path changes:
- Compatibility behavior preserved:

---

## VALIDATION PERFORMED

Be explicit. Future agents should know what is actually verified vs assumed.

- [ ] Read-only inspection only
- [ ] Static verification
- [ ] Manual smoke test
- [ ] Script run
- [ ] Build / compile / lint
- [ ] Runtime browser check

Details:

- Command(s) run:
- Result:
- What was not validated:

---

## CURRENT GIT STATE

Fill this in at end of session.

```text
Branch:
Latest commit at session start:
Latest commit at session end:
Working tree status:
Remote sync state:
```

If there are uncommitted changes, list them briefly.

---

## OPEN RISKS

- Risk 1:
- Risk 2:
- Risk 3:

Only list real risks, not generic filler.

---

## NEXT AGENT: DO THIS FIRST

These should be concrete and ordered.

1. [First next step]
2. [Second next step]
3. [Third next step]

---

## OPTIONAL: SUGGESTED FOLLOW-UP IMPROVEMENTS

Only include if useful and clearly separate from required next steps.

- [nice-to-have]
- [cleanup idea]

---

## SESSION NOTES

Use this for important nuance that does not fit elsewhere:

- stakeholder preference
- rejected approach
- naming constraint
- UI/UX expectation
- environment weirdness

---

## END-OF-SESSION CHECKLIST

Before closing the session, confirm:

- [ ] Important decisions were recorded
- [ ] Bugs and root causes were recorded
- [ ] Validation status is truthful
- [ ] Next steps are explicit
- [ ] Risks / traps are documented
- [ ] `context.md` was updated if project truth changed

---

End time: `[timestamp]`
Session owner: `[name]`
