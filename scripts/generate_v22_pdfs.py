#!/usr/bin/env python3
"""Generate the player-facing HeartGold Generations v2.2 PDF set.

Availability, encounters, evolutions, and abilities are read from the same
engine sources used by the V2.2 automated tests.  The two unchanged legacy
documents are wrapped and stamped as V2.2 reference documents.
"""

from __future__ import annotations

import csv
from io import BytesIO
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

import generate_v22_availability as availability


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LEGACY = ROOT / ".release-tools/legacy-docs-v20"
MANIFEST = DOCS / "v22_availability_manifest.csv"
CONFIG = ROOT / "armips/data/v22_availability.json"

NAVY = colors.HexColor("#14213D")
GOLD = colors.HexColor("#F4B942")
RED = colors.HexColor("#C9373F")
PALE = colors.HexColor("#F7F3E8")
BLUE_PALE = colors.HexColor("#EAF0F8")
INK = colors.HexColor("#202632")
MUTED = colors.HexColor("#5D6675")

STYLES = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "V22Title", parent=STYLES["Title"], fontName="Helvetica-Bold",
    fontSize=25, leading=29, textColor=NAVY, alignment=TA_LEFT, spaceAfter=8,
)
SUBTITLE = ParagraphStyle(
    "V22Subtitle", parent=STYLES["Normal"], fontName="Helvetica",
    fontSize=10, leading=14, textColor=MUTED, spaceAfter=14,
)
H1 = ParagraphStyle(
    "V22H1", parent=STYLES["Heading1"], fontName="Helvetica-Bold",
    fontSize=15, leading=18, textColor=NAVY, spaceBefore=10, spaceAfter=7,
)
H2 = ParagraphStyle(
    "V22H2", parent=STYLES["Heading2"], fontName="Helvetica-Bold",
    fontSize=11, leading=14, textColor=RED, spaceBefore=7, spaceAfter=5,
)
BODY = ParagraphStyle(
    "V22Body", parent=STYLES["BodyText"], fontName="Helvetica",
    fontSize=8.5, leading=12, textColor=INK, spaceAfter=5,
)
SMALL = ParagraphStyle(
    "V22Small", parent=BODY, fontSize=7, leading=9, spaceAfter=0,
)
TINY = ParagraphStyle(
    "V22Tiny", parent=BODY, fontSize=5.7, leading=7, spaceAfter=0,
)
CELL = ParagraphStyle(
    "V22Cell", parent=BODY, fontSize=6.5, leading=8, spaceAfter=0,
)
CELL_SMALL = ParagraphStyle(
    "V22CellSmall", parent=BODY, fontSize=5.4, leading=6.4, spaceAfter=0,
)
CELL_HEADER = ParagraphStyle(
    "V22CellHeader", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white,
)
CELL_HEADER_SMALL = ParagraphStyle(
    "V22CellHeaderSmall", parent=CELL_SMALL, fontName="Helvetica-Bold",
    textColor=colors.white,
)


def human_constant(value: str) -> str:
    for prefix in ("SPECIES_", "ABILITY_", "ITEM_", "EVO_", "TYPE_"):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    words = value.replace("_", " ").lower().split()
    special = {"jr": "Jr.", "mr": "Mr.", "mimejr": "Mime Jr.", "ho": "Ho-Oh"}
    return " ".join(special.get(word, word.capitalize()) for word in words)


def p(text: object, style: ParagraphStyle = CELL) -> Paragraph:
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)


def draw_page(canv: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    width, height = doc.pagesize
    canv.saveState()
    canv.setFillColor(NAVY)
    canv.rect(0, height - 7 * mm, width, 7 * mm, fill=1, stroke=0)
    canv.setFillColor(GOLD)
    canv.rect(0, height - 7 * mm, 42 * mm, 7 * mm, fill=1, stroke=0)
    canv.setFont("Helvetica-Bold", 7)
    canv.setFillColor(NAVY)
    canv.drawString(6 * mm, height - 4.8 * mm, "HEARTGOLD GENERATIONS")
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 7)
    canv.drawString(
        doc.leftMargin, 7 * mm,
        getattr(doc, "release_line", "v2.2 - Stability & Complete National Dex"),
    )
    canv.drawRightString(width - doc.rightMargin, 7 * mm, f"Page {doc.page}")
    canv.restoreState()


