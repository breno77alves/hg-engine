#!/usr/bin/env python3
"""Static contract for the V2.1 friendship-evolution threshold."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def evolution_block(source: str, species: str) -> str:
    start = source.index(f"evodata {species}\n")
    return source[start : source.index("terminateevodata", start)]


def main() -> None:
    config = read("include/config.h")
    assert re.search(r"#define FRIENDSHIP_EVOLUTION_THRESHOLD\s+160\b", config)
    assert not re.search(r"^#define FRIENDSHIP_EFFECTS\b", config, re.M), (
        "the requested evolution threshold must not enable unrelated affection bonuses"
    )

    engine = read("src/individual/GetMonEvolutionInternal.c")
    for method in ("EVO_FRIENDSHIP", "EVO_FRIENDSHIP_DAY", "EVO_FRIENDSHIP_NIGHT"):
        case = engine.split(f"case {method}:", 1)[1].split("break;", 1)[0]
        assert "friendship >= FRIENDSHIP_EVOLUTION_THRESHOLD" in case
    assert "friendship >= 220" not in engine

    evodata = read("armips/data/evodata.s")
    expected = {
        "SPECIES_GOLBAT": "evolution EVO_FRIENDSHIP, 0, SPECIES_CROBAT",
        "SPECIES_TOGEPI": "evolution EVO_FRIENDSHIP, 0, SPECIES_TOGETIC",
        "SPECIES_BUDEW": "evolution EVO_FRIENDSHIP_DAY, 0, SPECIES_ROSELIA",
        "SPECIES_RIOLU": "evolution EVO_FRIENDSHIP_DAY, 0, SPECIES_LUCARIO",
        "SPECIES_CHINGLING": "evolution EVO_FRIENDSHIP_NIGHT, 0, SPECIES_CHIMECHO",
        "SPECIES_SNOM": "evolution EVO_FRIENDSHIP_NIGHT, 0, SPECIES_FROSMOTH",
    }
    for species, evolution in expected.items():
        assert evolution in evolution_block(evodata, species)
    assert len(re.findall(r"^\s*evolution EVO_FRIENDSHIP(?:_DAY|_NIGHT)?\b", evodata, re.M)) == 16

    scripted_friendship_reads = []
    for path in (ROOT / "armips").rglob("*.s"):
        if path.name in {"scriptmacros.s", "constants.s"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"\b(mon_get_friendship|GetPokemonHappiness)\b", text):
            scripted_friendship_reads.append(str(path.relative_to(ROOT)))
    assert not scripted_friendship_reads, (
        "campaign scripts depend on explicit friendship reads: " + ", ".join(scripted_friendship_reads)
    )

    print("PASS: all friendship evolutions use 160 without campaign or affection coupling")


if __name__ == "__main__":
    main()
