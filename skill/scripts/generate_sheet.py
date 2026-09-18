#!/usr/bin/env python3
"""Generate an expandable, semantic, fillable PF2e character sheet."""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
from typing import Any, Iterable

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.pdfbase.acroform import AcroForm
from reportlab.pdfgen import canvas

GREEN = HexColor("#173F32")
BURGUNDY = HexColor("#6F2C2A")
PARCHMENT = HexColor("#F7F1E4")
PALE_GREEN = HexColor("#E9F0EA")
GRAY = HexColor("#5D625F")


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (list, tuple)):
        return ", ".join(text(item) for item in value)
    return str(value)


def chunks(items: list[Any], size: int) -> Iterable[tuple[int, list[Any]]]:
    for start in range(0, len(items), size):
        yield start, items[start : start + size]


class Sheet:
    def __init__(self, output: Path, pagesize=LETTER):
        self.output = output
        self.c = canvas.Canvas(str(output), pagesize=pagesize, pageCompression=1)
        self.form: AcroForm = self.c.acroForm
        self.width, self.height = pagesize
        self.margin = 30
        self.page_no = 0
        self.current_title = ""
        self.current_subtitle = ""
        self.page_meta: list[tuple[str, str]] = []

    def begin(self, title: str, subtitle: str = "") -> None:
        if self.page_no:
            self.c.showPage()
        self.page_no += 1
        self.current_title = title
        self.current_subtitle = subtitle
        self.page_meta.append((title, subtitle))
        self.c.setFillColor(PARCHMENT)
        self.c.rect(0, 0, self.width, self.height, stroke=0, fill=1)
        self.c.setFillColor(GREEN)
        self.c.setFont("Helvetica-Bold", 17)
        self.c.drawString(30, self.height - 40, title.upper())
        self.c.setStrokeColor(BURGUNDY)
        self.c.setLineWidth(2)
        self.c.line(30, self.height - 52, self.width - 30, self.height - 52)

    def footer(self) -> None:
        return

    def section(self, x: float, y: float, width: float, title: str) -> float:
        self.c.setFillColor(GREEN)
        self.c.setFont("Helvetica-Bold", 9)
        self.c.drawString(x, y, title.upper())
        self.c.setStrokeColor(GREEN)
        self.c.setLineWidth(1.2)
        label_width = min(width * 0.55, self.c.stringWidth(title.upper(), "Helvetica-Bold", 9) + 8)
        self.c.line(x + label_width, y + 2, x + width, y + 2)
        return y - 16

    def field(self, name: str, x: float, y: float, width: float, height: float = 18,
              value: Any = "", label: str | None = None, multiline: bool = False,
              font_size: float = 8) -> None:
        if label:
            self.c.setFillColor(GRAY)
            self.c.setFont("Helvetica", 6.5)
            self.c.drawString(x, y + height + 2, label)
        flags = 4096 if multiline else 0
        self.form.textfield(
            name=name, value=text(value), x=x, y=y, width=width, height=height,
            borderColor=BURGUNDY, fillColor=white, textColor=black,
            borderWidth=0.8, forceBorder=True, fontName="Helvetica",
            fontSize=font_size, fieldFlags=flags,
        )

    def checkbox(self, name: str, x: float, y: float, checked: bool, label: str) -> None:
        self.form.checkbox(
            name=name, x=x, y=y, size=9, checked=checked,
            buttonStyle="check", borderColor=GREEN, fillColor=white,
            textColor=BURGUNDY, forceBorder=True,
        )
        self.c.setFillColor(black)
        self.c.setFont("Helvetica", 6.5)
        self.c.drawString(x + 12, y + 1, label)

    def rank_pips(self, prefix: str, rank: str, x: float, y: float) -> None:
        ranks = ["trained", "expert", "master", "legendary"]
        for index, item in enumerate(ranks):
            self.checkbox(f"{prefix}.{item}", x + index * 27, y, rank == item, item[0].upper())

    def save(self) -> None:
        self.c.save()


