"""Export teaching views of actual accepting alias paths, without changing FSTs."""
import argparse
from html import escape
from pathlib import Path

from resumelens.catalog import load_catalog
from resumelens.normalization import build_transducers


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs" / "models" / "examples"
EXAMPLES = (
    ("javascript", "JS", "JAVASCRIPT"),
    ("react", "React.js", "REACT"),
    ("postgresql", "Postgres", "POSTGRESQL"),
    ("git", "Git SCM", "GIT"),
)
REJECTED_EXAMPLES = ("JSx", "ReactXjs", "React-js", "Git  SCM", "Postgres extra")


def accepting_path(machine, alias, canonical):
    """Find and verify the complete accepting path in the executable machine."""
    word = alias.casefold()
    candidates = [(state, []) for state in machine.start_states]
    for char in word:
        candidates = [
            (target, path + [(source, char, target, tuple(output))])
            for source, path in candidates
            for target, output in machine.transitions.get((source, char), ())
        ]
    accepted = [
        path for state, path in candidates
        if state in machine.final_states
        and tuple(token for _, _, _, output in path for token in output)
        == (canonical,)
    ]
    if len(accepted) != 1:
        raise ValueError(f"Expected one accepting alias path: {alias!r}")
    path = accepted[0]
    if not path or path[0][0] not in machine.start_states:
        raise ValueError("Missing initial state")
    if path[-1][2] not in machine.final_states:
        raise ValueError("Missing accepting state")
    for index, (source, char, target, output) in enumerate(path):
        if (target, list(output)) not in machine.transitions[(source, char)]:
            raise ValueError("Displayed transition differs from executable FST")
        if index and path[index - 1][2] != source:
            raise ValueError("Displayed path is not contiguous")
    if "".join(char for _, char, _, _ in path) != word:
        raise ValueError("Displayed path does not consume the complete alias")
    translations = {tuple(output) for output in machine.translate(list(word))}
    if translations != {(canonical,)}:
        raise ValueError("Executable translation differs from displayed result")
    return path


def symbol(char):
    return "␠" if char == " " else char


def output_label(output):
    return " ".join(output) if output else "ε"


def svg_example(category, alias, canonical, path):
    """Draw a short path; long aliases continue in a second, reversed row."""
    states = [path[0][0]] + [target for _, _, target, _ in path]
    columns = min(5, len(states))
    width = 184 * (columns - 1) + 194
    rows = (len(states) + columns - 1) // columns
    height = 240 + (rows - 1) * 166
    positions = []
    for index in range(len(states)):
        row, column = divmod(index, columns)
        if row % 2:
            column = columns - 1 - column
        positions.append((97 + column * 184, 156 + row * 166))
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(alias)} to {escape(canonical)}: actual FST alias path</title>',
        f'<desc id="desc">One accepting path from the {escape(category)} machine. State names and all input/output labels are taken from its executable transitions. Other alias paths are omitted.</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<defs><marker id="arrow" markerWidth="9" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#65538e"/></marker></defs>',
        '<style>text{font-family:Arial,sans-serif;fill:#282338}.edge{fill:none;stroke:#65538e;stroke-width:2;marker-end:url(#arrow)}.state{stroke:#65538e;stroke-width:2;fill:#f4f0fb}.label{font-size:14px}.name{font-size:11px;text-anchor:middle}</style>',
        f'<text x="24" y="31" font-size="22" font-weight="bold">{escape(alias)} → {escape(canonical)}</text>',
        f'<text x="24" y="57" font-size="13">Alias-path subset of {escape(category)}. Other branches are omitted.</text>',
        f'<text x="24" y="79" font-size="13">Input after separate casefold: {escape(alias.casefold())}</text>',
        f'<path class="edge" d="M20,156 L59,156"/>',
    ]
    for index, (_, char, _, output) in enumerate(path):
        x1, y1 = positions[index]
        x2, y2 = positions[index + 1]
        label = escape(f"{symbol(char)} / {output_label(output)}")
        if y1 == y2:
            direction = 1 if x2 > x1 else -1
            elements.append(f'<path class="edge" d="M{x1 + direction * 38},{y1} L{x2 - direction * 39},{y2}"/>')
            elements.append(f'<text class="label" x="{(x1 + x2) / 2}" y="{y1 - 16}" text-anchor="middle">{label}</text>')
        else:
            elements.append(f'<path class="edge" d="M{x1},{y1 + 38} L{x2},{y2 - 39}"/>')
            elements.append(f'<text class="label" x="{x1 - 12}" y="{(y1 + y2) / 2 + 5}" text-anchor="end">{label}</text>')
    for index, (state, (x, y)) in enumerate(zip(states, positions)):
        final = index == len(states) - 1
        color = "#e9f4ee" if final else "#f4f0fb"
        elements.append(f'<circle class="state" cx="{x}" cy="{y}" r="37" style="fill:{color}"/>')
        if final:
            elements.append(f'<circle cx="{x}" cy="{y}" r="32" fill="none" stroke="#65538e" stroke-width="2"/>')
        elements.append(f'<text class="name" x="{x}" y="{y + 4}">{escape(str(state))}</text>')
    elements.extend([
        f'<text x="24" y="{height - 23}" font-size="12">Labels: input / output. ε = empty output; ␠ = one space. Double circle = accepting.</text>',
        '</svg>',
    ])
    return "\n".join(elements) + "\n"


