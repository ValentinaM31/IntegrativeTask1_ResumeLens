"""Export complete five-tuples, tables and faithful diagrams from epsilon-NFAs."""
import csv
from html import escape
import json
from pathlib import Path
from resumelens.classification import build_profile_automaton, load_profiles, profile_branches

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs" / "automata"


def transitions_of(machine):
    return sorted((str(source.value), "ε" if symbol.value == "epsilon" else str(symbol.value), str(target.value))
                  for source, edges in machine.to_dict().items()
                  for symbol, targets in edges.items() for target in targets)


def export_svg(profile, machine, transitions):
    branches = profile_branches(profile)
    bucket_count = len(branches[0])
    width = 300 + bucket_count * 270
    graph_bottom = 170 + len(branches) * 220
    height = graph_bottom + 90 + bucket_count * 38
    positions = {"q0": (65, (graph_bottom + 100) / 2), "qf": (width - 65, (graph_bottom + 100) / 2)}
    for branch_index, groups in enumerate(branches):
        y = 210 + branch_index * 220
        for group_index, _ in enumerate(groups):
            positions[f"b{branch_index}_g{group_index}_before"] = (200 + group_index * 270, y)
            positions[f"b{branch_index}_g{group_index}_seen"] = (330 + group_index * 270, y)
    elements = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                '<rect width="100%" height="100%" fill="white"/>',
                '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#345566"/></marker></defs>',
                '<style>text{font-family:Arial,sans-serif;fill:#16384d}.edge{fill:none;stroke:#345566;stroke-width:1.5;marker-end:url(#arrow)}</style>',
                f'<text x="25" y="38" font-size="25" font-weight="bold">{escape(profile["id"])}</text>',
                '<text x="25" y="69" font-size="16">ε-NFA · arrow = transition · double circle = final · A / R labels are defined below.</text>',
                '<text x="25" y="95" font-size="15">before / seen = required member not yet seen / seen in this bucket. No ε edge bypasses a requirement.</text>']
    # Group parallel transitions without changing their relation.
    grouped = {}
    for source, symbol, target in transitions:
        grouped.setdefault((source, target), []).append(symbol)
    for (source, target), symbols in grouped.items():
        x1, y1 = positions[source]
        x2, y2 = positions[target]
        if source == target:
            group_index = int(source.split("_g")[1].split("_")[0])
            label = f"A{group_index}"
            path = f"M{x1-17},{y1-24} C{x1-55},{y1-100} {x1+55},{y1-100} {x1+17},{y1-24}"
            lx, ly = x1, y1 - 83
        else:
            path = f"M{x1+34},{y1} L{x2-34},{y2}"
            lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 - 14
            label = ", ".join(symbols)
            if label != "ε":
                branch_index = int(source.split("_g")[0][1:])
                group_index = int(source.split("_g")[1].split("_")[0])
                mandatory = branches[branch_index][group_index][1]
                label = f"A{group_index}" if mandatory == branches[branch_index][group_index][0] else f"R{branch_index},{group_index}"
        elements.append(f'<path class="edge" d="{path}"/>')
        elements.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="13">{escape(label)}</text>')
    for state in sorted(positions):
        x, y = positions[state]
        elements.append(f'<circle cx="{x}" cy="{y}" r="33" fill="#eef5f8" stroke="#16384d" stroke-width="1.5"/>')
        if state in {str(value.value) for value in machine.final_states}:
            elements.append(f'<circle cx="{x}" cy="{y}" r="28" fill="none" stroke="#16384d"/>')
        label = state if state in ("q0", "qf") else state.rsplit("_", 1)[-1]
        elements.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" font-size="13">{escape(label)}</text>')
        if state not in ("q0", "qf"):
            elements.append(f'<text x="{x}" y="{y+55}" text-anchor="middle" font-size="12">{escape(state)}</text>')
    qx, qy = positions["q0"]
    elements.append(f'<path class="edge" d="M5,{qy} L{qx-35},{qy}"/>')
    for branch_index, groups in enumerate(branches):
        pairs = profile.get("required_pair_alternatives", [])
        note = (f"R{branch_index},0 = {{{pairs[branch_index][0]}}}; R{branch_index},1 = {{{pairs[branch_index][1]}}} (compatible pair)"
                if pairs else "Each bucket requires at least one of its symbols.")
        elements.append(f'<text x="165" y="{300+branch_index*220}" font-size="15">Branch {branch_index}: {escape(note)}</text>')
    elements.append(f'<text x="25" y="{graph_bottom+25}" font-size="18" font-weight="bold">Complete bucket alphabets (all loop transitions)</text>')
    for group_index, (allowed, _) in enumerate(branches[0]):
        label = f"A{group_index} = {{" + ", ".join(sorted(allowed)) + "}"
        elements.append(f'<text x="25" y="{graph_bottom+62+group_index*38}" font-size="16">{escape(label)}</text>')
    elements.append('</svg>')
    (DEST / (profile["id"] + ".svg")).write_text("\n".join(elements), encoding="utf-8")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    summary = []
    for profile in load_profiles():
        machine = build_profile_automaton(profile)
        transitions = transitions_of(machine)
        model = {"profile": profile["id"], "type": "epsilon-NFA", "epsilon_label": "ε",
                 "Q": sorted(str(state.value) for state in machine.states),
                 "Sigma": sorted(str(symbol.value) for symbol in machine.symbols),
                 "delta": [list(row) for row in transitions], "q0": "q0", "F": ["qf"]}
        (DEST / (profile["id"] + ".json")).write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with (DEST / (profile["id"] + ".csv")).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["source", "input", "target"])
            writer.writerows(transitions)
        machine.write_as_dot(str(DEST / (profile["id"] + ".dot")))
        export_svg(profile, machine, transitions)
        summary.append({"profile": profile["id"], "states": len(machine.states),
                        "symbols": len(machine.symbols), "transitions": len(transitions)})
    (DEST / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
