"""Documented finite patterns; offsets refer to the original Python text."""
import re
from .catalog import load_catalog, validate_catalog

FLAGS = re.IGNORECASE | re.MULTILINE
PATTERNS = {
    "name": r"^[ \t]*(?:Name|Nombre)[ \t]*:[ \t]*(?P<value>[^\r\n]+)",
    "emails": r"(?<![\w.+-])[A-Z0-9_%+-]+(?:\.[A-Z0-9_%+-]+)*@(?:[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?\.)+[A-Z]{2,}(?![\w-]|\.[A-Z0-9])",
    "phones": r"(?<![\w+\d])(?:\+57[ -]?)?3\d{2}[ -]?\d{3}[ -]?\d{4}(?![\w\d])",
    "links": r"https?://(?:www\.)?(?:linkedin\.com/in|github\.com)/[A-Z0-9_-]+(?:/[A-Z0-9_.-]+)*(?![\w/-])",
    "education_phrase": r"(?<!\w)(?:(?:Bachelor|Master)(?:'s)?(?: degree(?: (?:in|of) [^\r\n.;]+)?| (?:in|of) [^\r\n.;]+)|PhD(?: in [^\r\n.;]+)?|Ingeniería(?: de| en)? [^\r\n.;]+|Maestría(?: de| en)? [^\r\n.;]+|Doctorado(?: de| en)? [^\r\n.;]+)(?!\w)",
    "experience_phrase": r"(?<!\w)\d+(?:[.,]\d+)?[ \t]+(?:years? of experience|años? de experiencia)(?:[^\r\n.;]*)(?!\w)",
    "skills_header": r"^[ \t]*(?:Technical Skills|Skills|Habilidades(?: técnicas)?|Tecnologías|Tecnologias|Competencias)[ \t]*:",
    "section_header": r"^[ \t]*(?:[A-ZÁÉÍÓÚÑ][\w ÁÉÍÓÚÑáéíóúñ/-]{0,45})[ \t]*:",
    "section_title": r"^[ \t]*(?P<label>Education|Educación|Educacion|Degree|Título|Titulo|Experience|Experiencia|Work Experience|Professional Experience|Experiencia laboral|Technical Skills|Skills|Habilidades(?: técnicas)?|Tecnologías|Tecnologias|Competencias|Projects|Proyectos|Summary|Resumen|Contact|Contacto|Languages|Idiomas|Certifications|Certificaciones)(?:[ \t]*:[ \t]*(?P<value>[^\r\n]*))?[ \t]*$",
    "negation": r"(?<!\w)(?:no experience with|sin experiencia en|no knowledge of|sin conocimientos de|(?:I[ \t]+)?do not use|(?:I[ \t]+)?don't use|no tengo experiencia (?:en|con)|no uso)[ \t]+",
    "clause_boundary": r"[!?;\r\n]|\.(?=[ \t]|$)|(?<!\w)(?:but|however|pero|aunque|sin[ \t]+embargo)(?!\w)",
    "react_technical": r"(?<!\w)(?:develop(?:ed|ing|s)?|build(?:ing|s)?|built|work(?:ed|ing|s)?|desarroll(?:o|é|amos|ando)|trabaj(?:o|é|amos|ando))[^\r\n.!?;]{0,80}(?<!\w)(?:using|with|usando|con)[ \t]+$",
    "react_after": r"^[ \t]+(?:framework|library|biblioteca)(?!\w)",
    "pandas_before": r"(?<!\w)(?:I[ \t]+)?(?:use|used|using|uso|usé|usando|utilizo|utilicé|utilizando)[ \t]+$",
    "pandas_after": r"^[ \t]+(?:for[ \t]+(?:data[ \t]+(?:analysis|processing)|processing[ \t]+data|analysing[ \t]+data)|para[ \t]+(?:procesar[ \t]+datos|analizar[ \t]+datos|análisis[ \t]+de[ \t]+datos|procesamiento[ \t]+de[ \t]+datos))(?!\w)",
    "url": r"https?://[^\s,;]+",
}
REGEX = {key: re.compile(pattern, FLAGS) for key, pattern in PATTERNS.items()}


def evidence(match, group=0):
    start, end = match.span(group)
    return {"raw": match.string[start:end], "start": start, "end": end}


def _records(text, category):
    # A section line is evidence; company/institution fields are not inferred.
    marked, active, offset = [], False, 0
    labels = {"education": {"education", "educación", "educacion", "degree", "título", "titulo"},
              "experience": {"experience", "experiencia", "work experience", "professional experience", "experiencia laboral"}}
    for line in text.splitlines(keepends=True):
        header = REGEX["section_title"].fullmatch(line.rstrip("\r\n"))
        if header:
            active = header.group("label").casefold() in labels[category]
            if active and header.group("value") and header.group("value").strip():
                start, end = header.span("value")
                marked.append({"raw": line[start:end], "start": offset + start, "end": offset + end})
        elif REGEX["section_header"].match(line):
            active = False
        elif active and line.strip():
            start = re.match(r"[ \t]*(?:[-*•][ \t]+)?", line).end()
            end = len(line.rstrip())
            if start < end:
                marked.append({"raw": line[start:end], "start": offset + start, "end": offset + end})
        offset += len(line)
    phrases = [evidence(m) for m in REGEX[category + "_phrase"].finditer(text)
               if not any(x["start"] <= m.start() and m.end() <= x["end"] for x in marked)]
    return sorted(marked + phrases, key=lambda x: x["start"])


