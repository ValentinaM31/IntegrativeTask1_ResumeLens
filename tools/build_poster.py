"""Build a complete research poster, its animated walkthrough and an optional PDF."""
import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/poster'
W, H = 1920, 1358
INK, MUTED = '#202b40', '#5f6d82'
PURPLE, TEAL, BLUE, GOLD = '#6052bc', '#287963', '#3e6ca2', '#956724'


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

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="594mm" height="420mm" viewBox="0 0 {W} {H}" role="img" aria-labelledby="poster-title poster-desc">'
                '<title id="poster-title">ResumeLens: from a resume to traceable qualification patterns</title>'
                '<desc id="poster-desc">Complete research poster with a worked example, regex evidence, FST path, four epsilon-NFA patterns, textX candidate language, separate synthetic evaluation results and verification limits.</desc>'
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
        document = canvas.Canvas(str(destination), pagesize=(594 * mm, 420 * mm))
        document.setTitle('ResumeLens - Formal language models and verified results')
        document.setAuthor('Valentina Martinez Franco and Juan Pino')
        document.scale(594 * mm / W, 420 * mm / H)
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
        document.showPage();document.save()


def build_scene():
    read = lambda path: json.loads((ROOT / path).read_text(encoding='utf-8'))
    extraction = read('data/evaluation/results.json')['summary']
    integration_path = ROOT / 'data/workflow-evaluation/visual-update/results.json'
    integration = json.loads(integration_path.read_text(encoding='utf-8')) if integration_path.exists() else read('data/workflow-evaluation/results.json')
    pre_path = ROOT / 'data/preannotated-evaluation/visual-update/results.json'
    pre = json.loads(pre_path.read_text(encoding='utf-8')) if pre_path.exists() else read('data/preannotated-evaluation/results.json')
    validation_path = DEST / 'verification.json'
    verified = json.loads(validation_path.read_text(encoding='utf-8')) if validation_path.exists() else {'status':'pending'}
    fingerprints = verified.get('source_sha256', {})
    current_paths = {path.relative_to(ROOT).as_posix() for directory in ('src/resumelens', 'tests')
                     for path in (ROOT / directory).rglob('*') if path.is_file()
                     and '__pycache__' not in path.parts
                     and path.suffix in ('.py', '.json', '.tx', '.html', '.css', '.js', '.txt')}
    if set(fingerprints) != current_paths or any(not (ROOT / path).is_file() or hashlib.sha256(
            (ROOT / path).read_bytes().replace(b'\r\n', b'\n')).hexdigest() != value
            for path, value in fingerprints.items()):
        verified = {'status': 'stale'}
    first = read('data/results/01_full_stack.json')
    mention = first['extracted_skills'][0]
    s = Scene()
    s.rect(0,0,W,H,'#f4f5fa')
    s.rect(0,0,W,175,'#fff')
    s.text(48,49,'COMPUTING & DISCRETE STRUCTURES III  /  INTEGRATIVE TASK 1',14,PURPLE,True)
    s.text(48,112,'ResumeLens',66,INK,True)
    s.text(48,152,'From a resume to traceable qualification patterns.',27,MUTED)
    s.text(1872,60,'Valentina Martinez Franco',19,INK,True,anchor='end')
    s.text(1872,88,'Juan Pino',19,INK,True,anchor='end')
    s.text(1872,120,'4 FSTs  |  4 profile automata',18,PURPLE,True,anchor='end')
    s.text(1872,147,'26 canonical symbols  /  56 aliases',17,MUTED,anchor='end')
    stages=[('TEXT','UTF-8 resume','Original wording',INK,'#e9edf4'),('REGEX','Extract','Exact evidence',BLUE,'#eaf1fb'),('FST','Normalize','Canonical skills',PURPLE,'#f0edfb'),('AUTOMATA','Recognize','Four profile patterns',TEAL,'#eaf5ee'),('TEXTX','Validate + render','DSL to candidate report',GOLD,'#fbf2e6')]
    for index,(label,title,subtitle,color,background) in enumerate(stages):
        x=48+index*367
        s.rect(x,199,354,86,background,12)
        s.text(x+18,222,label,12,color,True)
        s.text(x+18,251,title,25,color,True)
        s.text(x+18,273,subtitle,16,MUTED)
        if index<4:s.arrow(x+357,243,x+365,'#a3aabb')
    def card(x,y,width,height,label,title,color=PURPLE):
        s.rect(x,y,width,height,'#fff',16,'#e1e5ee')
        s.rect(x+20,y+23,4,44,color,2)
        s.text(x+37,y+37,label,12,color,True)
        s.text(x+37,y+68,title,28,INK,True)
    # The worked example traces actual offsets from the versioned main sample.
    s.group('stage-extract');card(48,311,592,348,'01  /  TEXT TO EVIDENCE','What does the text actually say?',BLUE)
    s.paragraph(74,405,'Question: can explicit formal models handle varied wording while preserving the evidence behind every result?',534,20)
    s.rect(74,459,540,89,'#f3f6fc',9)
    s.text(92,486,'Technical Skills:',18,BLUE,True,True)
    s.text(92,517,'JS, React.js, NodeJS, Postgres, Git.',19,INK,False,True)
    s.rect(89,497,27,29,'#dbe2fb',3)
    s.text(92,517,'JS',19,BLUE,True,True)
    s.text(74,579,f'raw: "{mention["raw"]}"   start: {mention["start"]}   end: {mention["end"]}',19,BLUE,True,True)
    s.paragraph(74,611,'Positions use the LF Alex Sample reference. Positive mentions and exclusions stay separate.',532,19)
    s.end_group()
    s.group('stage-normalize');card(48,681,592,495,'02  /  EQUIVALENT WORDING','One alias, one canonical symbol',PURPLE)
    s.text(74,780,'M = (Q, Σ, Γ, δ, ω, q0, F)',25,PURPLE,True)
    nodes=[112,307,520]
    for index,cx in enumerate(nodes):
        s.circle(cx,850,25,'#f1edfb',PURPLE)
        if index==2:s.circle(cx,850,20,'#f1edfb',PURPLE)
        s.text(cx,857,'q'+str(index),19,PURPLE,True,anchor='middle')
    s.arrow(74,850,85,PURPLE);s.arrow(139,850,280,PURPLE);s.arrow(334,850,493,PURPLE)
    s.text(206,829,'j / ε',17,PURPLE,False,True,anchor='middle')
    s.text(414,829,'s / JAVASCRIPT',15,PURPLE,False,True,anchor='middle')
    s.text(74,905,'JS -> js -> JAVASCRIPT',21,PURPLE,True,True)
    s.paragraph(74,939,'Schematic path: consume the entire alias; only the last edge emits a canonical token. Empty output still consumes an input character.',530,19)
    s.text(74,1041,'Q: alias-path states   Σ: casefolded characters',18,INK)
    s.text(74,1067,'Γ: canonical symbols   δ: character transitions',18,INK)
    s.text(74,1093,'ω: edge outputs   q0: start   F: full-alias ends',18,INK)
    s.text(74,1133,'Own: Type Script -> TYPESCRIPT | Git SCM -> GIT',17,MUTED)
    s.text(74,1157,'Structured Query Language -> SQL. Full models: docs/models/',17,MUTED)
    s.end_group()
    s.group('stage-recognize');card(664,311,592,506,'03  /  CANONICAL SYMBOLS','When does a profile accept?',TEAL)
    s.text(690,405,'A = (Q, Σ, δ, q0, F)    Type: ε-NFA',24,TEAL,True)
    s.text(690,441,'Full Stack',19,INK,True);s.text(690,466,'JS/TS + frontend + backend + database + Git',18,MUTED)
    s.text(690,501,'Machine Learning',19,INK,True);s.text(690,526,'Python + Pandas/NumPy + library + relational DB + Git',17,MUTED)
    s.text(690,554,'Library: Scikit-learn OR TensorFlow OR PyTorch',17,TEAL,True)
    s.text(690,589,'Backend',19,INK,True);s.text(690,614,'Compatible pair + database + REST API + Git',18,MUTED)
    s.text(690,649,'Data Engineer',19,INK,True);s.text(690,674,'Python + database + ETL/Airflow/Spark + Git',18,MUTED)
    s.line(690,696,1230,696,'#dfe8e4')
    s.text(690,725,'Q: states  Σ: canonical skills  δ: includes ε edges',18,INK)
    s.text(690,752,'q0: initial state  F: accepting states',18,INK)
    s.paragraph(690,779,'Bucket order stabilizes input. Compatible Backend branches constrain pairs. Several profiles may accept.',531,17)
    s.end_group()
    s.group('stage-validate');card(664,839,592,337,'04  /  EBNF AND COMPACT DSL EXAMPLE','Valid syntax before visualization',GOLD)
    code=['candidate {','  name "Alex Sample";','  contacts {} education {} experience {}','  skills { skill JAVASCRIPT; skill REACT;','    skill NODE_JS; skill POSTGRESQL; skill GIT; }','  accepted_profiles { profile FULL_STACK_DEVELOPER; }','}']
    s.rect(690,928,540,137,'#f8f3eb',9)
    for index,line in enumerate(code):s.text(705,948+index*18,line,15.5,'#795729',False,True)
    s.text(690,1091,'Record = "record", JSONString, ";" ;',15,GOLD,False,True)
    s.text(690,1116,'Education = "education", "{", {Record}, "}" ;',14.5,GOLD,False,True)
    s.text(690,1141,'Keywords/tokens: terminals. Record/Education: nonterminals.',15,INK)
    s.text(690,1164,'textX + semantic checks -> validated DSL -> escaped HTML.',16,INK)
    s.end_group()
    card(1280,311,592,326,'05  /  SEPARATE EVALUATIONS','Measured, with visible limits',PURPLE)
    s.text(1306,405,'14-case workflow regression',20,INK,True)
    s.text(1846,405,f'{integration["passed"]}/{integration["cases"]}',24,TEAL,True,anchor='end')
    s.text(1306,435,'Candidate data, spans, links, profiles and exports.',17,MUTED)
    overall=pre['summary']['overall'];exact=overall['all_annotations_exact']
    s.text(1306,475,'18-case preannotated evaluation',20,INK,True)
    s.text(1846,475,f'{exact}/18',24,TEAL,True,anchor='end')
    s.rect(1306,492,540,12,'#efeaf2',5);s.rect(1306,492,540*exact/18,12,'#5ca080',5)
    s.text(1306,529,'14 exact cases; 4 observed disagreements retained.',17,MUTED)
    mention_metrics=overall['positive_mentions'];profile_metrics=overall['accepted_profiles']
    s.text(1306,558,f'Mentions: TP {mention_metrics["tp"]} / FP {mention_metrics["fp"]} / FN {mention_metrics["fn"]}',17,INK)
    s.text(1306,585,f'Profiles: TP {profile_metrics["tp"]} / FP {profile_metrics["fp"]} / FN {profile_metrics["fn"]}',17,INK)
    s.text(1306,616,'23 historical extraction cases: 15 + 6 + 2.',17,MUTED)
    card(1280,659,592,200,'VERIFICATION SNAPSHOT','Executable evidence',TEAL)
    if verified.get('status')=='passed':
        s.text(1306,758,f'{verified["tests_run"]} tests  /  {verified["passed"]} pass  /  {verified["skipped"]} skip',25,TEAL,True)
        s.text(1306,789,'Windows regression; source spans and files checked.',17,MUTED)
        s.text(1306,821,'Bounded retries handle transient Windows file locks.',17,MUTED)
    else:
        s.text(1306,759,'Verification snapshot pending',24,GOLD,True)
        s.paragraph(1306,791,'Generate verification.json from the actual test run before presenting success counts.',525,18)
    card(1280,881,592,295,'INTERPRETATION  /  NEXT STEPS','What the models cannot prove',GOLD)
    limitations=[('Rust','Unknown technology outside the catalog.'),('Double negation','A positive Python claim can be missed.'),('Source attribution','Job requirements can be mistaken for skills.'),('Pandas wording','Bounded context misses some technical prose.')]
    for index,(label,detail) in enumerate(limitations):
        y=979+index*39
        s.circle(1314,y-6,4,GOLD)
        s.text(1329,y,label+':',17,INK,True)
        s.text(1329,y+21,detail,16,MUTED)
    s.text(1306,1158,'Next: independent real data and profile-domain validation.',16,GOLD,True)
    # A schematic minimal accepting path, not a claim of minimization of the actual NFA.
    s.rect(48,1198,1824,90,'#29273f',12)
    s.text(70,1231,'ACCEPTING PATH',12,'#b8b0e4',True)
    s.text(70,1257,'Schematic profile pattern',12,'#b8b0e4')
    s.arrow(248,1252,266,'#b8b0e4')
    positions=[285,515,745,975,1205,1435]
    symbols=['JAVASCRIPT','REACT','NODE_JS','POSTGRESQL','GIT']
    for index,cx in enumerate(positions):
        s.circle(cx,1252,17,'#393551','#b8b0e4')
        if index==5:s.circle(cx,1252,13,'#393551','#b8b0e4')
        s.text(cx,1258,'q'+str(index),15,'#fff',True,anchor='middle')
        if index<5:
            s.arrow(cx+19,1252,positions[index+1]-19,'#b8b0e4')
            s.text((cx+positions[index+1])/2,1237,symbols[index],14,'#fff',True,True,anchor='middle')
    s.text(1846,1243,'FULL STACK',19,'#aee6c6',True,anchor='end')
    s.text(1846,1270,'ACCEPTED',19,'#aee6c6',True,anchor='end')
    s.text(48,1309,'REPRODUCIBILITY',11,PURPLE,True)
    s.text(237,1309,'Complete machines: docs/models/ and docs/automata/ | EBNF: docs/candidate-language.md | Evaluation: data/',15,MUTED)
    s.text(48,1332,'REFERENCES',11,PURPLE,True)
    s.text(237,1332,'Mohri (1997), Computational Linguistics 23(2), 269-311. Yu, Guan & Zhou (2005), ACL, 499-506. doi:10.3115/1219840.1219902',14,MUTED)
    s.text(48,1353,'Synthetic regression, not population accuracy. Structure does not verify claims. No ranking or hiring decision is inferred.',14,MUTED)
    return s