def core_page(sheet: Sheet, data: dict[str, Any]) -> None:
    identity = data.get("identity", {})
    abilities = data.get("abilities", {})
    profs = data.get("proficiencies", {})
    computed = data.get("computed", {}).get("pathbuilder", {})
    ac = computed.get("ac") or {}
    sheet.begin("Pathfinder Character", "Core statistics")
    left, top = sheet.margin, sheet.height - 72
    usable = sheet.width - 2 * sheet.margin
    gap = 8
    third = (usable - 2 * gap) / 3
    sheet.field("identity.name", left, top - 18, third * 1.45, value=identity.get("name"), label="CHARACTER NAME", font_size=11)
    sheet.field("identity.level", left + third * 1.45 + gap, top - 18, 52, value=identity.get("level"), label="LEVEL", font_size=11)
    sheet.field("identity.xp", left + third * 1.45 + gap + 60, top - 18, 60, value=identity.get("xp"), label="XP")
    sheet.field("identity.class", left, top - 51, third, value=identity.get("class"), label="CLASS")
    sheet.field("identity.ancestry", left + third + gap, top - 51, third, value=identity.get("ancestry"), label="ANCESTRY")
    sheet.field("identity.background", left + 2 * (third + gap), top - 51, third, value=identity.get("background"), label="BACKGROUND")
    y = top - 86
    y = sheet.section(left, y, usable, "Attributes")
    ability_names = [("str", "Strength"), ("dex", "Dexterity"), ("con", "Constitution"), ("int", "Intelligence"), ("wis", "Wisdom"), ("cha", "Charisma")]
    box_w = (usable - 5 * gap) / 6
    for i, (key, label) in enumerate(ability_names):
        x = left + i * (box_w + gap)
        sheet.field(f"abilities.{key}", x, y - 25, box_w, 25, abilities.get(key), label, font_size=13)
    y -= 55
    y = sheet.section(left, y, usable, "Defenses and perception")
    defense_names = [("ac", "Armor Class", ac.get("acTotal")), ("fortitude", "Fortitude", ""), ("reflex", "Reflex", ""), ("will", "Will", ""), ("perception", "Perception", "")]
    defense_w = (usable - 4 * gap) / 5
    for i, (key, label, value) in enumerate(defense_names):
        x = left + i * (defense_w + gap)
        sheet.field(f"computed.pathbuilder.{key}", x, y - 23, defense_w, 23, value=value, label=label, font_size=12)
        if key in profs:
            sheet.rank_pips(f"proficiencies.{key}", profs[key].get("rank", "unknown"), x, y - 39)
    y -= 66
    column_gap = 12
    col = (usable - column_gap) / 2
    skill_y = sheet.section(left, y, col, "Skills")
    skill_keys = ["acrobatics", "arcana", "athletics", "crafting", "deception", "diplomacy", "intimidation", "medicine", "nature", "occultism", "performance", "religion", "society", "stealth", "survival", "thievery"]
    row_h = 22
    for idx, key in enumerate(skill_keys):
        yy = skill_y - idx * row_h
        sheet.c.setFillColor(black)
        sheet.c.setFont("Helvetica-Bold", 7)
        sheet.c.drawString(left, yy + 6, key.title())
        sheet.field(f"skills.{key}.modifier", left + 68, yy, 38, 16, value="", font_size=8)
        rank = profs.get(key, {}).get("rank", "unknown")
        sheet.rank_pips(f"proficiencies.{key}", rank, left + 114, yy + 3)
    right = left + col + column_gap
    ry = sheet.section(right, y, col, "Combat and movement")
    sheet.field("attributes.speed", right, ry - 20, 70, 20, data.get("attributes", {}).get("speed"), "SPEED")
    sheet.field("hitPoints.maximum", right + 78, ry - 20, 70, 20, "", "MAX HP")
    sheet.field("hitPoints.current", right + 156, ry - 20, 70, 20, "", "CURRENT HP")
    ry -= 52
    for idx, weapon in enumerate(data.get("weapons", [])[:5]):
        yy = ry - idx * 47
        sheet.field(f"weapons.{idx}.name", right, yy, col * 0.42, 18, weapon.get("name"), f"STRIKE {idx + 1}")
        sheet.field(f"weapons.{idx}.attack", right + col * 0.44, yy, 48, 18, weapon.get("computed", {}).get("attack"), "ATTACK")
        sheet.field(f"weapons.{idx}.damage", right + col * 0.44 + 54, yy, col * 0.35, 18, weapon.get("computed", {}).get("damageBonus"), "DAMAGE")
        sheet.field(f"weapons.{idx}.traits", right, yy - 20, col, 15, text(weapon.get("propertyRunes")), "RUNES / NOTES", font_size=7)
    visible_weapons = max(1, min(5, len(data.get("weapons", []))))
    notes_top = ry - visible_weapons * 47 - 12
    notes_y = 68
    sheet.field("core.notes", right, notes_y, col, max(48, notes_top - notes_y), "", "COMBAT NOTES", multiline=True, font_size=7)
    sheet.footer()


