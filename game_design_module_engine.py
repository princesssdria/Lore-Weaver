import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import streamlit as st

STATE_PATH = Path("game_design_state.json")
EXPORT_DIR = Path("exports")

MODULES = [
    "Genre/Theme",
    "Setting",
    "Game Rules",
    "Character Traits",
    "Narrative Script",
]

GAME_SIZES = ["Micro", "Mid-Tier", "Open World"]

SUGGESTION_LIBRARY: Dict[str, Dict[str, List[str]]] = {
    "Genre/Theme": {
        "Micro": [
            "Pocket tragedy roguelite where each run is a three-minute memory loop",
            "Single-screen social deduction puzzler played through voicemail snippets",
            "Minimalist rhythm tactics game set inside a malfunctioning lullaby machine",
        ],
        "Mid-Tier": [
            "Investigative action-RPG about urban folklore auditors who weaponize rumors",
            "Asymmetric co-op survival game where one player is the weather system",
            "Deckbuilding stealth game set in a living museum that rearranges eras nightly",
        ],
        "Open World": [
            "Post-borderland diplomacy sandbox where factions are languages, not nations",
            "Bio-architectural fantasy where terrain grows from player-made legal treaties",
            "Interplanetary migration sim mixing colony management with oral-history quests",
        ],
    },
    "Setting": {
        "Micro": [
            "An elevator stuck between two floors that changes decade every minute",
            "A tiny floating market drifting through cloud canyons at dawn",
            "A sealed train cabin crossing a storm where outside laws keep mutating",
        ],
        "Mid-Tier": [
            "A coastal city powered by archived dreams sold as public utilities",
            "An abandoned orbital station reclaimed by competing theater troupes",
            "A mountain megastructure where every district follows a different calendar",
        ],
        "Open World": [
            "A fractured continent linked by migratory forests that move each season",
            "A planet-sized archive where biomes are organized by forgotten emotions",
            "A tidal super-region whose coastlines are redrawn by moon-forge politics",
        ],
    },
    "Game Rules": {
        "Micro": [
            "One-hit permadeath, but every death permanently reveals one hidden map tile",
            "You can only perform one verb per turn, and the verb rotates globally",
            "Timer never stops: pausing rewinds your resources instead",
        ],
        "Mid-Tier": [
            "Trust economy: allies gain abilities only if your last three choices stayed consistent",
            "Combat outcomes alter local grammar, changing how quests can be interpreted",
            "Crafting uses entropy budget: stronger items destabilize nearby systems",
        ],
        "Open World": [
            "Dynamic ecosystem-based trade where species migration changes market value and quests",
            "Law simulation engine: regions generate procedural laws that NPCs enforce and exploit",
            "World memory system where major events rewrite fast-travel routes and faction doctrine",
        ],
    },
    "Character Traits": {
        "Micro": [
            "Protagonist remembers futures but forgets names",
            "Companion speaks only in map coordinates tied to emotions",
            "Hero can borrow one trait from any defeated rival for a single scene",
        ],
        "Mid-Tier": [
            "Diplomat-engineer with synesthesia that visualizes lies as architectural stress",
            "Ex-smuggler archivist whose confidence stat rises when hoarding contradictions",
            "Medic who can split a personality into temporary tactical specialists",
        ],
        "Open World": [
            "Faction leaders age at different speeds based on player policy decisions",
            "Playable cast carries hereditary vows that unlock or block whole questlines",
            "Nemesis characters evolve their ethics by observing your settlement design",
        ],
    },
    "Narrative Script": {
        "Micro": [
            "Three-scene loop: promise, fracture, reinterpretation",
            "Story delivered through receipts that reveal a missing person timeline",
            "Dialogue choices are replaced by choosing what memory to delete",
        ],
        "Mid-Tier": [
            "Five-act conspiracy where each act is narrated by a different unreliable witness",
            "Branching court drama resolved by reconstructing public myths in real time",
            "Main plot progresses only when side characters finish their personal arcs",
        ],
        "Open World": [
            "Layered epic with regional sagas feeding into a mutable world constitution",
            "Narrative mesh where player-founded institutions become future quest-givers",
            "Long-form political myth where endings are voted by simulated populations",
        ],
    },
}


