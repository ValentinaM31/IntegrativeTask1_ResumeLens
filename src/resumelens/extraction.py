"""Candidate data extraction."""
import re

FLAGS = re.IGNORECASE | re.MULTILINE
PATTERNS = {'name': '^[ \\t]*(?:Name|Nombre)[ \\t]*:[ \\t]*(?P<value>[^\\r\\n]+)',
 'emails': '(?<![\\w.+-])[A-Z0-9_%+-]+(?:\\.[A-Z0-9_%+-]+)*@(?:[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?\\.)+[A-Z]{2,}(?![\\w-]|\\.[A-Z0-9])',
 'phones': '(?<![\\w+\\d])(?:\\+57[ -]?)?3\\d{2}[ -]?\\d{3}[ -]?\\d{4}(?![\\w\\d])',
 'links': 'https?://(?:www\\.)?(?:linkedin\\.com/in|github\\.com)/[A-Z0-9_-]+(?:/[A-Z0-9_.-]+)*(?![\\w/-])',
 'education_phrase': "(?<!\\w)(?:(?:Bachelor|Master)(?:'s)?(?: degree(?: (?:in|of) [^\\r\\n.;]+)?| "
                     '(?:in|of) [^\\r\\n.;]+)|PhD(?: in [^\\r\\n.;]+)?|Ingeniería(?: de| en)? '
                     '[^\\r\\n.;]+|Maestría(?: de| en)? [^\\r\\n.;]+|Doctorado(?: de| en)? '
                     '[^\\r\\n.;]+)(?!\\w)',
 'experience_phrase': '(?<!\\w)\\d+(?:[.,]\\d+)?[ \\t]+(?:years? of experience|años? de '
                      'experiencia)(?:[^\\r\\n.;]*)(?!\\w)',
 'section_header': '^[ \\t]*(?:[A-ZÁÉÍÓÚÑ][\\w ÁÉÍÓÚÑáéíóúñ/-]{0,45})[ \\t]*:',
 'section_title': '^[ '
                  '\\t]*(?P<label>Education|Educación|Educacion|Degree|Título|Titulo|Experience|Experiencia|Work '
                  'Experience|Professional Experience|Experiencia laboral|Technical '
                  'Skills|Skills|Habilidades(?: '
                  'técnicas)?|Tecnologías|Tecnologias|Competencias|Projects|Proyectos|Summary|Resumen|Contact|Contacto|Languages|Idiomas|Certifications|Certificaciones)(?:[ '
                  '\\t]*:[ \\t]*(?P<value>[^\\r\\n]*))?[ \\t]*$'}
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

def extract_resume(text, name=None):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("The resume must contain nonempty text")
    matches = [m for m in REGEX["name"].finditer(text) if m.group("value").strip()]
    candidate = {"name": matches[0].group("value").strip() if matches else (name.strip() if name and name.strip() else None)}
    for category in ("emails", "phones", "links"):
        candidate[category] = [evidence(m) for m in REGEX[category].finditer(text)]
    candidate["phones"] = [item for item in candidate["phones"]
                           if not re.search(r"\+\d{1,3}[ -]+$", text[max(0, item["start"]-6):item["start"]])]
    for category in ("education", "experience"):
        candidate[category] = _records(text, category)
    warnings = []
    if candidate["name"] is None:
        warnings.append("Name not found; use Name: or --name")
    if len(matches) > 1:
        warnings.append("Multiple explicit names; keeping the first")
    return {"candidate": candidate, "warnings": warnings}