def mermaid_path(path):
    states = [path[0][0]] + [target for _, _, target, _ in path]
    lines = ["```mermaid", "flowchart LR", '    start(["start"]) --> n0']
    for index, state in enumerate(states):
        delimiter = ("(((", ")))") if index == len(states) - 1 else ("((", "))")
        lines.append(f'    n{index}{delimiter[0]}"{state}"{delimiter[1]}')
    for index, (_, char, _, output) in enumerate(path):
        lines.append(f'    n{index} -->|"{symbol(char)} / {output_label(output)}"| n{index + 1}')
    lines.append("```")
    return "\n".join(lines)


def build_outputs():
    catalog = load_catalog()
    categories = {skill["canonical"]: skill["category"] for skill in catalog["skills"]}
    machines = build_transducers(catalog)
    for raw in REJECTED_EXAMPLES:
        if any(list(machine.translate(list(raw.casefold()))) for machine in machines.values()):
            raise ValueError(f"Documented boundary example now accepts: {raw!r}")
    outputs = {}
    readme = [
        "# Worked transducer paths",
        "",
        "These views show four accepting alias paths taken from the executable",
        "`pyformlang.fst.FST` machines. They retain the real state names and transition",
        "labels. Each is a **subset of a complete category machine**: omitted branches",
        "still exist, and the full machine remains nondeterministic. These are neither",
        "separate production transducers nor minimized replacements.",
        "",
        "The input to each FST is `list(raw.casefold())`. Case folding is a separate",
        "preprocessor; it does not collapse separators or internal spaces. In the",
        "labels and tables, `␠` means exactly one space and `ε` means empty **output**.",
        "Every edge consumes its displayed input character. The initial arrow marks",
        "`q0`; a double circle marks an accepting state.",
        "",
        "[Complete seven-tuples and full diagrams](../../transducers.md)",
        "",
        "Regenerate from an installed checkout with:",
        "",
        "```powershell",
        ".\\.venv\\Scripts\\python.exe tools/export_model_examples.py",
        ".\\.venv\\Scripts\\python.exe tools/export_model_examples.py --check",
        "```",
        "",
        "The generator verifies each edge, complete input consumption, accepting",
        "state and canonical output against the actual machine before writing. Check",
        "mode also rejects stored views that differ from those verified transitions.",
    ]
    for slug, alias, canonical in EXAMPLES:
        category = categories[canonical]
        skill = next(skill for skill in catalog["skills"] if skill["canonical"] == canonical)
        if alias not in skill["aliases"]:
            raise ValueError(f"Teaching alias is absent from catalog: {alias}")
        path = accepting_path(machines[category], alias, canonical)
        outputs[f"{slug}.svg"] = svg_example(category, alias, canonical, path)
        readme.extend([
            "", f"## {alias} → {canonical}", "",
            f"Category: `{category}`. Raw input: `{alias}`. FST input: `{alias.casefold()}`.",
            "", f"![Accepting path for {alias}]({slug}.svg)", "",
            mermaid_path(path), "",
            "| Step | Raw character | FST input | Source | Target | Output |",
            "|---:|---|---|---|---|---|",
        ])
        if len(alias) != len(path):
            raise ValueError("Trace requires aligned raw and casefolded characters")
        for index, (source, char, target, output) in enumerate(path):
            readme.append(
                f"| {index + 1} | `{symbol(alias[index])}` | `{symbol(char)}` | "
                f"`{source}` | `{target}` | `{output_label(output)}` |"
            )
        readme.extend([
            "", f"The complete input is exhausted at `{path[-1][2]}`; concatenating the",
            f"transition outputs produces the single symbol `{canonical}`.",
        ])
    readme.extend([
        "", "## Boundary examples", "",
        "Direct FST translation rejects `JSx`, `ReactXjs`, `React-js`, `Git  SCM` and",
        "`Postgres extra`: none is a complete catalog alias. `React.js` keeps its",
        "literal dot, and `Git SCM` consumes exactly one internal space. An extractor",
        "may locate a shorter alias within a larger source string; that is a separate",
        "stage and does not expand the language accepted by the FST.",
    ])
    outputs["README.md"] = "\n".join(readme) + "\n"
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify stored examples without rewriting them")
    args = parser.parse_args()
    outputs = build_outputs()
    if args.check:
        stale = [name for name, content in outputs.items()
                 if not (DEST / name).is_file()
                 or (DEST / name).read_text(encoding="utf-8") != content]
        if stale:
            parser.exit(1, "Missing or stale model examples: " + ", ".join(stale) + "\n")
    else:
        DEST.mkdir(parents=True, exist_ok=True)
        for name, content in outputs.items():
            (DEST / name).write_text(content, encoding="utf-8")
    print(f"Verified {len(EXAMPLES)} accepting alias paths; {'checked' if args.check else 'exported'} {len(outputs)} files.")


if __name__ == "__main__":
    main()