@dataclass
class EngineState:
    game_size: str
    selected: Dict[str, List[str]]

    @classmethod
    def load(cls) -> "EngineState":
        if STATE_PATH.exists():
            data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            return cls(
                game_size=data.get("game_size", GAME_SIZES[0]),
                selected={m: data.get("selected", {}).get(m, []) for m in MODULES},
            )
        return cls(game_size=GAME_SIZES[0], selected={m: [] for m in MODULES})

    def save(self) -> None:
        payload = {"game_size": self.game_size, "selected": self.selected}
        STATE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def get_suggestions(module: str, game_size: str) -> List[str]:
    return SUGGESTION_LIBRARY[module][game_size]


def build_art_prompt(entry: str, module: str, game_size: str) -> str:
    style = "2D pixel-art" if game_size == "Micro" else "stylized concept art" if game_size == "Mid-Tier" else "cinematic worldbuilding illustration"
    focus = "character design sheet" if module == "Character Traits" else "environment matte painting"
    mood = "high contrast lighting, rich atmospheric depth, crisp silhouette, storytelling composition"
    return (
        f"{style}, {focus}, {entry}, dramatic perspective, layered foreground and background, "
        f"materials and textures clearly defined, {mood}, production-ready game art prompt"
    )


def infer_tones(traits: List[str]) -> List[str]:
    text = " ".join(traits).lower()
    mapping = {
        "sarcastic": ["sarcastic", "dry humor", "wry"],
        "brave": ["brave", "fearless", "valiant"],
        "distrustful": ["distrust", "skeptic", "paranoid"],
    }
    tones = []
    for tone, keywords in mapping.items():
        if any(k in text for k in keywords):
            tones.append(tone)
    return tones or ["grounded", "intense", "guarded"]


def can_finish_thought(seed: str) -> bool:
    return bool(re.search(r'["“]$|\.\.\.$|:$', seed.strip()))


def build_dialogue_variations(seed: str, traits: List[str]) -> List[str]:
    tones = infer_tones(traits)
    base = seed.strip()
    if not base.endswith((" ", '"', "“")):
        base = f"{base} "

    pools = {
        "sarcastic": [
            '"Perfect. Another mystery map with no legend—my favorite kind of optimism."',
            '"If this route gets us killed, at least the cartography is stylish."',
            '"Great, the path marked \"safe\" is on fire. Very reassuring."',
        ],
        "brave": [
            '"Then we move before dawn—if danger wants us, it can chase us."',
            '"We follow the ridge together. No one gets left behind."',
            '"Mark the shortest path. I will open the way."',
        ],
        "distrustful": [
            '"No. Someone altered these markings after the last patrol."',
            '"Keep your voices down; this map is bait, not guidance."',
            '"We verify every checkpoint ourselves—trust nothing inked here."',
        ],
        "grounded": [
            '"If this is accurate, we have one clean chance to cross."',
            '"We plan for the worst route and earn the better one."',
            '"Circle the hazards first; then we decide who moves where."',
        ],
        "intense": [
            '"Every minute we hesitate, the window closes—choose now."',
            '"We commit fully or we turn back; there is no middle path."',
            '"This is the line. Cross it ready, or don\'t cross at all."',
        ],
        "guarded": [
            '"We proceed, but only after we test who benefits from this route."',
            '"Assume we are expected. Move like we are already watched."',
            '"No shortcuts. Careful steps keep us alive longer than bold guesses."',
        ],
    }

    first_three = tones[:3]
    lines = [f"{base}{pools[tone][0]}" for tone in first_three]
    while len(lines) < 3:
        lines.append(f"{base}{pools['grounded'][len(lines)]}")
    return lines[:3]