def skill_pattern(catalog):
    validate_catalog(catalog)
    aliases = [alias for skill in catalog["skills"] for alias in skill["aliases"]]
    alternatives = "|".join(re.escape(a) for a in sorted(aliases, key=lambda a: (-len(a), a.casefold())))
    return re.compile(r"(?<![\w.+-])(?:" + alternatives + r")(?![\w+-]|\.[\w])", re.IGNORECASE)


def _skill_contexts(text, pattern):
    ranges, active, offset = [], False, 0
    for line in text.splitlines(keepends=True):
        header = REGEX["skills_header"].match(line)
        title = REGEX["section_title"].fullmatch(line.rstrip("\r\n"))
        if header:
            active = True
            ranges.append((offset + header.end(), offset + len(line)))
        elif title and title.group("label").casefold() in {"skills", "technical skills", "habilidades", "habilidades técnicas", "tecnologías", "tecnologias", "competencias"}:
            active = True
        elif not line.strip() or title or REGEX["section_header"].match(line):
            active = False
        elif active:
            # Only list-like continuation lines; free prose ends the section.
            parts = re.split(r"[,;|]", re.sub(r"^[ \t]*[-*•][ \t]+", "", line.strip()).rstrip("."))
            if parts and all(pattern.fullmatch(part.strip()) for part in parts if part.strip()):
                ranges.append((offset, offset + len(line)))
            else:
                active = False
        offset += len(line)
    return ranges


def _clause_prefix(text, start):
    """Text preceding a mention, bounded by its line and clause."""
    line_start = max(text.rfind("\n", 0, start), text.rfind("\r", 0, start)) + 1
    prefix = text[line_start:start]
    boundaries = list(REGEX["clause_boundary"].finditer(prefix))
    return prefix[boundaries[-1].end():] if boundaries else prefix


def _negative_list_prefix(remainder, pattern):
    """Accept an empty prefix or known aliases followed by a list separator."""
    while remainder.strip():
        found = pattern.match(remainder)
        if not found:
            return False
        remainder = remainder[found.end():]
        separator = re.match(r"[ \t]*(?:[,/]|\b(?:and|or|y|o)\b)[ \t]*", remainder, re.IGNORECASE)
        if not separator:
            return False
        remainder = remainder[separator.end():]
    return True


def _negated(text, match, pattern):
    """A supported phrase negates only the immediate mention or its explicit list."""
    prefix = _clause_prefix(text, match.start())
    markers = list(REGEX["negation"].finditer(prefix))
    return any(_negative_list_prefix(prefix[m.end():], pattern) for m in markers)


def _react_context(text, match, contexts):
    if any(start <= match.start() < end for start, end in contexts):
        return True
    prefix = _clause_prefix(text, match.start())
    return bool(REGEX["react_technical"].search(prefix)
                or REGEX["react_after"].match(text[match.end():]))


def _pandas_context(text, match, contexts):
    """Skills section or explicit use for data analysis/processing."""
    if any(start <= match.start() < end for start, end in contexts):
        return True
    prefix = _clause_prefix(text, match.start())
    return bool(REGEX["pandas_before"].search(prefix)
                and REGEX["pandas_after"].match(text[match.end():]))


def extract_resume(text, name=None, catalog=None):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("The resume must contain nonempty text")
    catalog = load_catalog() if catalog is None else catalog
    matches = [m for m in REGEX["name"].finditer(text) if m.group("value").strip()]
    candidate = {"name": matches[0].group("value").strip() if matches else (name.strip() if name and name.strip() else None)}
    for category in ("emails", "phones", "links"):
        candidate[category] = [evidence(m) for m in REGEX[category].finditer(text)]
    candidate["phones"] = [item for item in candidate["phones"]
                           if not re.search(r"\+\d{1,3}[ -]+$", text[max(0, item["start"]-6):item["start"]])]
    for category in ("education", "experience"):
        candidate[category] = _records(text, category)
    pattern = skill_pattern(catalog)
    contexts = _skill_contexts(text, pattern)
    urls = [m.span() for m in REGEX["url"].finditer(text)]
    emails = [m.span() for m in REGEX["emails"].finditer(text)]
    ambiguous = {a.casefold() for a in catalog["ambiguous_aliases"]}
    positive, excluded = [], []
    for match in pattern.finditer(text):
        item, reason = evidence(match), None
        if any(start <= match.start() < end for start, end in urls):
            reason = "Mention inside a URL"
        elif any(start <= match.start() < end for start, end in emails):
            reason = "Mention inside an email address"
        elif _negated(text, match, pattern):
            reason = "Explicit simple negation"
        elif match.group().casefold() == "react" and not _react_context(text, match, contexts):
            reason = "React without supported technical context"
        elif match.group().casefold() == "pandas" and not _pandas_context(text, match, contexts):
            reason = "Pandas without supported technical context"
        elif match.group().casefold() in ambiguous and match.group().casefold() not in {"react", "pandas"} and not any(start <= match.start() < end for start, end in contexts):
            reason = "Ambiguous alias outside a skills section"
        if reason:
            excluded.append({**item, "reason": reason})
        else:
            positive.append(item)
    warnings = []
    if candidate["name"] is None:
        warnings.append("Name not found; use Name: or --name")
    if len(matches) > 1:
        warnings.append("Multiple explicit names; keeping the first")
    return {"candidate": candidate, "extracted_skills": positive, "excluded_mentions": excluded, "warnings": warnings}