def build_pdf(
    path: Path, title: str, subtitle: str, story: list, *, wide: bool = False,
    release: str = "v2.2", release_line: str = "v2.2 - Stability & Complete National Dex",
) -> None:
    pagesize = landscape(A4) if wide else A4
    doc = SimpleDocTemplate(
        str(path), pagesize=pagesize, rightMargin=10 * mm, leftMargin=10 * mm,
        topMargin=13 * mm, bottomMargin=13 * mm, title=title,
        author=f"HeartGold Generations {release}",
    )
    doc.release_line = release_line
    lead = [Paragraph(title, TITLE), Paragraph(subtitle, SUBTITLE)]
    doc.build(lead + story, onFirstPage=draw_page, onLaterPages=draw_page)


def table(data: list[list[object]], widths: list[float], *, font: float = 6.5) -> Table:
    converted = []
    for row_index, row in enumerate(data):
        if row_index == 0:
            style = CELL_HEADER if font >= 6 else CELL_HEADER_SMALL
        else:
            style = CELL if font >= 6 else CELL_SMALL
        converted.append([p(value, style) if not isinstance(value, Paragraph) else value for value in row])
    result = Table(converted, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), (colors.white, BLUE_PALE)),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#B7C0CE")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return result


def ability_pdf() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    text = (ROOT / "armips/data/mondata.s").read_text(encoding="utf-8")
    rows = [["Pokemon/form", "Ability 1", "Ability 2"]]
    for match in re.finditer(
        r'^mondata\s+(SPECIES_[A-Z0-9_]+),\s*"([^"]*)"\s*(.*?)(?=^mondata|\Z)',
        text, re.MULTILINE | re.DOTALL,
    ):
        species, name, body = match.groups()
        abilities = re.search(r"^\s*abilities\s+(ABILITY_[A-Z0-9_]+),\s*(ABILITY_[A-Z0-9_]+)", body, re.MULTILINE)
        if species == "SPECIES_NONE" or not abilities:
            continue
        label = name if name != "-----" else human_constant(species)
        rows.append([label, human_constant(abilities.group(1)), human_constant(abilities.group(2))])

    story = [
        Paragraph("v2.2 ability policy", H1),
        Paragraph(
            "Every released species has an operative ability path. Mechanics that are safe in the HGSS battle engine are implemented; high-risk modern mechanics use the documented stable substitutes below.", BODY,
        ),
        table(
            [["Pokemon/form", "Original", "v2.2 replacement"]] + [
                [human_constant(x["species"]), human_constant(x["original"]), human_constant(x["replacement"])]
                for x in config["ability_substitutions"]
            ],
            [70 * mm, 70 * mm, 70 * mm],
        ),
        Paragraph("New or completed mechanics", H1),
        Paragraph(
            "Comatose, Ice Face, Schooling, Shields Down, Hunger Switch, Gulp Missile, Zero to Hero, Protosynthesis, Quark Drive, Hospitality, Opportunist, Stakeout, Cheek Pouch, Cotton Down and Toxic Chain are connected to battle-engine handlers in v2.2.", BODY,
        ),
        Paragraph("Complete current ability matrix", H1),
        table(rows, [92 * mm, 58 * mm, 58 * mm]),
    ]
    build_pdf(DOCS / "Ability Changes.pdf", "Ability Changes", "Complete v2.2 ability matrix and modern-mechanic policy", story, wide=True)


