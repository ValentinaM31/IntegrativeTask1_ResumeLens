"""Render a standalone HTML report only after successful textX validation."""
from html import escape
from .dsl import parse_candidate_dsl


def render_candidate_html(dsl_source):
    """Parse the DSL before rendering; display candidate values as escaped text."""
    candidate = parse_candidate_dsl(dsl_source)
    name = escape(candidate["name"] or "Unnamed candidate")

    def records(values):
        if not values:
            return '<p class="empty">None recorded.</p>'
        return "<ul>" + "".join("<li>" + escape(value) + "</li>" for value in values) + "</ul>"

    def badges(values, empty):
        if not values:
            return '<p class="empty">' + empty + "</p>"
        return '<ul class="badges">' + "".join(
            "<li>" + escape(value.replace("_", " ")) + "</li>" for value in values
        ) + "</ul>"

    contacts = records([item["kind"].title() + ": " + item["value"] for item in candidate["contacts"]])
    education = records(candidate["education"])
    experience = records(candidate["experience"])
    skills = badges(candidate["skills"], "No cataloged qualifications recorded.")
    profiles = badges(candidate["accepted_profiles"], "No profile meets all required groups.")
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ResumeLens — {name}</title>
<style>
:root{{color-scheme:light;--ink:#19313e;--muted:#546a75;--line:#dae5e8}}
*{{box-sizing:border-box}}body{{margin:0;background:#edf3f4;color:var(--ink);font:16px/1.65 system-ui,sans-serif}}
main{{max-width:980px;margin:40px auto;background:white;border:1px solid var(--line);border-radius:18px;overflow:hidden}}
header{{padding:34px 40px;background:#123e4d;color:white}}header p{{margin:0;color:#b9dfe2}}
h1{{margin:12px 0 6px;font-size:clamp(28px,5vw,42px);line-height:1.25;overflow-wrap:anywhere}}
.label{{font-size:13px;letter-spacing:.12em;text-transform:uppercase}}
.content{{padding:12px 40px 28px}}section{{padding:20px 0;border-bottom:1px solid var(--line)}}
h2{{font-size:19px;margin:0 0 10px}}ul{{margin:0;padding-left:22px}}li{{overflow-wrap:anywhere}}
.empty{{color:var(--muted);margin:0}}.badges{{display:flex;flex-wrap:wrap;gap:8px;padding:0;list-style:none}}
.badges li{{border-radius:7px;background:#edf5f6;border:1px solid #d4e7e9;padding:5px 11px;font-size:13px;font-weight:600}}
.profiles .badges li{{background:#dff2e9;border-color:#c3e1d2;color:#20513c}}
.columns{{display:grid;grid-template-columns:1fr 1fr;gap:28px}}footer{{padding:20px 40px;background:#f6f9fa;color:var(--muted);font-size:13px}}
footer p{{margin:0}}@media(max-width:640px){{main{{margin:12px;border-radius:12px}}header,.content,footer{{padding-left:20px;padding-right:20px}}.columns{{grid-template-columns:1fr;gap:0}}}}
@media print{{body{{background:white}}main{{margin:0;border:0}}header{{background:white;color:var(--ink)}}header p{{color:var(--muted)}}}}
</style>
</head>
<body>
<main>
<header><p class="label">ResumeLens · Candidate report</p><h1>{name}</h1><p>Qualifications and profile matches</p></header>
<div class="content">
<section class="profiles"><h2>Accepted professional profiles</h2>{profiles}</section>
<section><h2>Normalized qualifications</h2>{skills}</section>
<section><h2>Contact information</h2>{contacts}</section>
<div class="columns"><section><h2>Education</h2>{education}</section><section><h2>Experience</h2>{experience}</section></div>
</div>
<footer><p>Profiles reflect explicit qualifications and the team's documented patterns. Several profiles may apply. Records retain the submitted wording; no proficiency score or hiring decision is inferred.</p></footer>
</main>
</body>
</html>
'''
