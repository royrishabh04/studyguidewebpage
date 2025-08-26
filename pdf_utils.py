
from typing import List, Tuple
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.enums import TA_LEFT

# A4 constants
PAGE_W, PAGE_H = A4

def _grid_positions(cols: int, rows: int, margin_mm: float, gutter_mm: float):
    margin = margin_mm * mm
    gutter = gutter_mm * mm
    grid_w = PAGE_W - 2 * margin
    grid_h = PAGE_H - 2 * margin

    cell_w = (grid_w - (cols - 1) * gutter) / cols
    cell_h = (grid_h - (rows - 1) * gutter) / rows

    positions = []
    for r in range(rows):
        for c in range(cols):
            x = margin + c * (cell_w + gutter)
            y = PAGE_H - margin - (r + 1) * cell_h - r * gutter
            positions.append((x, y, cell_w, cell_h))
    return positions

def _mirror_positions_horiz(positions: List[tuple], cols: int, rows: int):
    """Mirror positions horizontally for the back page (long-edge duplex)."""
    mirrored = []
    for r in range(rows):
        row_positions = positions[r*cols:(r+1)*cols]
        row_positions = list(reversed(row_positions))
        mirrored.extend(row_positions)
    return mirrored

def _draw_card_frame(c: canvas.Canvas, x: float, y: float, w: float, h: float):
    c.rect(x, y, w, h)

def _draw_text_in_frame(c: canvas.Canvas, text: str, x: float, y: float, w: float, h: float, font_size: int):
    style = ParagraphStyle(
        name="Card",
        fontName="Helvetica",
        fontSize=font_size,
        leading=font_size * 1.2,
        alignment=TA_LEFT
    )
    frame = Frame(x + 6, y + 6, w - 12, h - 12, showBoundary=0)
    para = Paragraph(text.replace('\n', '<br/>'), style)
    frame.addFromList([para], c)

def export_flashcards_pdf(
    cards: List[Tuple[str, str]],
    output_path: str,
    cols: int = 2,
    rows: int = 4,
    margin_mm: float = 12,
    gutter_mm: float = 6,
    draw_borders: bool = True,
    question_font_size: int = 12,
    answer_font_size: int = 12,
):
    """
    Create a duplex-friendly PDF:
      - Front pages: questions arranged left->right, top->bottom.
      - Back pages: answers with **horizontally mirrored** positions per sheet.
    """
    c = canvas.Canvas(output_path, pagesize=A4)

    per_sheet = cols * rows
    positions_front = _grid_positions(cols, rows, margin_mm, gutter_mm)
    positions_back = _mirror_positions_horiz(positions_front, cols, rows)

    # Chunk cards into sheets
    for i in range(0, len(cards), per_sheet):
        chunk = cards[i:i+per_sheet]

        # FRONT (Questions)
        for idx, (q, _a) in enumerate(chunk):
            x, y, w, h = positions_front[idx]
            if draw_borders:
                _draw_card_frame(c, x, y, w, h)
            _draw_text_in_frame(c, q, x, y, w, h, question_font_size)
        c.showPage()

        # BACK (Answers)
        for idx, (_q, a) in enumerate(chunk):
            x, y, w, h = positions_back[idx]
            if draw_borders:
                _draw_card_frame(c, x, y, w, h)
            _draw_text_in_frame(c, a, x, y, w, h, answer_font_size)
        c.showPage()

    c.save()
