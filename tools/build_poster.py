"""Vector poster for extraction and normalization."""
from html import escape
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs" / "poster"


def main():
    DEST.mkdir(exist_ok=True)
    metrics = json.loads((ROOT / "data/evaluation/results.json").read_text(encoding="utf-8"))["summary"]
    elements = ['<svg xmlns="http://www.w3.org/2000/svg" width="594mm" height="420mm" viewBox="0 0 1697 1200">',
                '<rect width="1697" height="1200" fill="#f5f7fa"/>',
                '<style>text{font-family:Arial,sans-serif} .arrow{fill:none;stroke:#334155;stroke-width:3;marker-end:url(#arr)}</style>',
                '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#334155"/></marker></defs>']

    def txt(x, y, value, size=22, color="#1e293b", weight="normal"):
        elements.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>')

    def paragraph(x, y, value, width=490, size=18):
        for line in textwrap.wrap(value, width=int(width / (size * .53))):
            txt(x, y, line, size)
            y += size * 1.38
        return y + 16

    def heading(x, y, value):
        txt(x, y, value, 26, "#12345b", "bold")
        return y + 40

    txt(38, 76, "ResumeLens", 60, "#12345b", "bold")
    txt(39, 119, "Traceable résumé extraction with regex and finite-state transducers", 30)
    txt(40, 152, "Extraction and normalization study • Partial project poster", 20, "#475569")
    labels = [("Text input", "UTF-8"), ("Regex extraction", "Evidence spans"), ("FST normalization", "Canonical tokens"), ("Profile automata", "Recognition model"), ("DSL and HTML", "Representation model")]
    for i, (title, subtitle) in enumerate(labels):
        x = 40 + i * 329
        fill = "#dbeafe" if i in (1, 2) else "#e2e8f0"
        elements.append(f'<rect x="{x}" y="185" width="298" height="80" rx="9" fill="{fill}"/>')
        txt(x + 16, 219, title, 23, "#12345b", "bold")
        txt(x + 16, 249, subtitle, 19)
        if i < 4:
            elements.append(f'<path class="arrow" d="M{x+300},225 L{x+323},225"/>')
    xs = [40, 599, 1158]
    for x in xs:
        elements.append(f'<rect x="{x}" y="296" width="519" height="734" rx="12" fill="white"/>')
    x, y = xs[0] + 18, 341
    y = heading(x, y, "Problem and research question")
    y = paragraph(x, y, "Different spellings and résumé layouts obscure explicit qualifications. Can formal models normalize a finite vocabulary while preserving the evidence for every output?", 480)
    y = heading(x, y + 5, "Extraction method")
    y = paragraph(x, y, "Python re identifies contact, academic and work records, and known skills. Section headings preserve multiline records. Longer aliases take precedence; literal punctuation and word boundaries limit partial matches.", 480)
    y = paragraph(x, y, "JS/TS require skills context; React requires explicit technical context. Eight negative patterns and clause boundaries exclude mentions while preserving positive contrasts.", 480)
    y = heading(x, y + 5, "Evidence contract")
    for line in ['Input:  Skills: JS', 'raw: "JS"   start: 8   end: 10', 'text[8:10] == "JS"', 'canonical: JAVASCRIPT']:
        txt(x, y, line, 20)
        y += 28
    paragraph(x, y + 6, "Repeated mentions retain separate evidence; canonical tokens are unique. JSON 1.0 preserves candidate data for subsequent processing.", 480)

    x, y = xs[1] + 18, 341
    y = heading(x, y, "Formal transducer model")
    y = paragraph(x, y, "Four pyformlang FSTs cover 26 canonical symbols and 56 aliases. Each casefolded alias has a separate character path. Only the last edge emits its canonical token.", 480)
    txt(x, y, "M = (Q, Σ, Γ, δ, ω, q0, F)", 26, "#12345b", "bold")
    y += 47
    for delta, state in [(0, "q0"), (177, "s0_a1_1"), (354, "s0_a1_2")]:
        cx, cy = x + 58 + delta, y + 55
        elements.append(f'<circle cx="{cx}" cy="{cy}" r="40" fill="#dbeafe" stroke="#12345b" stroke-width="2"/>')
        if delta == 354:
            elements.append(f'<circle cx="{cx}" cy="{cy}" r="35" fill="none" stroke="#12345b" stroke-width="2"/>')
        txt(cx - (16 if state == "q0" else 32), cy + 5, state, 16)
    for start, end, label in [(x + 101, x + 195, "j / ε"), (x + 278, x + 372, "s / JAVASCRIPT")]:
        elements.append(f'<path class="arrow" d="M{start},{y+55} L{end},{y+55}"/>')
        txt(start - 2, y + 1, label, 17)
    y += 138
    y = paragraph(x, y, "JS → js → JAVASCRIPT. Acceptance consumes the entire input and reaches a final state. Empty output is not an epsilon input edge. Shared first characters permit nondeterminism.", 480)
    y = heading(x, y + 4, "Our own transformations")
    for value in ["Type Script → TYPESCRIPT", "Git SCM → GIT", "Structured Query Language → SQL", "extracción transformación carga → ETL"]:
        txt(x, y, value, 18)
        y += 30
    paragraph(x, y + 7, "Complete seven tuples, transition tables and full SVG/DOT graphs are exported from the executable machines.", 480)

    x, y = xs[2] + 18, 341
    y = heading(x, y, "Results and failure analysis")
    y = paragraph(x, y, "39 automated tests pass: alias and case variants, eight sample résumés, records, context, negation, JSON validation and CLI errors. Verified in a fresh Python 3.12 environment.", 480)
    y = paragraph(x, y, "Evaluation: 23 synthetic annotated cases, including six historical reserved cases reused for regression. Exact character spans are compared; this is not a real-world independent benchmark.", 480)
    for group, label in [("supported", "Supported formats"), ("holdout", "Reserved synthetic cases"), ("stress", "Stress beyond scope")]:
        m = metrics[group]
        txt(x, y, f'{label}: {m["cases"]} cases', 22, "#12345b", "bold")
        y += 27
        txt(x, y, f'TP {m["tp"]}   FP {m["fp"]}   FN {m["fn"]}   F1 {m["f1"]:.2f}', 21)
        y += 31
    y = heading(x, y + 4, "Limits and conclusion")
    y = paragraph(x, y, "Stress cases expose double negation and unknown technology (Rust). Animal pandas mentions are excluded by context rules. No population accuracy claim or candidate ranking is made.", 480)
    paragraph(x, y, "Extraction and normalization preserve explicit evidence. Profile recognition and DSL validation require separate models, tests and results.", 480)

    txt(40, 1070, "Selected references", 25, "#12345b", "bold")
    txt(40, 1101, "Yu, Guan & Zhou (2005). Resume Information Extraction with Cascaded Hybrid Model. ACL, 499–506. doi:10.3115/1219840.1219902", 18)
    txt(40, 1129, "Mohri (1997). Finite-State Transducers in Language and Speech Processing. Computational Linguistics 23(2), 269–311.", 18)
    txt(40, 1157, "Python re documentation • pyformlang FST documentation • Full references and models: docs/ in the project repository", 18)
    elements.append("</svg>")
    (DEST / "first-stage-poster.svg").write_text("\n".join(elements), encoding="utf-8")
    print("A2 poster generated")


if __name__ == "__main__":
    main()