def table_page(sheet: Sheet, title: str, subtitle: str, prefix: str,
               rows: list[dict[str, Any]], columns: list[tuple[str, str, float]],
               rows_per_page: int = 24) -> None:
    for start, page_rows in chunks(rows or [{}], rows_per_page):
        sheet.begin(title, subtitle if start == 0 else f"{subtitle} - continued")
        left, top = sheet.margin, sheet.height - 70
        usable = sheet.width - 2 * sheet.margin
        widths = [usable * fraction for _, _, fraction in columns]
        x = left
        sheet.c.setFillColor(GREEN)
        sheet.c.rect(left, top - 4, usable, 18, stroke=0, fill=1)
        sheet.c.setFillColor(white)
        sheet.c.setFont("Helvetica-Bold", 7)
        for (_, label, _), width in zip(columns, widths):
            sheet.c.drawString(x + 3, top + 1, label.upper())
            x += width
        y = top - 24
        row_h = min(27, (top - 55) / rows_per_page)
        for local_idx in range(rows_per_page):
            absolute = start + local_idx
            row = page_rows[local_idx] if local_idx < len(page_rows) else {}
            x = left
            for (key, _, _), width in zip(columns, widths):
                value = row.get(key, "") if isinstance(row, dict) else ""
                sheet.field(f"{prefix}.{absolute}.{key}", x, y, width - 3, row_h - 4, value, font_size=7)
                x += width
            y -= row_h
        sheet.footer()


def advancement_pages(sheet: Sheet, data: dict[str, Any]) -> None:
    rows = []
    for feat in data.get("feats", []):
        rows.append({"level": feat.get("level"), "category": feat.get("category"), "name": feat.get("name"), "selection": feat.get("selection") or feat.get("choiceTrack")})
    table_page(sheet, "Advancement", "Feats and features", "feats", rows,
               [("level", "Level", .08), ("category", "Category", .22), ("name", "Feat / feature", .34), ("selection", "Selection / source", .36)], 24)


def inventory_pages(sheet: Sheet, data: dict[str, Any]) -> None:
    rows = []
    for item in data.get("inventory", {}).get("equipment", []):
        rows.append({"name": item.get("name"), "quantity": item.get("quantity"), "container": item.get("containerId"), "invested": item.get("invested")})
    for item in data.get("armor", []) + data.get("shields", []):
        rows.append({"name": item.get("name"), "quantity": item.get("quantity"), "container": "Worn", "invested": ""})
    table_page(sheet, "Inventory", "Equipment, armor, and shields", "inventory.equipment", rows,
               [("name", "Item", .44), ("quantity", "Qty", .10), ("container", "Container", .28), ("invested", "Invested", .18)], 25)