def evolution_requirement(method: str, parameter: str) -> str:
    value = human_constant(parameter) if parameter.startswith(("ITEM_", "MOVE_", "SPECIES_")) else parameter
    names = {
        "EVO_LEVEL": f"Level {parameter}",
        "EVO_LEVEL_DAY": f"Level {parameter}, daytime",
        "EVO_LEVEL_NIGHT": f"Level {parameter}, nighttime",
        "EVO_STONE": f"Use {value}",
        "EVO_TRADE": "Legacy trade method (optional)",
        "EVO_TRADE_ITEM": f"Legacy trade holding {value} (optional)",
        "EVO_HAS_MOVE": f"Level up knowing {value}",
        "EVO_FRIENDSHIP": "Friendship 160",
        "EVO_FRIENDSHIP_DAY": "Friendship 160, daytime",
        "EVO_FRIENDSHIP_NIGHT": "Friendship 160, nighttime",
    }
    return names.get(method, f"{human_constant(method)}: {value}")


def evolution_pdf() -> None:
    text = (ROOT / "armips/data/evodata.s").read_text(encoding="utf-8")
    forms = availability.form_map()
    reverse_forms = {(base, index): form for form, (base, index) in forms.items()}
    rows = [["From", "Requirement", "To"]]
    current = ""
    for line in text.splitlines():
        header = re.match(r"evodata\s+(SPECIES_[A-Z0-9_]+)", line)
        if header:
            current = header.group(1)
            continue
        formed = re.search(r"evolutionwithform\s+(EVO_[A-Z0-9_]+),\s*([^,]+),\s*(SPECIES_[A-Z0-9_]+),\s*(\d+)", line)
        normal = re.search(r"evolution\s+(EVO_[A-Z0-9_]+),\s*([^,]+),\s*(SPECIES_[A-Z0-9_]+)", line)
        if formed:
            method, parameter, base, index = formed.groups()
            target = reverse_forms.get((base, int(index)), f"{base} form {index}")
        elif normal:
            method, parameter, target = normal.groups()
        else:
            continue
        if method == "EVO_NONE" or target == "SPECIES_NONE":
            continue
        rows.append([human_constant(current), evolution_requirement(method, parameter.strip()), human_constant(target)])

    story = [
        Paragraph("Single-save evolution contract", H1),
        Paragraph(
            "No evolution requires a real trade, multiplayer session, temporary event or finite item. Linking Cord is the universal alternative for simple trades; item trades retain their original item and also accept Linking Cord where configured.", BODY,
        ),
        table([
            ["Special adaptation", "v2.2 method"],
            ["Karrablast / Shelmet", "Level 30"],
            ["Pawmo / Bramblin / Rellor", "Level 32"],
            ["Palafin", "Level 38; Zero to Hero activates after switching"],
            ["Gimmighoul", "Use Amulet Coin"],
            ["Kubfu", "Darkness or Waters Scroll"],
            ["Meltan", "Level 40"],
        ], [90 * mm, 115 * mm]),
        Paragraph("Complete compiled evolution table", H1),
        table(rows, [72 * mm, 92 * mm, 46 * mm]),
    ]
    build_pdf(DOCS / "Evolution Changes.pdf", "Evolution Changes", "Every compiled evolution path in HeartGold Generations v2.2", story, wide=True)


