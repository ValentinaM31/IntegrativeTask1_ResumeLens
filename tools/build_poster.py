"""Build a complete research poster, its animated walkthrough and an optional PDF."""
import argparse
import hashlib
from html import escape
import json
import math
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/poster'
W, H = 1920, 1358
PAGE_WIDTH_MM, PAGE_HEIGHT_MM = 841, 594
INK, MUTED = '#172f3d', '#536977'
PURPLE, TEAL = '#183d56', '#087f7c'
BLUE, GOLD = PURPLE, INK
PROJECT_URL = 'https://github.com/ValentinaM31/IntegrativeTask1_ResumeLens'
FONT_ROLES = {'title': 82, 'authors': 49, 'headings': 36, 'body': 26}


class Scene:
    def __init__(self):
        self.parts = []
        self.operations = []

    def group(self, identifier):
        self.parts.append(f'<g id="{identifier}" class="stage-panel">')

    def end_group(self):
        self.parts.append('</g>')

    def rect(self, x, y, width, height, fill, radius=0, stroke=None):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke or "none"}"/>')
        self.operations.append(('rect', x, y, width, height, fill, radius, stroke))

    def text(self, x, y, value, size=20, fill=INK, bold=False, mono=False, anchor='start'):
        value = str(value)
        font = 'Consolas,monospace' if mono else 'Arial,sans-serif'
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}" text-anchor="{anchor}">{escape(value)}</text>')
        self.operations.append(('text', x, y, value, size, fill, bold, mono, anchor))

    def paragraph(self, x, y, value, width=520, size=20, fill=MUTED):
        for line in textwrap.wrap(value, width=int(width / (size * .54)), break_long_words=False):
            self.text(x, y, line, size, fill)
            y += size * 1.34
        return y

    def line(self, x1, y1, x2, y2, fill=MUTED, width=2):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{fill}" stroke-width="{width}"/>')
        self.operations.append(('line', x1, y1, x2, y2, fill, width))

    def circle(self, x, y, radius, fill, stroke=None):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="2"/>')
        self.operations.append(('circle', x, y, radius, fill, stroke))

    def arrow(self, x1, y, x2, fill=PURPLE):
        self.line(x1, y, x2 - 9, y, fill, 2)
        points = [(x2, y), (x2 - 10, y - 5), (x2 - 10, y + 5)]
        self.parts.append(f'<polygon points="{" ".join(f"{x},{py}" for x,py in points)}" fill="{fill}"/>')
        self.operations.append(('polygon', points, fill))

    def arrow_to(self, x1, y1, x2, y2, fill=PURPLE):
        length = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        bx, by = x2 - 10 * ux, y2 - 10 * uy
        self.line(x1, y1, bx, by, fill, 3)
        points = [(x2, y2), (bx - 5 * uy, by + 5 * ux),
                  (bx + 5 * uy, by - 5 * ux)]
        self.parts.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in points)}" fill="{fill}"/>')
        self.operations.append(('polygon', points, fill))

    def curve(self, points, fill=TEAL, width=2.5):
        """Draw the same cubic Bezier curve in SVG and the vector PDF."""
        (x0,y0),(x1,y1),(x2,y2),(x3,y3) = points
        self.parts.append(f'<path d="M{x0},{y0} C{x1},{y1} {x2},{y2} {x3},{y3}" fill="none" stroke="{fill}" stroke-width="{width}"/>')
        self.operations.append(('curve', points, fill, width))

    def check(self, x, y, accepted=True, fill=TEAL):
        self.circle(x, y, 15, fill if accepted else '#fff', fill)
        if accepted:
            self.line(x-7, y, x-1, y+6, '#fff', 3)
            self.line(x-1, y+6, x+8, y-7, '#fff', 3)
        else:
            self.line(x-6, y-6, x+6, y+6, fill, 3)
            self.line(x-6, y+6, x+6, y-6, fill, 3)

    def link_text(self, x, y, value, url, size=26):
        self.parts.append(f'<a href="{escape(url, quote=True)}">')
        self.text(x, y, value, size, PURPLE)
        self.parts.append('</a>')
        self.operations.append(('link', url, x, y - size,
                                len(value) * size * .6, size * 1.25))

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_WIDTH_MM}mm" height="{PAGE_HEIGHT_MM}mm" viewBox="0 0 {W} {H}" role="img" aria-labelledby="poster-title poster-desc">'
                '<title id="poster-title">ResumeLens: traceable evidence and deterministic profile recognition</title>'
                '<desc id="poster-desc">Three-column research poster with a worked resume, an alias transducer path, accepted and rejected DFA traces, a grammar rule, a validated candidate report and separate synthetic evaluation results.</desc>'
                + '\n'.join(self.parts) + '</svg>')

    def pdf(self, destination):
        from reportlab.pdfgen import canvas
        from reportlab.lib.colors import HexColor
        def color(value):
            if len(value) == 4:
                value = '#' + ''.join(character * 2 for character in value[1:])
            return HexColor(value)
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        fonts = [('C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/consola.ttf'),
                 ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')]
        selected = next((paths for paths in fonts if all(Path(path).exists() for path in paths)), None)
        if selected is None:
            raise RuntimeError('PDF export needs Arial or DejaVu TrueType fonts for formal-model symbols')
        for name, path in zip(('PosterRegular', 'PosterBold', 'PosterMono'), selected):
            pdfmetrics.registerFont(TTFont(name, path))
        document = canvas.Canvas(str(destination), pagesize=(PAGE_WIDTH_MM * mm, PAGE_HEIGHT_MM * mm))
        document.setTitle('ResumeLens - Formal language models and verified results')
        document.setAuthor('Valentina Martinez Franco and Juan Pino')
        scale = min(PAGE_WIDTH_MM * mm / W, PAGE_HEIGHT_MM * mm / H)
        document.translate((PAGE_WIDTH_MM * mm - W * scale) / 2,
                           (PAGE_HEIGHT_MM * mm - H * scale) / 2)
        document.scale(scale, scale)
        for operation in self.operations:
            kind, *args = operation
            if kind == 'rect':
                x,y,width,height,fill,radius,stroke=args
                document.setFillColor(color(fill))
                if stroke: document.setStrokeColor(color(stroke))
                document.roundRect(x,H-y-height,width,height,radius,stroke=bool(stroke),fill=1)
            elif kind == 'text':
                x,y,value,size,fill,bold,mono,anchor=args
                document.setFillColor(color(fill))
                document.setFont('PosterMono' if mono else 'PosterBold' if bold else 'PosterRegular',size)
                draw = document.drawCentredString if anchor == 'middle' else document.drawRightString if anchor == 'end' else document.drawString
                draw(x,H-y,value)
            elif kind == 'line':
                x1,y1,x2,y2,fill,width=args
                document.setStrokeColor(color(fill));document.setLineWidth(width)
                document.line(x1,H-y1,x2,H-y2)
            elif kind == 'circle':
                x,y,radius,fill,stroke=args
                document.setFillColor(color(fill))
                if stroke: document.setStrokeColor(color(stroke))
                document.setLineWidth(2)
                document.circle(x,H-y,radius,stroke=bool(stroke),fill=1)
            elif kind == 'polygon':
                points,fill=args
                document.setFillColor(color(fill));path=document.beginPath()
                path.moveTo(points[0][0],H-points[0][1])
                for x,y in points[1:]:path.lineTo(x,H-y)
                path.close();document.drawPath(path,stroke=0,fill=1)
            elif kind == 'curve':
                points,fill,width=args
                document.setStrokeColor(color(fill));document.setLineWidth(width)
                path=document.beginPath();path.moveTo(points[0][0],H-points[0][1])
                path.curveTo(points[1][0],H-points[1][1],points[2][0],H-points[2][1],points[3][0],H-points[3][1])
                document.drawPath(path,stroke=1,fill=0)
            elif kind == 'link':
                url, x, y, width, height = args
                document.linkURL(url, (x, H-y-height, x+width, H-y), relative=1)
        document.showPage();document.save()


def build_scene():
    read = lambda path: json.loads((ROOT / path).read_text(encoding='utf-8'))
    first = read('data/results/01_full_stack.json')
    classification = read('data/classification/01_full_stack.json')
    model = read('docs/automata/FULL_STACK_DEVELOPER.json')
    delta = {(source, symbol): target for source, symbol, target in model['delta']}
    sequence = next(row['sequence'] for row in classification['profiles']
                    if row['profile'] == 'FULL_STACK_DEVELOPER')
    state, path = model['q0'], [model['q0']]
    for symbol in sequence:
        state = delta[state, symbol]
        path.append(state)
    if model['type'] != 'DFA' or path != ['q0', 'q1', 'q2', 'q3', 'q4', 'q5'] or state not in model['F']:
        raise ValueError('The worked poster trace must match the exported Full Stack DFA')
    if delta['q1', 'NODE_JS'] != model['sink']:
        raise ValueError('The missing-frontend trace must reach the actual rejecting sink')
    pre = read('data/preannotated-evaluation/visual-update/results.json')
    workflow = read('data/workflow-evaluation/visual-update/results.json')
    verification_path = DEST / 'verification.json'
    verified = json.loads(verification_path.read_text(encoding='utf-8')) if verification_path.exists() else {}
    current_paths = {p.relative_to(ROOT).as_posix() for folder in ('src/resumelens', 'tests')
                     for p in (ROOT / folder).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts
                     and p.suffix in ('.py', '.json', '.tx', '.html', '.css', '.js', '.txt')}
    hashes = verified.get('source_sha256', {})
    fresh = (verified.get('status') == 'passed' and set(hashes) == current_paths
             and all(hashlib.sha256((ROOT / p).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == value
                     for p, value in hashes.items()))
    evidence_paths = ('data/preannotated-evaluation/visual-update/results.json',
                      'data/workflow-evaluation/visual-update/results.json',
                      'tools/evaluate_preannotated.py', 'tools/evaluate_workflow.py')
    evaluation_hashes = verified.get('evaluation_sha256', {})
    fresh = fresh and set(evaluation_hashes) == set(evidence_paths) and all(
        hashlib.sha256((ROOT / p).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == value
        for p, value in evaluation_hashes.items())
    rows = pre['results'] if 'results' in pre else pre['cases']
    if not isinstance(rows, list):
        raise ValueError('Evaluation requires one annotated result per case')
    outcomes = [row['all_annotations_exact'] for row in rows]
    overall = pre['summary']['overall']
    if len(outcomes) != overall['cases'] or sum(outcomes) != overall['all_annotations_exact']:
        raise ValueError('The poster case grid must reproduce the actual evaluation outcomes')
    s = Scene()
    s.rect(0, 0, W, H, '#fff')
    s.rect(64, 44, 7, 161, TEAL, 3)
    s.text(90, 62, 'ICESI UNIVERSITY / COMPUTING & DISCRETE STRUCTURES III', 26, MUTED)
    s.text(88, 147, 'ResumeLens', FONT_ROLES['title'], PURPLE, True)
    s.text(90, 198, 'From skill mentions to verified profiles.', 36, INK)
    s.text(1160, 63, 'RESEARCH QUESTION', 26, TEAL, True)
    s.text(1160, 113, 'Can formal models keep', 34, INK, True)
    s.text(1160, 160, 'profile decisions traceable?', 34, INK, True)
    s.text(1160, 202, 'Explicit rules. Original evidence.', 26, MUTED)
    s.text(70, 270, 'Valentina Martinez Franco', FONT_ROLES['authors'], INK, True)
    s.text(1320, 270, 'Juan Pino', FONT_ROLES['authors'], INK, True)
    stages = [('Resume', 'Original text'), ('Regex', 'Evidence spans'),
              ('Transducers', 'Canonical symbols'), ('DFA', 'Profile decisions'),
              ('textX', 'Validated DSL'), ('HTML', 'Candidate report')]
    for i, (title, subtitle) in enumerate(stages):
        x = 70 + i * 300
        s.rect(x, 307, 272, 77, '#eef5f6', 8)
        s.text(x + 16, 338, title, 28, TEAL if i in (2, 3) else PURPLE, True)
        s.text(x + 16, 368, subtitle, 26, INK)
        if i < 5:
            s.arrow_to(x + 279, 345, x + 294, 345, MUTED)
    s.line(650, 411, 650, 1150, '#dce5e9', 2)
    s.line(1257, 411, 1257, 1150, '#dce5e9', 2)

    # One source sample, with original text/evidence retained before normalization.
    s.group('stage-extract')
    s.text(70, 441, '01  Preserve & normalize', 36, PURPLE, True)
    s.rect(70, 472, 550, 163, '#f0f5f8', 9)
    s.text(94, 515, first['candidate']['name'], 32, INK, True)
    s.text(94, 555, 'Technical Skills', 26, MUTED)
    s.rect(94, 573, 51, 41, '#d6ece8', 5)
    s.text(101, 602, 'JS', 26, TEAL, True)
    s.text(157, 602, 'React.js · NodeJS · Postgres · Git', 26, INK)
    mention = first['extracted_skills'][0]
    s.text(70, 677, f'text[{mention["start"]}:{mention["end"]}] == "{mention["raw"]}"', 28, TEAL, True, True)
    s.text(70, 713, 'Regex preserves wording and positions.', 26, INK)
    s.end_group()
    s.group('stage-normalize')
    s.text(70, 766, 'Finite-state transducer (FST)', 30, PURPLE, True)
    s.text(70, 808, 'M = (Q, Σ, Γ, δ, ω, q0, F)', 29, INK)
    for i, x in enumerate((125, 335, 550)):
        s.circle(x, 899, 29, '#eef5f6', PURPLE)
        if i == 2:
            s.circle(x, 899, 24, '#eef5f6', PURPLE)
        s.text(x, 908, 'q' + str(i), 26, PURPLE, True, anchor='middle')
    s.arrow_to(70, 899, 92, 899, PURPLE)
    s.arrow_to(159, 899, 301, 899, PURPLE)
    s.arrow_to(369, 899, 516, 899, PURPLE)
    s.text(230, 857, 'j / ε', 26, PURPLE, mono=True, anchor='middle')
    s.text(442, 857, 's / JAVASCRIPT', 26, PURPLE, mono=True, anchor='middle')
    s.rect(70, 953, 550, 53, '#e1f0ee', 8)
    s.text(345, 991, 'JS → js → JAVASCRIPT', 30, TEAL, True, anchor='middle')
    s.text(70, 1046, 'ε is empty output; j is consumed.', 26, INK)
    s.text(70, 1085, 'JS path; state names abbreviated.', 26, MUTED)
    s.text(70, 1137, '4 FSTs / 26 symbols / 56 aliases', 28, PURPLE, True)
    s.end_group()

    # Real DFA state names. The two traces are subsets of its total transition function.
    s.group('stage-recognize')
    s.text(684, 441, '02  Recognize the profile', 36, TEAL, True)
    s.text(684, 485, 'Deterministic finite automaton (DFA)', 26, INK)
    s.text(684, 528, 'A = (Q, Σ, δ, q0, F)', 30, TEAL, True)
    s.text(684, 565, 'Full Stack: two executed traces.', 26, INK)
    points = [(720, 669), (930, 669), (1140, 669),
              (1140, 842), (930, 842), (720, 842)]
    for name, (x, y) in zip(path, points):
        s.circle(x, y, 28, '#e1f0ee', TEAL)
        if name in model['F']:
            s.circle(x, y, 23, '#e1f0ee', TEAL)
        s.text(x, y+9, name, 26, TEAL, True, anchor='middle')
    s.arrow_to(680, 669, 688, 669, TEAL)
    s.arrow_to(753, 669, 897, 669, TEAL)
    s.arrow_to(963, 669, 1107, 669, TEAL)
    s.arrow_to(1140, 702, 1140, 809, TEAL)
    s.arrow_to(1107, 842, 963, 842, TEAL)
    s.arrow_to(897, 842, 753, 842, TEAL)
    for x, y, symbol in [(825, 628, sequence[0]), (1035, 628, sequence[1]),
                         (1040, 754, sequence[2]), (1035, 803, sequence[3]),
                         (825, 803, sequence[4])]:
        s.text(x, y, symbol, 25, TEAL, True, mono=True, anchor='middle')
    s.text(684, 899, 'q5 accepts: all five groups are present.', 26, INK)
    s.text(684, 948, 'Missing frontend: same q1, next NODE_JS', 25, INK)
    s.circle(720, 1002, 28, '#f0f5f8', PURPLE)
    s.text(720, 1011, 'q1', 26, PURPLE, True, anchor='middle')
    s.arrow_to(753, 1002, 1107, 1002, PURPLE)
    s.text(930, 984, 'NODE_JS', 26, PURPLE, True, mono=True, anchor='middle')
    s.circle(1140, 1002, 36, '#f0f5f8', PURPLE)
    s.text(1140, 1010, 'q_dead', 21, PURPLE, True, anchor='middle')
    s.curve([(1170, 982), (1235, 940), (1235, 1064), (1170, 1022)], PURPLE)
    s.arrow_to(1180, 1027, 1170, 1022, PURPLE)
    s.text(1223, 1009, 'Σ', 26, PURPLE, True, anchor='middle')
    s.text(684, 1080, 'One token → one next state. No ε edges.', 26, INK)
    s.text(684, 1117, 'Other transitions: see complete models.', 26, MUTED)
    s.text(684, 1154, 'Full Stack / ML / Backend / Data Engineer', 25, TEAL, True)
    s.end_group()

    s.group('stage-validate')
    s.text(1290, 441, '03  Validate & evaluate', 36, PURPLE, True)
    s.text(1290, 485, 'Extended Backus-Naur form (EBNF)', 26, INK)
    s.rect(1290, 513, 562, 103, '#f0f5f8', 8)
    s.text(1308, 552, 'SkillEntry = "skill",', 26, INK, mono=True)
    s.text(1308, 590, '  SkillSymbol, ";" ;', 26, INK, mono=True)
    s.text(1290, 655, 'textX syntax + profile consistency', 26, INK)
    s.text(1290, 698, 'Domain-specific language (DSL) excerpt', 25, MUTED)
    for i, line in enumerate(['accepted_profiles {', '  profile FULL_STACK_DEVELOPER;', '}']):
        s.text(1308, 737+i*33, line, 25, PURPLE, mono=True)
    s.arrow_to(1571, 811, 1571, 829, TEAL)
    s.rect(1290, 836, 562, 105, '#e1f0ee', 9)
    s.text(1314, 875, 'Alex Sample', 30, INK, True)
    s.text(1828, 875, 'HTML', 26, MUTED, anchor='end')
    s.check(1330, 910)
    s.text(1360, 919, 'Full Stack Developer accepted', 28, TEAL, True)
    s.text(1290, 984, 'Separate synthetic evaluations', 29, INK, True)
    s.text(1290, 1065, f'{sum(outcomes)}/{len(outcomes)}' if fresh else 'Pending', 66, TEAL, True)
    s.text(1290, 1105, 'Exact cases', 26, INK)
    s.text(1290, 1141, 'Preannotated dataset', 25, MUTED)
    for i, accepted in enumerate(outcomes):
        x, y = 1586+(i % 6)*44, 1010+(i//6)*43
        case_id = rows[i]['id']
        s.parts.append(f'<g><title>{escape(str(case_id))}: {"exact annotations" if accepted else "annotation differences"}</title>')
        s.check(x, y, accepted if fresh else False, TEAL if fresh else MUTED)
        s.parts.append('</g>')
    s.text(1580, 1141, f'{overall["pipeline_valid"]}/{overall["cases"]} valid pipelines' if fresh else 'Verification pending', 24, INK)
    s.text(1290, 1180, f'{workflow["passed"]}/{workflow["cases"]} workflow regression (separate)' if fresh else 'Workflow verification pending', 26, INK)
    s.end_group()

    s.text(70, 1180, 'Filled check = exact case; cross = difference.', 26, MUTED)
    if fresh:
        s.text(1225, 1180, f'{verified["tests_run"]} tests / {verified["passed"]} pass / {verified["skipped"]} skip', 26, TEAL, True, anchor='end')
    else:
        s.text(1225, 1180, 'Verification snapshot pending', 26, MUTED, anchor='end')
    s.rect(70, 1205, 1782, 69, PURPLE, 9)
    s.text(98, 1252, 'Traceable evidence. Deterministic decisions. Interpretation still has limits.', 36, '#fff', True)
    s.text(70, 1310, 'Known gaps: Rust, double negation, source attribution and Pandas wording. Synthetic results only.', 26, MUTED)
    s.link_text(70, 1347, 'Mohri (1997)', 'https://aclanthology.org/J97-2003/', 22)
    s.link_text(270, 1347, 'Yu, Guan & Zhou (2005)', 'https://aclanthology.org/P05-1062/', 22)
    s.link_text(850, 1347, 'Code / formal models / evaluation methods', PROJECT_URL, 22)
    return s


def walkthrough(svg):
    steps=[('stage-extract','Extract evidence','Regex identifies explicit mentions. JS retains its exact span in the Alex Sample text. Negated or ambiguous mentions are kept separately.'),
           ('stage-normalize','Normalize aliases','Follow j and s through an illustrative FST path. The epsilon output on j emits nothing while consuming j; the final edge emits JAVASCRIPT after the complete alias.'),
           ('stage-recognize','Recognize a profile','Canonical bucket order prepares the skills for a complete DFA. Follow the actual q0 to q5 path, then compare a missing-frontend transition to q_dead. Backend states retain compatible-framework choices.'),
           ('stage-validate','Validate and render','The EBNF defines skill declarations and repeated records. textX checks syntax; semantic checks execute the DFA to verify profile claims. The validated DSL becomes the candidate report. The evaluation grid uses the actual case outcomes.')]
    buttons=''.join(f'<button type="button" data-stage="{identifier}" aria-pressed="false">{title}</button>' for identifier,title,_ in steps)
    data=json.dumps(steps,ensure_ascii=False).replace('<','\\u003c')
    markup = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ResumeLens | Research poster walkthrough</title><style>
    *{box-sizing:border-box}body{margin:0;background:#edf3f5;color:#172f3d;font:15px/1.6 system-ui,sans-serif}.controls{position:sticky;top:10px;z-index:5;max-width:1500px;margin:18px auto;padding:18px 22px;background:white;box-shadow:0 8px 30px #173d5612;border:1px solid #dce5e9;border-radius:14px}.controls h1{font-size:24px;margin:0 0 6px}.controls p{margin:7px 0;color:#536977}.buttons{display:flex;flex-wrap:wrap;gap:9px;margin:16px 0}button{font:600 12px system-ui,sans-serif;padding:10px 13px;color:#183d56;background:#eef5f6;border:1px solid #cddfe5;border-radius:8px;cursor:pointer}button[aria-pressed=true]{background:#087f7c;color:white}button:disabled{opacity:.5;cursor:default}:focus-visible{outline:3px solid #183d56;outline-offset:4px}.poster{max-width:1500px;margin:0 auto 25px;padding:0 18px}.enlarged .poster{width:1956px;max-width:none;margin-left:0;margin-right:0}.poster svg{width:100%;height:auto;background:#fff;border-radius:12px}.stage-panel{transition:opacity .3s}.has-selection .stage-panel{opacity:.38}.has-selection .stage-panel.is-active{opacity:1}.is-active>rect:first-child{stroke:#087f7c;stroke-width:3}.is-active{animation:highlight 1s ease-out}#stage-note{min-height:48px}.note{font-size:12px}.print-link{color:#087f7c;font-weight:600}@keyframes highlight{from{filter:brightness(1.12)}to{filter:none}}@media(max-width:650px){.controls{margin:12px;padding:18px}.poster{padding:0 8px}.controls h1{font-size:21px}}@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}@page{size:POSTER_SIZE landscape;margin:0}@media print{.controls{display:none}.enlarged .poster{width:auto;max-width:none}.poster{padding:0;margin:0;max-width:none}.has-selection .stage-panel{opacity:1}.poster svg{border-radius:0}}
    </style></head><body><section class="controls" aria-label="Poster walkthrough"><h1>Follow one resume through four formal models.</h1><p>Choose a stage, or play the guided walkthrough. Read left to right: source evidence, formal models and validated output. Then compare the separate results.</p><div class="buttons">'''+buttons+'''<button type="button" id="play">Play walkthrough</button><button type="button" id="overview">Show complete poster</button><button type="button" id="enlarge" aria-pressed="false">Enlarge poster</button></div><p id="stage-note" role="status" aria-live="polite">The complete poster shows methodology, formal definitions, separate evaluations and limits.</p><p class="note">Use Enlarge poster for details on small screens. Original labels and observed errors are preserved. Animations respect reduced-motion preferences. <a class="print-link" href="resumelens-poster.pdf">Open printable PDF</a></p></section><main class="poster">'''+svg+'''</main><script>
    const stages='''+data+''';let index=0,timer=null;const buttons=[...document.querySelectorAll('[data-stage]')],play=document.querySelector('#play'),note=document.querySelector('#stage-note');const reduced=matchMedia('(prefers-reduced-motion: reduce)');
    function stop(){clearInterval(timer);timer=null;play.textContent='Play walkthrough'}
    function select(i){index=i;document.querySelector('.poster').classList.add('has-selection');stages.forEach((stage,j)=>{document.getElementById(stage[0]).classList.toggle('is-active',i===j);buttons[j].setAttribute('aria-pressed',String(i===j))});note.textContent=stages[i][1]+': '+stages[i][2];document.getElementById(stages[i][0]).scrollIntoView({behavior:reduced.matches?'instant':'smooth',block:'center'})}
    buttons.forEach((button,i)=>button.addEventListener('click',()=>{stop();select(i)}));play.addEventListener('click',()=>{if(timer){stop();return}if(reduced.matches)return;select(index);play.textContent='Pause walkthrough';timer=setInterval(()=>select((index+1)%stages.length),6500)});
    document.querySelector('#overview').addEventListener('click',()=>{stop();document.querySelector('.poster').classList.remove('has-selection');stages.forEach((stage,i)=>{document.getElementById(stage[0]).classList.remove('is-active');buttons[i].setAttribute('aria-pressed','false')});note.textContent='Complete poster: methodology, formal definitions, separate evaluations and limits.'});
    document.querySelector('#enlarge').addEventListener('click',(event)=>{const active=document.body.classList.toggle('enlarged');event.currentTarget.setAttribute('aria-pressed',String(active));event.currentTarget.textContent=active?'Fit poster to screen':'Enlarge poster'});
    function motion(){if(reduced.matches)stop();play.disabled=reduced.matches}reduced.addEventListener('change',motion);motion();document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});
    </script></body></html>'''
    return markup.replace('POSTER_SIZE', 'A1' if PAGE_WIDTH_MM == 841 else 'A2')


def main(argv=None):
    global PAGE_WIDTH_MM, PAGE_HEIGHT_MM
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf',action='store_true',help='Export the same vector scene as PDF; requires ReportLab and Arial/DejaVu fonts')
    parser.add_argument('--paper', choices=('a1', 'a2'), default='a1', help='Landscape paper size; A1 is the presentation default, A2 is a reduced handout')
    args=parser.parse_args(argv)
    PAGE_WIDTH_MM, PAGE_HEIGHT_MM = (841, 594) if args.paper == 'a1' else (594, 420)
    scene=build_scene();DEST.mkdir(exist_ok=True)
    svg=scene.svg()
    (DEST/'resumelens-poster.svg').write_text(svg,encoding='utf-8')
    (DEST/'resumelens-poster.html').write_text(walkthrough(svg),encoding='utf-8')
    if args.pdf:scene.pdf(DEST/'resumelens-poster.pdf')
    layout = {'paper': args.paper.upper(), 'orientation': 'landscape',
              'width_mm': PAGE_WIDTH_MM, 'height_mm': PAGE_HEIGHT_MM,
              'central_columns': 3, 'accent_colors': [PURPLE, TEAL],
              'font_roles_points': {name: round(size * PAGE_HEIGHT_MM * 72 / 25.4 / H, 1)
                                    for name, size in FONT_ROLES.items()},
              'svg_text_word_count': sum(len(op[3].split()) for op in scene.operations if op[0] == 'text'),
              'word_count_scope': 'All SVG text labels, including diagrams, formulas and references; not only prose',
              'composition_area_percentages': None,
              'area_limit': 'Text/graphic/whitespace ink areas and physical viewing distance are not measured.'}
    (DEST/'layout-check.json').write_text(json.dumps(layout, indent=2) + '\n', encoding='utf-8')
    print('Complete research poster and interactive walkthrough generated'+(' with vector PDF.' if args.pdf else '.'))


if __name__=='__main__':main()
