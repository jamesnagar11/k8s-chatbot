import logfire


def _parse_docx(file_path: str) -> str:
    """Extract text (paragraphs + tables) from a .docx using python-docx."""
    from docx import Document

    doc = Document(file_path)
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                parts.append(" | ".join(cells))
    return "\n".join(parts)


def _parse_pptx(file_path: str) -> str:
    """Extract text (text frames + tables) from a .pptx using python-pptx."""
    from pptx import Presentation

    prs = Presentation(file_path)
    parts: list[str] = []
    for i, slide in enumerate(prs.slides, 1):
        parts.append(f"--- Slide {i} ---")
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    text = "".join(run.text for run in para.runs).strip()
                    if text:
                        parts.append(text)
            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    cells = [c.text.strip() for c in row.cells if c.text.strip()]
                    if cells:
                        parts.append(" | ".join(cells))
    return "\n".join(parts)


def parse_office(file_path: str):
    """
    Parses Office documents (.docx, .pptx) locally.

    Uses python-docx / python-pptx directly instead of `unstructured`, whose
    `partition()` import hangs on this Windows/Python 3.14 setup.
    """
    with logfire.span("Office Document Parsing", filename=file_path):
        try:
            ext = file_path.lower().rsplit(".", 1)[-1]
            if ext == "docx":
                full_text = _parse_docx(file_path)
            elif ext == "pptx":
                full_text = _parse_pptx(file_path)
            else:
                raise ValueError(f"Unsupported office file type: {ext}")

            if not full_text.strip():
                logfire.warning(f"Parser returned empty text for {file_path}")
            else:
                logfire.info(f"Successfully parsed {len(full_text)} characters")

            return full_text
        except Exception as e:
            logfire.error(f"Office Parse Failed: {e}")
            raise e
