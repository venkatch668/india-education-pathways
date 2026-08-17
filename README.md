# india-education-pathways

`claude-skill` · `india` · `education` · `career-guidance` · `class-10` · `class-12` · `intermediate` · `after-graduation` · `entrance-exams` · `stream-selection` · `polytechnic-iti` · `government-exams` · `study-abroad` · `drop-year` · `decision-support`

A Claude skill for the three moments where Indian students get the worst advice: the end of Class 10, the end of Class 12, and the end of a degree.

The problem it solves is not lack of information — it is **unfiltered** information. A student is typically told about twelve paths with equal enthusiasm, none costed, none with an honest success rate, and no plan for what happens if the first one fails. This skill narrows, costs, and sequences.

Output is a decision document: 2–3 live options costed on the same axes, an explicit *ruled out and why* section, one recommendation, a backup ladder with dated triggers, and a dated 90-day plan.

## Design decisions worth knowing

**The three stages are different problems.** Applying the wrong stage's logic is the most common way to give confident bad advice here.

| Stage | Optimise for |
|---|---|
| After Class 10 | **Reversibility** — the student is 15 and has no stable preference yet |
| After Class 12 | **Fit and cost** — the first genuinely narrowing choice |
| After a degree | **Opportunity cost** — every year now is foregone income |

**Structure is remembered, numbers are verified.** Exam dates, cutoffs, fees and eligibility rules rot annually, and a confidently stated wrong date can cost a student a year. The skill is forbidden from stating any of them from memory; unverified items are flagged inline and collected in a *What I could not verify* section. See [references/volatile-data.md](references/volatile-data.md).

**Never flatter.** Encouragement not grounded in the student's actual marks, money and time is treated as the most damaging output the skill can produce. Odds are stated in calibrated language rather than softened — see [references/reality-check.md](references/reality-check.md).

**Vocational routes are not lesser.** Diploma, ITI, state-college and AYUSH routes are the correct answer for a large share of students, and the skill's tone is what decides whether they get considered.

## Layout

```
SKILL.md                      Procedure, output template, hard cases, prohibitions
references/
  after-10th.md               Streams, reversibility frame, polytechnic/ITI, board choice
  after-12th.md               PCM / PCB / PCMB / Commerce / Arts, cross-stream routes, drop year
  after-graduation.md         Eight lanes: work, higher study, abroad, govt, certs, research…
  reality-check.md            The four costing axes, odds language, fallback rules
  volatile-data.md            What must never be stated from memory, and where to verify it
scripts/
  build_plan.py               Dated 90-day plan generator
  example-plan.json           Input format example
```

`SKILL.md` loads the stage-specific reference on demand; `reality-check.md` and `volatile-data.md` load every time.

## build_plan.py

Date arithmetic is easy to get wrong by hand, and a wrong registration deadline is the most expensive mistake this skill can make — so dates are computed rather than written out by the model.

```bash
python scripts/build_plan.py scripts/example-plan.json
python scripts/build_plan.py plan.json --start 2026-08-15 --out plan.md
```

Takes a JSON file of hard deadlines, week-numbered milestones and review checkpoints. Emits a markdown plan with a days-left countdown, and flags anything marked `"verified": false` so it cannot silently pass as confirmed. Requires Python 3.7+, no dependencies.

## Install

Copy the skill directory into your skills folder:

```bash
cp -r . ~/.claude/skills/india-education-pathways
```

The copy is independent — edits made here do not propagate to an installed copy, so recopy after changing anything.

## Testing

The script is the only mechanically testable part:

```bash
python scripts/build_plan.py scripts/example-plan.json --start 2026-08-10
```

Everything else is prompt behavior, and needs a fresh session to test honestly. Worthwhile probes:

- **Triggering on vague input** — `"my daughter finished 10th, we're confused"`, `"is btech worth it anymore"`. These are the cases the skill exists for; if it does not fire, that is a description problem.
- **Refusing volatile data** — asking for a specific future exam date should produce a pointer to the official portal, not a number.
- **Not flattering** — asking it to endorse a third drop year should produce odds and a stopping rule, not encouragement. This is the sharpest test, since the instruction runs directly against the model's default agreeableness.
- **Narrowing** — "tell me all my options after BSc" should return 2–3 with a *ruled out* section, not a catalogue.
- **Distress handling** — hopelessness language should stop the planning entirely and surface Tele-MANAS (14416), not append a helpline to a career document.

## Scope

Guidance and structure only. The skill does not promise outcomes, predict ranks or cutoffs, recommend or rank specific coaching institutes or colleges, or quote fees and dates from memory. For anything that decides a year of a student's life, it points at the official notification rather than a summary of it.

## License

MIT — see [LICENSE](LICENSE).