def walkthrough(svg):
    steps=[('stage-extract','Extract evidence','Regex identifies explicit mentions. JS retains its exact span in the Alex Sample text. Negated or ambiguous mentions are kept separately.'),
           ('stage-normalize','Normalize aliases','Follow j and s through an illustrative FST path. The final edge emits JAVASCRIPT only after the alias has been consumed.'),
           ('stage-recognize','Recognize a profile','Canonical bucket order prepares the skills for an epsilon-NFA. Every required group must be seen. Backend pairs use compatible branches.'),
           ('stage-validate','Validate and render','The EBNF defines repeated records. textX checks syntax; semantic checks verify profile claims. The validated specification becomes escaped HTML.')]
    buttons=''.join(f'<button type="button" data-stage="{identifier}" aria-pressed="false">{title}</button>' for identifier,title,_ in steps)
    data=json.dumps(steps,ensure_ascii=False).replace('<','\\u003c')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ResumeLens | Research poster walkthrough</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f3f4fa;color:#202b40;font:15px/1.6 system-ui,sans-serif}.controls{max-width:1500px;margin:22px auto;padding:22px 26px;background:white;border:1px solid #dce0eb;border-radius:14px}.controls h1{font-size:24px;margin:0 0 6px}.controls p{margin:7px 0;color:#5f6d82}.buttons{display:flex;flex-wrap:wrap;gap:9px;margin:16px 0}button{font:600 12px system-ui,sans-serif;padding:10px 13px;color:#524491;background:#f1eefb;border:1px solid #d9d1eb;border-radius:8px;cursor:pointer}button[aria-pressed=true]{background:#6052bc;color:white}button:disabled{opacity:.5;cursor:default}:focus-visible{outline:3px solid #33227a;outline-offset:4px}.poster{max-width:1700px;margin:0 auto 25px;padding:0 18px}.poster svg{width:100%;height:auto;background:#f4f5fa;border-radius:12px}.stage-panel{transition:opacity .3s}.has-selection .stage-panel{opacity:.38}.has-selection .stage-panel.is-active{opacity:1}.is-active>rect:first-child{stroke:#6052bc;stroke-width:3}.is-active{animation:highlight 1s ease-out}#stage-note{min-height:48px}.note{font-size:12px}.print-link{color:#6052bc;font-weight:600}@keyframes highlight{from{filter:brightness(1.12)}to{filter:none}}@media(max-width:650px){.controls{margin:12px;padding:18px}.poster{padding:0 8px}.controls h1{font-size:21px}}@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}@media print{.controls{display:none}.poster{padding:0;margin:0;max-width:none}.has-selection .stage-panel{opacity:1}.poster svg{border-radius:0}}
    </style></head><body><section class="controls" aria-label="Poster walkthrough"><h1>Follow one resume through four formal models.</h1><p>Choose a stage, or play the guided walkthrough. The printed poster remains a complete, static research artifact.</p><div class="buttons">'''+buttons+'''<button type="button" id="play">Play walkthrough</button><button type="button" id="overview">Show complete poster</button></div><p id="stage-note" role="status" aria-live="polite">The complete poster shows methodology, formal definitions, separate evaluations and limits.</p><p class="note">Original labels and observed errors are preserved. Animations respect reduced-motion preferences. <a class="print-link" href="resumelens-poster.pdf">Open printable PDF</a></p></section><main class="poster">'''+svg+'''</main><script>
    const stages='''+data+''';let index=0,timer=null;const buttons=[...document.querySelectorAll('[data-stage]')],play=document.querySelector('#play'),note=document.querySelector('#stage-note');const reduced=matchMedia('(prefers-reduced-motion: reduce)');
    function stop(){clearInterval(timer);timer=null;play.textContent='Play walkthrough'}
    function select(i){index=i;document.querySelector('.poster').classList.add('has-selection');stages.forEach((stage,j)=>{document.getElementById(stage[0]).classList.toggle('is-active',i===j);buttons[j].setAttribute('aria-pressed',String(i===j))});note.textContent=stages[i][1]+': '+stages[i][2]}
    buttons.forEach((button,i)=>button.addEventListener('click',()=>{stop();select(i)}));play.addEventListener('click',()=>{if(timer){stop();return}if(reduced.matches)return;select(index);play.textContent='Pause walkthrough';timer=setInterval(()=>select((index+1)%stages.length),6500)});
    document.querySelector('#overview').addEventListener('click',()=>{stop();document.querySelector('.poster').classList.remove('has-selection');stages.forEach((stage,i)=>{document.getElementById(stage[0]).classList.remove('is-active');buttons[i].setAttribute('aria-pressed','false')});note.textContent='Complete poster: methodology, formal definitions, separate evaluations and limits.'});
    function motion(){if(reduced.matches)stop();play.disabled=reduced.matches}reduced.addEventListener('change',motion);motion();document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});
    </script></body></html>'''


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf',action='store_true',help='Export the same vector scene as PDF; requires ReportLab and Arial/DejaVu fonts')
    args=parser.parse_args(argv)
    scene=build_scene();DEST.mkdir(exist_ok=True)
    svg=scene.svg()
    (DEST/'resumelens-poster.svg').write_text(svg,encoding='utf-8')
    (DEST/'resumelens-poster.html').write_text(walkthrough(svg),encoding='utf-8')
    if args.pdf:scene.pdf(DEST/'resumelens-poster.pdf')
    print('Complete research poster and interactive walkthrough generated'+(' with vector PDF.' if args.pdf else '.'))


if __name__=='__main__':main()