def features_pdf() -> None:
    story = [
        Paragraph("What v2.3 delivers", H1),
        table([
            ["Area", "v2.3 status"],
            ["National Dex", "1,025/1,025 species obtainable in one save"],
            ["Functional forms", "61 documented regional or item-driven forms"],
            ["Trades", "No real trade or connection required"],
            ["Automatic HMs", "All eight field HMs work without being taught; HM, badge, map and story checks remain"],
            ["Battle D-pad", "Pressing Up while RUN is focused selects FIGHT without confirming it"],
            ["Save compatibility", "Persistent layouts preserved from v2.0 through v2.2.1"],
            ["Frame rate", "60 FPS / uncapped-frame-rate hacks remain disabled for hardware stability"],
            ["Distribution", "Code, documentation and xdelta patch only; full ROM remains local"],
        ], [50 * mm, 145 * mm]),
        Paragraph("Automatic field HMs", H1),
        Paragraph(
            "Cut, Surf, Strength, Rock Smash, Whirlpool, Waterfall and Rock Climb work through their original contextual interactions. Fly is available from HM02 in the Bag through FLY / TEACH / CANCEL. Automatic use requires the matching HM, its original badge and at least one non-Egg Pokemon; the first non-Egg party member is the visual actor. HMs remain teachable for battle use.", BODY,
        ),
        Paragraph("Preserved field restrictions", H1),
        Paragraph(
            "Map, story, follower, Rocket disguise, Safari/Pal Park, Surf-state and destination checks remain in the original engine paths. Flash, Dig, Teleport, Headbutt, Sweet Scent and other non-HM field moves still need to be learned.", BODY,
        ),
        Paragraph("Preserved features and quality of life", H1),
        Paragraph(
            "Rebalanced trainers and Gym Leaders; Infinite Candy and Pocket Heal; Portable PC on L; buyable Nature Mints and Ability Capsules; type changes; free Heart Scales after seven Gyms; Master Balls after eight Gyms; hard level cap; Mega Evolution; smoother level curve; and the Kanto endgame boss rush.", BODY,
        ),
        Paragraph("v2.2 encounter policy preserved", H1),
        Paragraph(
            "Only seed stages are newly added to the wild when their later stages can be evolved in the same save. Common families are concentrated in Johto, aquatic families in water tables, and legendary, mythical, paradox and similarly high-power species in Kanto or post-game areas at 1% in every period.", BODY,
        ),
        Paragraph("Special form and ability policy", H1),
        Paragraph(
            "Regional and permanent functional forms have explicit sources. Cosmetic forms, fusions, mounts and automatic battle transformations are not separate capture targets. Terastal remains disabled; Terapagos uses its base form and Filter.", BODY,
        ),
        Paragraph("Known compatibility notes", H1),
        Paragraph(
            "This project prioritizes HGSS stability over exact replication of mechanics designed for later engines. Ball Fetch, Commander, Dancer, Mimicry and Tera Shift use the stable substitutions listed in Ability Changes. Manual save-fixture and long-session hardware testing remain recommended even after automated and build verification.", BODY,
        ),
    ]
    build_pdf(
        DOCS / "Features,QoL, and Known Bugs.pdf",
        "Features, QoL, and Known Bugs",
        "Player-facing v2.3 feature and compatibility reference",
        story,
        release="v2.3",
        release_line="v2.3 - Automatic HMs & Battle D-pad",
    )


def item_pdf() -> None:
    memory_names = [f"{name} Memory" for name in (
        "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel",
        "Fire", "Water", "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark", "Fairy",
    )]
    rows = [
        ["Items", "Repeatable source", "Purpose"],
        ["Linking Cord", "Goldenrod Dept. Store 5F; Celadon Dept. Store 3F", "Trade-evolution alternative"],
        ["Sun/Moon/Fire/Thunder/Water/Leaf/Ice/Shiny/Dusk/Dawn Stones", "Goldenrod Dept. Store 5F", "Stone evolutions"],
        ["Metal Alloy / Peat Block", "Goldenrod Dept. Store 5F", "Modern evolutions"],
        ["Nectars (all four)", "Specialty mart clerks", "Oricorio styles"],
        ["Scroll of Darkness / Waters", "Specialty mart clerk", "Kubfu evolution"],
        ["Wellspring / Hearthflame / Cornerstone Masks", "Specialty mart clerk", "Ogerpon battle forms"],
        [", ".join(memory_names), "Memory specialty clerk", "Silvally types"],
        ["Amulet Coin", "Specialty mart clerk", "Gimmighoul evolution"],
        ["Booster Energy", "Specialty mart clerk", "Protosynthesis / Quark Drive"],
        ["Chipped Pot", "Specialty mart clerk", "Antique tea evolution"],
        ["Galarica Cuff/Wreath; Black Augurite; pots; apples; armors", "Safari Zone Gate", "Regional and cross-generation evolutions"],
        ["Nature Mints / Ability Capsule", "Goldenrod & Celadon Dept. Store 2F", "Nature and ability changes"],
        ["Rare Candy / healing / Repels", "General marts by badge progression", "Grinding and travel QoL"],
    ]
    story = [
        Paragraph("Repeatability guarantee", H1),
        Paragraph(
            "Every item required to complete the National Dex or access a supported functional form can be bought repeatedly. The mart data is compiled from armips/asm/custom/mart_items.s.", BODY,
        ),
        table(rows, [67 * mm, 70 * mm, 70 * mm]),
        Paragraph("Usage note", H1),
        Paragraph(
            "Evolution items are either used directly on the Pokemon or checked while leveling, depending on the evolution row. Both Scrolls are configured as usable evolution items in v2.2.", BODY,
        ),
    ]
    build_pdf(DOCS / "New Item Locations.pdf", "New Item Locations", "Repeatable evolution and form supplies in v2.2", story, wide=True)


