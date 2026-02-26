"""Shared marker definitions for scenario parsing."""

SECTION_MARKERS = {
    "HOOK": ("[HOOK]", "[END HOOK]"),
    "CORE": ("[CORE]", "[END CORE]"),
    "LIGHT": ("[LIGHT]", "[END LIGHT]"),
}

TECHNICAL_TAGS = [
    "AI_VIDEO",
    "AI_THUMB",
    "FOLDER",
    "SHORT_START",
    "SHORT_END",
    "SHORT_TEXT",
    "SHORT_PROMPT",
]

ALLOWED_FOLDERS = {
    "SKY_COSMIC_LIGHT",
    "FOREST_NATURE_MIST",
    "WATER_OCEAN",
    "SYMBOLIC_ABSTRACT",
    "HUMAN_REFLECTION_SOLITUDE",
    "SPIRITUAL_SYMBOLS",
}