def render_pitch(state: EngineState) -> str:
    parts = [f"# Game Pitch\n\n**Game Size:** {state.game_size}\n"]
    for module in MODULES:
        choices = state.selected.get(module, [])
        if choices:
            parts.append(f"## {module}\n")
            for item in choices:
                parts.append(f"- {item}\n")
    parts.append(
        "\nThis concept fuses your selected pillars into a coherent production-ready direction, balancing scope, mechanics, and narrative identity."
    )
    return "\n".join(parts)


def render_ide_tree(state: EngineState) -> str:
    lines = [
        "game-design/",
        "├── 01_genre_theme.md",
        "├── 02_setting.md",
        "├── 03_game_rules.md",
        "├── 04_character_traits.md",
        "└── 05_narrative_script.md",
        "",
    ]
    for index, module in enumerate(MODULES, start=1):
        filename = f"{index:02d}_{module.lower().replace('/', '').replace(' ', '_')}.md"
        lines.append(f"# {filename}")
        lines.append(f"## {module}")
        for entry in state.selected.get(module, []):
            lines.append(f"- {entry}")
        lines.append("")
    return "\n".join(lines)


def render_unity_script(state: EngineState) -> str:
    def to_field(module: str) -> str:
        cleaned = module.replace("/", " ").replace("-", " ").lower().split()
        return "".join([cleaned[0]] + [w.capitalize() for w in cleaned[1:]])

    lines = [
        "using System.Collections.Generic;",
        "using UnityEngine;",
        "",
        "[CreateAssetMenu(fileName = \"GameDesignData\", menuName = \"Game Design/Data\")]",
        "public class GameDesignData : ScriptableObject",
        "{",
        f'    [SerializeField] private string gameSize = "{state.game_size}";',
    ]
    for module in MODULES:
        field = to_field(module)
        lines.append(
            f"    [SerializeField] private List<string> {field} = new List<string> {{"
        )
        for entry in state.selected.get(module, []):
            safe = entry.replace('"', '\\"')
            lines.append(f'        "{safe}",')
        lines.append("    };")
    lines.append("}")
    return "\n".join(lines)


def export_outputs(state: EngineState, style: str) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    if style == "Paragraph Form":
        path = EXPORT_DIR / "game_pitch.md"
        path.write_text(render_pitch(state), encoding="utf-8")
        return path
    if style == "IDE Style":
        path = EXPORT_DIR / "ide_export.md"
        path.write_text(render_ide_tree(state), encoding="utf-8")
        return path

    path = EXPORT_DIR / "GameDesignData.cs"
    path.write_text(render_unity_script(state), encoding="utf-8")
    return path


def init_session_state(state: EngineState) -> None:
    if "approved_dialogue" not in st.session_state:
        st.session_state["approved_dialogue"] = list(state.selected.get("Narrative Script", []))