def availability_pdf() -> None:
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    rows = [["Target", "Method", "Location", "Time", "Chance", "Requirement / evolves from"]]
    for entry in manifest:
        target = human_constant(entry["display_name"]) if entry["display_name"].startswith("SPECIES_") else entry["display_name"]
        requirement = entry["requirement"]
        if entry["evolution_from"]:
            requirement = (requirement + "; " if requirement else "") + "from " + human_constant(entry["evolution_from"])
        rows.append([target, entry["method"], entry["location"], entry["period"], entry["chance"], requirement])
    story = [
        Paragraph("Coverage", H1),
        Paragraph(
            "This replaces the old Non-Included Pokemon document. It contains one row for every National Dex species plus every supported functional form: 1,025 species and 61 form targets.", BODY,
        ),
        table(rows, [43 * mm, 39 * mm, 65 * mm, 23 * mm, 20 * mm, 77 * mm], font=5.4),
    ]
    build_pdf(DOCS / "Pokemon Availability.pdf", "Pokemon Availability", "Complete single-save availability matrix generated from the v2.2 manifest", story, wide=True)


def wild_pdf() -> None:
    text = (ROOT / "armips/data/encounters.s").read_text(encoding="utf-8")
    _, blocks, order = availability.split_blocks(text)
    story: list = [
        Paragraph("How to read the tables", H1),
        Paragraph(
            "Grass slots always use 20/20/10/10/10/10/5/5/4/4/1/1 percent. Legendary, mythical and post-game special additions occupy 1% slots in morning, day and night. Water slot columns use 60/30/5/4/1 percent.", BODY,
        ),
        Paragraph("Locked v2.2 placements", H1),
        table([
            ["Location", "Morning", "Day", "Night"],
            ["Route 29", "Yamper 10%", "Yamper 10%", "Yamper 5%"],
            ["National Park", "Dracozolt 1%; Arctozolt 1%", "Dracovish 1%; Arctovish 1%", "Aerodactyl 1%"],
        ], [50 * mm, 72 * mm, 72 * mm, 72 * mm]),
    ]
    grass_header = ["Time"] + [f"{chance}%" for chance in availability.SLOT_CHANCES]
    water_chances = (60, 30, 5, 4, 1)
    for encounter_id in order:
        block = blocks[encounter_id]
        location = availability.location_name(block)
        rates = {
            name: int(re.search(rf"^{name}\s+(\d+)", block, re.MULTILINE).group(1))
            for name in ("walkrate", "surfrate", "rocksmashrate", "oldrodrate", "goodrodrate", "superrodrate")
        }
        if not any(rates.values()) or location == "???" or location.startswith("Safari Zone"):
            continue
        section: list = [Paragraph(f"{location}  [encounter {encounter_id}]", H1)]
        if rates["walkrate"]:
            grass_rows = [grass_header]
            for period in availability.PERIODS:
                values = [human_constant(availability.species_on_line(line)) for line in availability.grass_lines(block, period)]
                grass_rows.append([period.title()] + values)
            section.append(table(grass_rows, [15 * mm] + [20.7 * mm] * 12, font=5.4))
        water_rows = [["Method", "Table rate", "60%", "30%", "5%", "4%", "1%"]]
        for label, rate_name in (
            ("Surf", "surfrate"), ("Old Rod", "oldrodrate"),
            ("Good Rod", "goodrodrate"), ("Super Rod", "superrodrate"),
        ):
            if not rates[rate_name]:
                continue
            source_section = label.lower()
            entries = []
            for line in availability.encounter_lines(block, source_section):
                species = human_constant(availability.species_on_line(line))
                levels = re.search(r",\s*(\d+)\s*,\s*(\d+)\s*$", line)
                entries.append(f"{species} Lv.{levels.group(1)}-{levels.group(2)}")
            water_rows.append([label, rates[rate_name]] + entries)
        if len(water_rows) > 1:
            section.extend([Spacer(1, 2 * mm), table(water_rows, [25 * mm, 18 * mm] + [44 * mm] * 5, font=5.4)])
        story.append(KeepTogether(section))
    build_pdf(DOCS / "Wild Encounters.pdf", "Wild Encounters", "All compiled v2.2 grass, Surf and fishing encounter tables", story, wide=True)


