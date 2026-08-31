"""Converte il markdown salvato di un AuditPresentation in slide reveal.js.
Il markdown è sempre nella forma prodotta da app/audits/service.py
(_assemble_markdown): un piccolo parser dedicato basta, non serve una
dipendenza markdown generica — il formato è fisso e controllato da noi, non è
markdown arbitrario da un utente."""
from dataclasses import dataclass
from markupsafe import escape


@dataclass(frozen=True)
class Slide:
    kind: str  # "title" | "content"
    heading: str
    lines: list[str]  # sotto-titolo/meta per "title", bullet per "content"


def parse_markdown(markdown: str) -> list[Slide]:
    blocks = markdown.split("\n\n---\n\n")
    slides = []
    for block in blocks:
        lines = [line for line in block.strip().splitlines() if line.strip()]
        if not lines:
            continue
        first = lines[0].strip()
        if first.startswith("# "):
            heading = first[2:].strip()
            meta = [line.strip() for line in lines[1:]]
            slides.append(Slide(kind="title", heading=heading, lines=meta))
        elif first.startswith("## "):
            heading = first[3:].strip()
            bullets = [line.strip()[2:].strip() for line in lines[1:] if line.strip().startswith("- ")]
            slides.append(Slide(kind="content", heading=heading, lines=bullets))
    return slides


def slides_to_html(slides: list[Slide]) -> str:
    """HTML delle sole <section> (nessun documento completo) — usato dal
    template reveal.js, che ci mette intorno chrome/branding/script."""
    parts = []
    for slide in slides:
        if slide.kind == "title":
            meta_html = "".join(f"<p class='audit-meta'>{escape(line).replace('_', '')}</p>" for line in slide.lines)
            parts.append(f"<section class='audit-title-slide'><h1>{escape(slide.heading)}</h1>{meta_html}</section>")
        else:
            items = "".join(f"<li>{escape(b)}</li>" for b in slide.lines)
            parts.append(f"<section><h2>{escape(slide.heading)}</h2><ul>{items}</ul></section>")
    return "\n".join(parts)
