#!/usr/bin/env python3
"""Build a dated 90-day action plan from a milestones file.

Date arithmetic is easy to get wrong by hand, and a wrong registration deadline
in a student's plan is the most expensive kind of mistake this skill can make.
So the dates are computed here rather than written out by the model.

Usage:
    python build_plan.py plan.json
    python build_plan.py plan.json --start 2026-08-15 --out plan.md

Input format (JSON):

{
  "student": "Class 12 PCM, Telangana",
  "primary_path": "State CET engineering admission",
  "hard_deadlines": [
    {"date": "2026-09-20", "what": "TS EAMCET counselling registration closes",
     "source": "tgeapcet.nic.in", "verified": false}
  ],
  "milestones": [
    {"week": 1,  "what": "Collect caste, income and domicile certificates"},
    {"week": 3,  "what": "Shortlist 15 colleges by branch and fee"},
    {"week": 6,  "what": "First full mock, review with a teacher"}
  ],
  "review_points": [
    {"week": 6, "question": "Are mock scores moving?",
     "if_no": "Switch to the Plan B shortlist this week."}
  ]
}

Every field except "milestones" is optional. Anything with "verified": false is
flagged in the output so it cannot silently pass as confirmed.
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def week_range(start, week_no):
    """Return (monday, sunday) for the given 1-indexed week from start."""
    first_monday = start - timedelta(days=start.weekday())
    monday = first_monday + timedelta(weeks=week_no - 1)
    return monday, monday + timedelta(days=6)


def fmt(d):
    return d.strftime("%d %b %Y")


def build(plan, start):
    end = start + timedelta(days=90)
    out = []

    title = plan.get("primary_path", "Next 90 days")
    out.append(f"# Next 90 days — {title}")
    out.append("")
    if plan.get("student"):
        out.append(f"*{plan['student']}*")
        out.append("")
    out.append(f"**Window:** {fmt(start)} → {fmt(end)}")
    out.append("")

    deadlines = sorted(
        plan.get("hard_deadlines", []), key=lambda d: parse_date(d["date"])
    )
    if deadlines:
        out.append("## Hard deadlines")
        out.append("")
        out.append("| Date | Days left | What | Source | Verified |")
        out.append("|---|---|---|---|---|")
        for d in deadlines:
            when = parse_date(d["date"])
            days = (when - start).days
            if days < 0:
                left = "**PASSED**"
            elif days <= 14:
                left = f"**{days} days**"
            else:
                left = f"{days} days"
            mark = "yes" if d.get("verified") else "**NOT VERIFIED**"
            out.append(
                f"| {fmt(when)} | {left} | {d['what']} | "
                f"{d.get('source', '—')} | {mark} |"
            )
        out.append("")

    milestones = plan.get("milestones", [])
    reviews = {r["week"]: r for r in plan.get("review_points", [])}

    if milestones:
        by_week = {}
        for m in milestones:
            by_week.setdefault(int(m["week"]), []).append(m["what"])

        out.append("## Week by week")
        out.append("")
        all_weeks = sorted(set(list(by_week) + list(reviews)))
        outside = [w for w in all_weeks if w < 1 or w > 13]
        if outside:
            print(
                f"warning: ignoring items outside the 90-day window "
                f"(weeks {', '.join(str(w) for w in outside)}; valid range 1-13)",
                file=sys.stderr,
            )

        for wk in all_weeks:
            if wk < 1 or wk > 13:
                continue
            mon, sun = week_range(start, wk)
            out.append(f"### Week {wk} — {fmt(mon)} to {fmt(sun)}")
            out.append("")
            for item in by_week.get(wk, []):
                out.append(f"- [ ] {item}")
            if wk in reviews:
                r = reviews[wk]
                out.append("")
                out.append(f"> **Checkpoint:** {r['question']}")
                if r.get("if_no"):
                    out.append(f"> If the answer is no: {r['if_no']}")
            out.append("")

    unverified = [d for d in deadlines if not d.get("verified")]
    if unverified:
        out.append("## Verify before relying on this")
        out.append("")
        for d in unverified:
            out.append(
                f"- {d['what']} — listed as {fmt(parse_date(d['date']))}. "
                f"Confirm at {d.get('source', 'the official portal')}."
            )
        out.append("")

    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan", help="Path to the milestones JSON file")
    ap.add_argument("--start", help="Start date YYYY-MM-DD (default: today)")
    ap.add_argument("--out", help="Write markdown here instead of stdout")
    args = ap.parse_args()

    try:
        with open(args.plan, encoding="utf-8") as fh:
            plan = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"Could not read plan file: {exc}")

    start = parse_date(args.start) if args.start else date.today()
    text = build(plan, start)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Wrote {args.out}")
    else:
        # The output contains arrows and em dashes; a Windows console defaults
        # to cp1252 and would raise UnicodeEncodeError on them.
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(text)


if __name__ == "__main__":
    main()