def spell_pages(sheet: Sheet, data: dict[str, Any]) -> None:
    for caster_index, caster in enumerate(data.get("spellcasting", [])):
        source = caster.get("name") or f"Source {caster_index + 1}"
        sheet.begin("Spellcasting", source)
        left, top = sheet.margin, sheet.height - 78
        usable = sheet.width - 2 * sheet.margin
        sheet.field(f"spellcasting.{caster_index}.name", left, top - 18, usable * .30, value=source, label="CASTING SOURCE")
        sheet.field(f"spellcasting.{caster_index}.tradition", left + usable * .32, top - 18, usable * .18, value=caster.get("tradition"), label="TRADITION")
        sheet.field(f"spellcasting.{caster_index}.castingType", left + usable * .52, top - 18, usable * .18, value=caster.get("castingType"), label="TYPE")
        sheet.field(f"spellcasting.{caster_index}.ability", left + usable * .72, top - 18, usable * .12, value=caster.get("ability"), label="ABILITY")
        sheet.field(f"spellcasting.{caster_index}.focusPoints", left + usable * .86, top - 18, usable * .14, value=caster.get("focusPoints"), label="FOCUS")
        y = top - 60
        y = sheet.section(left, y, usable, "Slots and spells by rank") - 30
        rank_sources = caster.get("repertoire") or caster.get("knownOrAvailable") or {}
        prepared = caster.get("prepared") or {}
        rank_keys = sorted(set(rank_sources) | set(prepared) | set(caster.get("slotsPerDay", {})), key=lambda item: int(item))
        if not rank_keys:
            rank_keys = [str(i) for i in range(11)]
        row_h = 54
        for rank in rank_keys[:11]:
            if y - row_h < 55:
                sheet.footer()
                sheet.begin("Spellcasting", f"{source} - continued")
                y = sheet.height - 75
            sheet.c.setFillColor(BURGUNDY)
            sheet.c.setFont("Helvetica-Bold", 10)
            sheet.c.drawString(left, y + 25, "Cantrips" if rank == "0" else f"Rank {rank}")
            sheet.field(f"spellcasting.{caster_index}.slotsPerDay.{rank}", left, y, 48, 20, caster.get("slotsPerDay", {}).get(rank, ""))
            sheet.field(f"spellcasting.{caster_index}.spells.{rank}", left + 58, y, usable * .43, 36, text(rank_sources.get(rank, [])), "KNOWN / REPERTOIRE", multiline=True, font_size=7)
            sheet.field(f"spellcasting.{caster_index}.prepared.{rank}", left + 64 + usable * .43, y, usable - 64 - usable * .43, 36, text(prepared.get(rank, [])), "PREPARED", multiline=True, font_size=7)
            y -= row_h
        focus_entries = [
            (focus_index, entry)
            for focus_index, entry in enumerate(data.get("focus", {}).get("entries", []))
            if entry.get("tradition") == caster.get("tradition")
            and entry.get("ability") == caster.get("ability")
        ]
        if focus_entries:
            if y < 115:
                sheet.footer()
                sheet.begin("Spellcasting", f"{source} - focus magic")
                y = sheet.height - 75
            y = sheet.section(left, y, usable, "Focus magic") - 38
            for focus_index, entry in focus_entries:
                sheet.field(
                    f"focus.entries.{focus_index}.cantrips", left, y, usable * .48, 34,
                    text(entry.get("cantrips", [])), "FOCUS CANTRIPS", multiline=True, font_size=7,
                )
                sheet.field(
                    f"focus.entries.{focus_index}.spells", left + usable * .51, y, usable * .49, 34,
                    text(entry.get("spells", [])), "FOCUS SPELLS", multiline=True, font_size=7,
                )
                y -= 48
        sheet.footer()