def cover_pdf(title: str, note: str) -> bytes:
    buffer = BytesIO()
    canv = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    canv.setFillColor(NAVY)
    canv.rect(0, 0, width, height, fill=1, stroke=0)
    canv.setFillColor(GOLD)
    canv.rect(0, height - 35 * mm, width, 8 * mm, fill=1, stroke=0)
    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 25)
    canv.drawString(22 * mm, height - 62 * mm, title)
    canv.setFillColor(GOLD)
    canv.setFont("Helvetica-Bold", 15)
    canv.drawString(22 * mm, height - 75 * mm, "HeartGold Generations v2.2")
    text = canv.beginText(22 * mm, height - 100 * mm)
    text.setFont("Helvetica", 10)
    text.setLeading(15)
    text.setFillColor(colors.white)
    for line in note.split("\n"):
        text.textLine(line)
    canv.drawText(text)
    canv.save()
    return buffer.getvalue()


def stamp_legacy(filename: str, title: str, note: str) -> None:
    source = LEGACY / filename
    if not source.exists():
        raise FileNotFoundError(f"legacy PDF source missing: {source}")
    writer = PdfWriter()
    cover = PdfReader(BytesIO(cover_pdf(title, note)))
    writer.add_page(cover.pages[0])
    for page in PdfReader(source).pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        overlay_buffer = BytesIO()
        canv = canvas.Canvas(overlay_buffer, pagesize=(width, height))
        canv.setFillColor(NAVY)
        canv.rect(0, 0, width, 13, fill=1, stroke=0)
        canv.setFillColor(colors.white)
        canv.setFont("Helvetica-Bold", 6.5)
        canv.drawString(18, 4, "HEARTGOLD GENERATIONS v2.2 - VERIFIED REFERENCE")
        canv.save()
        overlay = PdfReader(BytesIO(overlay_buffer.getvalue())).pages[0]
        page.merge_page(overlay)
        writer.add_page(page)
    writer.add_metadata({"/Title": title, "/Author": "HeartGold Generations v2.2"})
    with (DOCS / filename).open("wb") as handle:
        writer.write(handle)


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    ability_pdf()
    evolution_pdf()
    features_pdf()
    item_pdf()
    availability_pdf()
    wild_pdf()
    stamp_legacy(
        "Pokemon Type Changes.pdf", "Pokemon Type Changes",
        "The v2.0 type-balance table remains unchanged in v2.2.\nThis edition is stamped and reviewed as the v2.2 reference.",
    )
    stamp_legacy(
        "Gym Leader Teams and Level Caps.pdf", "Gym Leader Teams and Level Caps",
        "Trainer teams and level caps are unchanged from the supplied balance document.\nThis edition is stamped and reviewed as the v2.2 reference.",
    )
    print("generated 8 HeartGold Generations v2.2 PDFs")


if __name__ == "__main__":
    main()
