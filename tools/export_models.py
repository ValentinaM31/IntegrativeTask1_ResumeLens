"""Export septuples, complete relations and graphs from executable FSTs."""
import csv
from html import escape
import json
from pathlib import Path
from resumelens.normalization import build_transducers

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs" / "models"


def export_svg(category, machine, transitions):
    # Disjoint paths from q0. Each state is drawn once.
    branches = {}
    for source, char, target, output in transitions:
        branch = target.rsplit("_", 1)[0]
        branches.setdefault(branch, []).append((source, char, target, output))
    for rows in branches.values():
        rows.sort(key=lambda row: int(row[2].rsplit("_", 1)[1]))
    branches = sorted(branches.items())
    width = max(len(rows) for _, rows in branches) * 150 + 430
    height = len(branches) * 110 + 170
    y0 = height / 2
    elements = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                '<rect width="100%" height="100%" fill="white"/>',
                '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#475569"/></marker></defs>',
                '<style>text{font-family:Arial,sans-serif;fill:#111827} .edge{stroke:#475569;fill:none;marker-end:url(#arrow)}</style>',
                f'<text x="24" y="30" font-size="22">FST {escape(category)}</text>',
                '<text x="24" y="58" font-size="14">Input / output. ε = empty word. Double circle = final. Each path consumes a complete alias.</text>',
                f'<path class="edge" d="M8,{y0} L44,{y0}"/>',
                f'<circle cx="75" cy="{y0}" r="30" fill="#dbeafe" stroke="#2563eb"/>',
                f'<text x="75" y="{y0+4}" text-anchor="middle" font-size="13">q0</text>']
    for index, (_, rows) in enumerate(branches):
        y = 140 + index * 110
        for j, (source, char, target, output) in enumerate(rows):
            x = 220 + j * 150
            if j == 0:
                elements.append(f'<path class="edge" d="M105,{y0} L155,{y} L{x-38},{y}"/>')
                label_x = 170
            else:
                elements.append(f'<path class="edge" d="M{x-150+38},{y} L{x-38},{y}"/>')
                label_x = x - 75
            label = ("␠" if char == " " else char) + " / " + (output[0] if output else "ε")
            if output:
                # Canonical token beneath the last edge avoids long labels over nodes.
                label = ("␠" if char == " " else char) + " /"
                elements.append(f'<text x="{label_x}" y="{y+54}" text-anchor="middle" font-size="12">{escape(output[0])}</text>')
            elements.append(f'<text x="{label_x}" y="{y-42}" text-anchor="middle" font-size="13">{escape(label)}</text>')
            elements.append(f'<circle cx="{x}" cy="{y}" r="38" fill="#f8fafc" stroke="#475569"/>')
            if target in machine.final_states:
                elements.append(f'<circle cx="{x}" cy="{y}" r="33" fill="none" stroke="#475569"/>')
            elements.append(f'<text x="{x}" y="{y+4}" text-anchor="middle" font-size="10">{escape(target)}</text>')
    elements.append('</svg>')
    (DEST / f"{category}.svg").write_text("\n".join(elements), encoding="utf-8")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    summary = []
    for category, machine in build_transducers().items():
        transitions = sorted((source, char, target, list(output))
                             for (source, char), edges in machine.transitions.items()
                             for target, output in edges)
        model = {"Q": sorted(machine.states), "Sigma": sorted(machine.input_symbols),
                 "Gamma": sorted(machine.output_symbols), "q0": "q0", "F": sorted(machine.final_states),
                 "delta": [[s, c, t] for s, c, t, _ in transitions],
                 "omega": [{"transition": [s, c, t], "output": out} for s, c, t, out in transitions]}
        (DEST / f"{category}.json").write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with (DEST / f"{category}.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["source", "input", "target", "output"])
            writer.writerows((s, c, t, " ".join(out) if out else "ε") for s, c, t, out in transitions)
        machine.write_as_dot(str(DEST / f"{category}.dot"))
        export_svg(category, machine, transitions)
        summary.append({"category": category, "states": len(machine.states),
                        "transitions": len(transitions), "final_states": len(machine.final_states)})
    (DEST / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
