from pathlib import Path

import fitz

from .common import OUTPUT, ROOT, file_sha, manifest, write_json


def prepare(selected=None):
    docs = manifest()
    if selected and selected not in {d["doc_id"] for d in docs}:
        raise ValueError("Unknown document ID: " + selected)
    all_pdfs = list(ROOT.rglob("*.pdf"))
    reports = []
    for entry in docs:
        if selected and entry["doc_id"] != selected:
            continue
        pdf_path = ROOT / entry["pdf"]
        if not pdf_path.is_file():
            raise FileNotFoundError(pdf_path)
        same_name = [p for p in all_pdfs if p.name.casefold() == pdf_path.name.casefold()]
        if len(same_name) != 1:
            raise ValueError("Ambiguous PDF filename match for %s: %s" % (entry["doc_id"], same_name))
        document = fitz.open(pdf_path)
        pages = []
        for page_num, page in enumerate(document):
            width, height = page.rect.width, page.rect.height
            words = []
            # PyMuPDF text boxes are in unrotated page space. The rotation matrix
            # maps them to the same displayed geometry used by get_pixmap().
            for x0, y0, x1, y1, word, block, line, index in page.get_text("words", sort=True):
                box = fitz.Rect(x0, y0, x1, y1) * page.rotation_matrix
                coords = [box.x0 / width, box.y0 / height, box.x1 / width, box.y1 / height]
                if not all(0 <= v <= 1 for v in coords) or coords[0] >= coords[2] or coords[1] >= coords[3]:
                    continue
                words.append({"text": word, "bbox": [round(v, 6) for v in coords], "block": block, "line": line, "word": index})
            if not words:
                raise ValueError("No PDF text-layer words on %s page %s" % (entry["doc_id"], page_num))
            pages.append({"page_num": page_num, "width_pt": round(width, 3), "height_pt": round(height, 3), "rotation_deg": page.rotation, "words": words})
        prepared = {"doc_id": entry["doc_id"], "source_pdf": entry["pdf"], "pdf_sha256": file_sha(pdf_path), "coordinate_system": "displayed_page_top_left_normalized", "pages": pages}
        write_json(OUTPUT / "inputs" / (Path(entry["doc_id"]).stem + ".json"), prepared)
        reports.append({"doc_id": entry["doc_id"], "pdf": entry["pdf"], "pages": len(pages), "words": sum(len(p["words"]) for p in pages), "pdf_sha256": prepared["pdf_sha256"]})
    write_json(OUTPUT / "preparation.json", reports)
    return reports