def supplemental_pages(sheet: Sheet, data: dict[str, Any]) -> None:
    rows = []
    for index, item in enumerate(data.get("companions", [])):
        rows.append({"kind": "Companion", "name": item.get("data", {}).get("name"), "details": json.dumps(item.get("data", {}), ensure_ascii=False)})
    for index, item in enumerate(data.get("familiars", [])):
        rows.append({"kind": "Familiar", "name": item.get("data", {}).get("name"), "details": json.dumps(item.get("data", {}), ensure_ascii=False)})
    for item in data.get("formulas", []):
        rows.append({"kind": "Formula", "name": text(item.get("known")), "details": item.get("type")})
    for item in data.get("rituals", []):
        rows.append({"kind": "Ritual", "name": item.get("name"), "details": ""})
    for item in data.get("resistances", []):
        rows.append({"kind": "Resistance", "name": item.get("raw"), "details": ""})
    if rows:
        table_page(sheet, "Additional Character Data", "Companions, familiars, crafting, and rituals", "supplemental", rows,
                   [("kind", "Type", .17), ("name", "Name", .31), ("details", "Details", .52)], 18)


def flatten_pdf(path: Path) -> None:
    reader = PdfReader(str(path))
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    fields = writer.get_fields() or {}
    values = {name: field.get("/V", "/Off" if field.get("/FT") == "/Btn" else "") for name, field in fields.items()}
    writer.update_page_form_field_values(None, values, auto_regenerate=False, flatten=True)
    writer.remove_annotations(subtypes="/Widget")
    writer.root_object.pop(NameObject("/AcroForm"), None)
    with path.open("wb") as stream:
        writer.write(stream)


def add_page_chrome(path: Path, pagesize: tuple[float, float], metadata: list[tuple[str, str]]) -> None:
    width, height = pagesize
    source = PdfReader(str(path))
    writer = PdfWriter()
    writer.clone_document_from_reader(source)
    for page_no, (title, subtitle) in enumerate(metadata, 1):
        buffer = io.BytesIO()
        overlay = canvas.Canvas(buffer, pagesize=pagesize, pageCompression=0)
        if subtitle:
            overlay.setFillColor(GRAY)
            overlay.setFont("Helvetica", 7.5)
            overlay.drawRightString(width - 30, height - 39, subtitle)
        overlay.setFillColor(GRAY)
        overlay.setFont("Helvetica", 6.5)
        overlay.drawString(30, 17, "PF2e semantic character sheet - Paizo-inspired original layout")
        overlay.drawRightString(width - 30, 17, f"Page {page_no}")
        overlay.showPage()
        overlay.save()
        buffer.seek(0)
        writer.pages[page_no - 1].merge_page(PdfReader(buffer).pages[0], over=True)
    temporary = path.with_suffix(".chrome.pdf")
    with temporary.open("wb") as stream:
        writer.write(stream)
    temporary.replace(path)


def generate(data: dict[str, Any], output: Path, paper: str = "letter", flatten: bool = False) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    pagesize = A4 if paper.lower() == "a4" else LETTER
    sheet = Sheet(output, pagesize)
    core_page(sheet, data)
    if data.get("feats") or data.get("specials"):
        advancement_pages(sheet, data)
    if data.get("inventory", {}).get("equipment") or data.get("armor") or data.get("shields"):
        inventory_pages(sheet, data)
    spell_pages(sheet, data)
    supplemental_pages(sheet, data)
    sheet.save()
    add_page_chrome(output, pagesize, sheet.page_meta)
    if flatten:
        flatten_pdf(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Normalized character JSON")
    parser.add_argument("output", type=Path, help="Output PDF")
    parser.add_argument("--paper", choices=("letter", "a4"), default="letter")
    parser.add_argument("--flatten", action="store_true")
    args = parser.parse_args()
    with args.input.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    generate(data, args.output, args.paper, args.flatten)


if __name__ == "__main__":
    main()