def main() -> None:
    st.set_page_config(page_title="Game Design Module Engine", layout="wide")
    st.title("Game Design Module Engine")
    st.caption("Master Design Flow: jump into stuck points, suggest ideas, checkmark what works, and export.")

    state = EngineState.load()
    init_session_state(state)

    selected_size = st.selectbox("Game Size", GAME_SIZES, index=GAME_SIZES.index(state.game_size))
    if selected_size != state.game_size:
        state.game_size = selected_size
        state.save()

    module_choice = st.radio("Module Menu (Stuck Points)", MODULES, horizontal=True)
    suggestion_key = f"suggestions::{module_choice}::{state.game_size}"

    st.subheader(module_choice)
    if st.button(f"Suggest for {module_choice}"):
        st.session_state[suggestion_key] = get_suggestions(module_choice, state.game_size)

    suggestions = st.session_state.get(suggestion_key, get_suggestions(module_choice, state.game_size))

    custom_entry = st.text_input(f"Add your own {module_choice} entry")
    if st.button(f"Add Custom {module_choice} Entry") and custom_entry.strip():
        current = state.selected.get(module_choice, [])
        merged = list(dict.fromkeys(current + [custom_entry.strip()]))
        state.selected[module_choice] = merged
        state.save()
        st.success("Custom entry saved.")

    checked_values: List[str] = []
    for idx, suggestion in enumerate(suggestions):
        key = f"{module_choice}_{idx}_{state.game_size}"
        default = suggestion in state.selected.get(module_choice, [])
        if st.checkbox(suggestion, key=key, value=default):
            checked_values.append(suggestion)

    if st.button("Save Checkmarked Selections"):
        existing_custom = [
            item
            for item in state.selected.get(module_choice, [])
            if item not in get_suggestions(module_choice, state.game_size)
        ]
        state.selected[module_choice] = existing_custom + checked_values
        state.save()
        st.success(f"Saved {len(checked_values)} selections to {STATE_PATH}.")

    if module_choice in {"Character Traits", "Setting"}:
        st.markdown("### Visual Concept Generator")
        entries = state.selected.get(module_choice, [])
        if not entries:
            st.info("Save at least one entry in this module to generate art prompts.")
        for i, entry in enumerate(entries):
            if st.button(f"Generate Art Prompt #{i + 1}", key=f"art_btn_{module_choice}_{i}"):
                st.session_state[f"art_prompt_{module_choice}_{i}"] = build_art_prompt(entry, module_choice, state.game_size)

            prompt = st.session_state.get(f"art_prompt_{module_choice}_{i}")
            if prompt:
                st.text_area(
                    f"Copy to Clipboard Prompt #{i + 1}",
                    value=prompt,
                    height=120,
                    key=f"art_prompt_box_{module_choice}_{i}",
                    help="Use Ctrl/Cmd + C to copy.",
                )

    if module_choice == "Narrative Script":
        st.markdown("### Smart Script: Live Dialogue Assistant")
        seed = st.text_area(
            "Enter a line ending in a quote / trailing pause (\" ... or :)",
            key="dialogue_seed",
            placeholder='John looked at the map and said...'
        )

        if st.button("Finish the Thought"):
            if not can_finish_thought(seed):
                st.warning("Please end your seed with a quote, ellipsis (...), or colon (:).")
            else:
                trait_context = state.selected.get("Character Traits", [])
                st.session_state["dialogue_variations"] = build_dialogue_variations(seed, trait_context)

        variations = st.session_state.get("dialogue_variations", [])
        for idx, line in enumerate(variations):
            st.write(f"**Variation {idx + 1}:** {line}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Approve", key=f"approve_{idx}"):
                    approved_dialogue = st.session_state.get("approved_dialogue", [])
                    approved_dialogue.append(line)
                    st.session_state["approved_dialogue"] = approved_dialogue
                    updated_script = list(dict.fromkeys(state.selected.get("Narrative Script", []) + approved_dialogue))
                    state.selected["Narrative Script"] = updated_script
                    state.save()
                    st.success("Line approved and added to your running script.")
            with c2:
                if st.button("Reject", key=f"reject_{idx}"):
                    trait_context = state.selected.get("Character Traits", [])
                    st.session_state["dialogue_variations"] = build_dialogue_variations(seed + " ", trait_context)
                    st.info("Regenerated dialogue variations.")

        st.markdown("#### Approved Dialogue (Session Script Builder)")
        approved_lines = st.session_state.get("approved_dialogue", [])
        if approved_lines:
            script_text = "\n".join(f"- {line}" for line in approved_lines)
            st.text_area(
                "Build your script line-by-line",
                value=script_text,
                height=220,
                disabled=True,
            )
            if st.button("Clear Approved Dialogue"):
                st.session_state["approved_dialogue"] = []
                st.success("Cleared approved dialogue for this session.")
        else:
            st.info("Approve dialogue lines to build your script here.")

    st.divider()
    st.subheader("Export")
    style = st.selectbox("Output Style", ["Paragraph Form", "IDE Style", "Unity Engine"])
    if st.button("Export Design"):
        export_path = export_outputs(state, style)
        st.success(f"Exported to {export_path}")


if __name__ == "__main__":
    main()
