"""Generate and validate the candidate language using textX, not JSON Schema."""
from functools import lru_cache
from importlib.resources import files
import json
from textx import metamodel_from_str
from .classification import classify_skills


@lru_cache(maxsize=1)
def _metamodel():
    grammar = files("resumelens").joinpath("candidate.tx").read_text(encoding="utf-8")
    return metamodel_from_str(grammar, autokwd=True)


def generate_candidate_dsl(first_stage, classification):
    candidate = first_stage["candidate"]
    quote = lambda value: json.dumps(value, ensure_ascii=False)
    lines = ["candidate {", "  name " + quote(candidate["name"]) + ";", "  contacts {"]
    for key, kind in (("emails", "email"), ("phones", "phone"), ("links", "link")):
        lines.extend(f"    {kind} {quote(item['raw'])};" for item in candidate[key])
    lines.append("  }")
    for key in ("education", "experience"):
        lines.append("  " + key + " {")
        lines.extend(f"    record {quote(item['raw'])};" for item in candidate[key])
        lines.append("  }")
    lines.append("  skills {")
    lines.extend(f"    skill {skill};" for skill in first_stage["normalized_skills"])
    lines.extend(["  }", "  accepted_profiles {"])
    lines.extend(f"    profile {profile};" for profile in classification["accepted_profiles"])
    lines.extend(["  }", "}"])
    return "\n".join(lines) + "\n"


def parse_candidate_dsl(source):
    """Return only data reconstructed from a valid textX model.

    Lexical/syntactic errors are textX exceptions. Additional semantic checks
    reject duplicate symbols and classification claims inconsistent with the NFA.
    """
    if not isinstance(source, str):
        raise ValueError("Candidate DSL must be text")
    model = _metamodel().model_from_str(source)
    skills = [entry.value for entry in model.skills]
    profiles = [entry.value for entry in model.profiles]
    if len(skills) != len(set(skills)) or len(profiles) != len(set(profiles)):
        raise ValueError("Duplicate skills or accepted profiles in DSL")
    if sorted(profiles) != classify_skills(skills)["accepted_profiles"]:
        raise ValueError("Accepted profiles are inconsistent with the automata")
    return {"name": json.loads(model.name),
            "contacts": [{"kind": entry.kind, "value": json.loads(entry.value)} for entry in model.contacts],
            "education": [json.loads(entry.value) for entry in model.education],
            "experience": [json.loads(entry.value) for entry in model.experience],
            "skills": skills, "accepted_profiles": profiles}
