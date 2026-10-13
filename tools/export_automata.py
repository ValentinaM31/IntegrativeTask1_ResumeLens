"""Export complete DFA five-tuples, total tables and faithful transition panels."""
from html import escape
import json
from pathlib import Path
from textwrap import wrap
from resumelens.classification import build_profile_automaton, load_profiles

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs" / "automata"


def transitions_of(machine):
    return sorted((str(source.value), str(symbol.value), str(target.value))
                  for source, edges in machine.to_dict().items()
                  for symbol, target in edges.items())


def state_order(state):
    if state == "q0": return (0, 0)
    if state.startswith("L"): return (1, int(state[1:]))
    if state.startswith("W"): return (2, int(state[1:]))
    if state == "pair_seen": return (3, 0)
    if state == "qf": return (5, 0)
    if state == "q_dead": return (6, 0)
    return (4, int(state[1:]))


def export_svg(profile, machine, transitions):
    """A complete outgoing-transition panel per state, with parallel edges grouped.

    Identical names in multiple panels denote the same state. Each labelled
    arrow is a real transition; no error or sink transition is omitted.
    """
    finals = {str(state.value) for state in machine.final_states}
    states = sorted((str(state.value) for state in machine.states), key=state_order)
    groups = {}
    for source, symbol, target in transitions:
        groups.setdefault(source, {}).setdefault(target, []).append(symbol)
    panels = []
    for source in states:
        rows, height = [], 88
        for target in sorted(groups[source], key=state_order):
            symbols = groups[source][target]
            labels = wrap(", ".join(symbols), 43, break_long_words=False, break_on_hyphens=False)
            row_height = max(82, len(labels) * 21 + 30)
            rows.append((target, symbols, labels, row_height))
            height += row_height
        panels.append((source, rows, height))
    width = 1860
    header = 400 if profile.get("required_pair_alternatives") else 232
    row_heights = [max(panel[2] for panel in panels[index:index + 2]) for index in range(0, len(panels), 2)]
    height = header + sum(row_heights) + len(row_heights) * 20 + 35
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(profile["id"])}: complete deterministic automaton</title>',
        '<desc id="desc">One complete outgoing-transition panel per source state. Identical names denote the same state. All input symbols have one destination. The rejecting sink is explicit.</desc>',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<defs><marker id="arrow" markerWidth="9" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#65538e"/></marker></defs>',
        '<style>text{font-family:Arial,sans-serif;fill:#282338}.edge{fill:none;stroke:#65538e;stroke-width:2;marker-end:url(#arrow)}</style>',
        f'<text x="30" y="42" font-size="29" font-weight="bold">{escape(profile["id"])}</text>',
        f'<text x="30" y="78" font-size="20">Complete DFA: {len(states)} states · {len(machine.symbols)} symbols · {len(transitions)} transition triples · no epsilon transitions.</text>',
        '<text x="30" y="112" font-size="18">Every panel lists all outgoing transitions. Commas separate alternative input symbols on one edge.</text>',
        '<text x="30" y="143" font-size="18">Identical names denote the same state. Arrow into q0 = start. Double circle = accepting.</text>',
        '<text x="30" y="174" font-size="18">q_dead is the rejecting sink: all its symbols return to q_dead. Missing or out-of-order groups enter q_dead.</text>',
    ]
    if profile.get("required_pair_alternatives"):
        notes = [
            'Backend memory: Lm reads languages; Wm has read frameworks but no compatible pair yet.',
            'm records compatible frameworks: bit 1 = DJANGO; bit 2 = NODE_JS; bit 4 = SPRING_BOOT.',
            'Examples: L3/W3 admit DJANGO or NODE_JS; L7 admits all three. W7 is unreachable.',
            'pair_seen = compatible pair; q3 = database; q4 = REST_API; qf = GIT.',
        ]
        elements.extend(f'<text x="30" y="{211 + i * 31}" font-size="18">{escape(note)}</text>' for i, note in enumerate(notes))
    else:
        elements.append('<text x="30" y="205" font-size="18">qi means the first i required groups were consumed; alphabet loops retain additional alternatives.</text>')

    def node(state, x, y):
        fill = "#fbeeed" if state == "q_dead" else "#e9f4ee" if state in finals else "#f4f0fb"
        elements.append(f'<circle cx="{x}" cy="{y}" r="34" fill="{fill}" stroke="#65538e" stroke-width="2"/>')
        if state in finals:
            elements.append(f'<circle cx="{x}" cy="{y}" r="29" fill="none" stroke="#65538e" stroke-width="2"/>')
        elements.append(f'<text x="{x}" y="{y + 4}" text-anchor="middle" font-size="11">{escape(state)}</text>')

    y = header
    for index in range(0, len(panels), 2):
        for column, (source, rows, panel_height) in enumerate(panels[index:index + 2]):
            x = 30 + column * 915
            elements.extend([
                f'<g data-source="{escape(source)}">',
                f'<rect x="{x}" y="{y}" width="885" height="{panel_height}" rx="12" fill="#fff" stroke="#ddd8e8"/>',
                f'<text x="{x + 20}" y="{y + 30}" font-size="20" font-weight="bold">From {escape(source)}</text>',
            ])
            source_y = y + 48 + (panel_height - 48) / 2
            node(source, x + 92, source_y)
            if source == "q0":
                elements.append(f'<path class="edge" d="M{x + 15},{source_y} L{x + 53},{source_y}"/>')
            target_y = y + 57
            for target, symbols, labels, edge_height in rows:
                center_y = target_y + edge_height / 2
                elements.append(f'<g data-target="{escape(target)}" data-symbols="{escape(json.dumps(symbols), quote=True)}">')
                elements.append(f'<path class="edge" d="M{x + 132},{source_y} L{x + 744},{center_y}"/>')
                label_y = center_y - (len(labels) - 1) * 10.5 - 10
                for line_index, label in enumerate(labels):
                    line_y = label_y + line_index * 21
                    elements.append(f'<rect x="{x + 259}" y="{line_y - 17}" width="465" height="21" fill="#fff"/>')
                    elements.append(f'<text x="{x + 275}" y="{line_y}" font-size="16">{escape(label)}</text>')
                node(target, x + 784, center_y)
                elements.append('</g>')
                target_y += edge_height
            elements.append('</g>')
        y += row_heights[index // 2] + 20
    elements.append('</svg>')
    (DEST / (profile["id"] + ".svg")).write_text("\n".join(elements) + "\n", encoding="utf-8")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    summary = []
    for profile in load_profiles():
        machine = build_profile_automaton(profile)
        transitions = transitions_of(machine)
        assert len(transitions) == len(machine.states) * len(machine.symbols)
        model = {"profile": profile["id"], "type": "DFA", "complete": True, "sink": "q_dead",
                 "Q": sorted(str(state.value) for state in machine.states),
                 "Sigma": sorted(str(symbol.value) for symbol in machine.symbols),
                 "delta": [list(row) for row in transitions], "q0": "q0",
                 "F": sorted(str(state.value) for state in machine.final_states)}
        (DEST / (profile["id"] + ".json")).write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        export_svg(profile, machine, transitions)
        summary.append({"profile": profile["id"], "states": len(machine.states),
                        "symbols": len(machine.symbols), "transitions": len(transitions)})
    (DEST / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
