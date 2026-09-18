import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader


SCRIPT = Path(__file__).parents[2] / "skill" / "scripts" / "generate_sheet.py"
SPEC = importlib.util.spec_from_file_location("generate_sheet", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GenerateSheetTests(unittest.TestCase):
    def character(self):
        return {
            "identity": {"name": "Test Hero", "level": 8, "class": "Wizard", "ancestry": "Human", "background": "Scholar"},
            "abilities": {"str": 10, "dex": 14, "con": 12, "int": 20, "wis": 14, "cha": 10},
            "attributes": {"speed": 25},
            "proficiencies": {"arcana": {"rank": "master", "rankBonus": 6}},
            "feats": [{"name": f"Feat {index}", "level": index, "category": "Class Feat"} for index in range(1, 30)],
            "specials": [],
            "inventory": {"equipment": [{"name": "Spellbook", "quantity": 1, "containerId": "Backpack", "invested": False}]},
            "weapons": [], "armor": [], "shields": [],
            "spellcasting": [{"name": "Wizard", "tradition": "arcane", "castingType": "prepared", "ability": "int", "focusPoints": 1, "slotsPerDay": {"1": 3}, "knownOrAvailable": {"1": ["Force Barrage"]}, "prepared": {"1": ["Force Barrage"]}}],
            "focus": {"points": 1, "entries": [{"tradition": "arcane", "ability": "int", "cantrips": ["Protective Wards"], "spells": ["Hand of the Apprentice"]}]},
            "companions": [{"data": {"name": "Wolf"}}], "familiars": [], "formulas": [], "rituals": [], "resistances": [],
            "computed": {"pathbuilder": {"ac": {"acTotal": 24}}},
        }

    def test_interactive_sheet_has_semantic_fields_and_overflow_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sheet.pdf"
            MODULE.generate(self.character(), output)
            reader = PdfReader(str(output))
            fields = reader.get_fields() or {}
            self.assertGreaterEqual(len(reader.pages), 6)
            self.assertIn("identity.name", fields)
            self.assertIn("feats.28.name", fields)
            self.assertIn("spellcasting.0.prepared.1", fields)
            self.assertIn("focus.entries.0.cantrips", fields)
            self.assertIn("focus.entries.0.spells", fields)
            widgets = sum(len([a for a in (page.get("/Annots") or []) if a.get_object().get("/Subtype") == "/Widget"]) for page in reader.pages)
            self.assertGreater(widgets, 0)

    def test_flattened_sheet_has_no_form_or_widgets(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "flat.pdf"
            MODULE.generate(self.character(), output, flatten=True)
            reader = PdfReader(str(output))
            self.assertFalse(reader.get_fields())
            widgets = sum(len([a for a in (page.get("/Annots") or []) if a.get_object().get("/Subtype") == "/Widget"]) for page in reader.pages)
            self.assertEqual(widgets, 0)


if __name__ == "__main__":
    unittest.main()
