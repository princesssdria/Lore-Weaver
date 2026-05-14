import json
import re
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import streamlit as st

# --- CONSTANTS & PATHS ---
STATE_PATH = Path("game_design_state.json")
MODULES = ["Genre/Theme", "Setting", "Game Rules", "Character Traits", "Physical Traits", "Narrative Script"]
GAME_SIZES = ["Micro", "Mid-Tier", "Open World"]

# --- THE FULL 120-ITEM SUGGESTION LIBRARY (RESTORED) ---
SUGGESTION_LIBRARY = {
    "Genre/Theme": {
        "Micro": ["Pocket tragedy roguelite", "Voicemail social deduction", "Lullaby rhythm tactics",
                  "Input-flip puzzle", "Typing combat", "Sound-pattern stealth", "Heartbeat rhythm", "One-weapon arena",
                  "Logic-chain programming", "Emoji text-adventure", "Glass-stacking physics", "Clockwork bullet hell",
                  "Brightness horror", "Ant-hill sim", "1-bit crawler", "Gravity-flip platformer",
                  "Digital tarot builder", "Bullet-avoiding shooter", "Cosmic speed-dating", "16x16 moss garden"],
        "Mid-Tier": ["Urban folklore auditors", "Weather-system survival", "Museum deckbuilder", "Moral-skill RPG",
                     "Relationship-mechanic sim", "Shifting physics beat-em-up", "Song-path adventure",
                     "Emotional stealth RPG", "Dancing combat rhythm", "Steampunk airship racer",
                     "Scent-memory detective", "Sentient fabric RPG", "Nightmare hunting horror",
                     "Whale-back city builder", "Alchemy reaction sim", "Gothic body-part Metroidvania",
                     "3D node hacker", "Ghost-disappearance mystery", "Revolution grand strategy",
                     "Cooking gladiator combat"],
        "Open World": ["Language diplomacy sandbox", "Bio-architectural fantasy", "Interplanetary migration sim",
                       "Musical genre RPG", "AI society simulation", "Robot societal builder",
                       "Terrain-reshape hack-and-slash", "NPC memory simulation", "Language physics exploration",
                       "Sea monster city-builder", "Oxygen currency survival", "Coding magic frontier",
                       "Terraforming merchant sim", "Sand-dune tech exploration", "Cyber-feudal Japan",
                       "Multi-realm ripple RPG", "Machine automation sandbox", "Solar-punk green tech",
                       "God-ribcage exploration", "Sky-island wind sandbox"]
    },
    "Setting": {
        "Micro": ["Stuck elevator", "Cloud market", "Train cabin", "Repeating trench", "Victorian office",
                  "Time-storm ship", "VR training glitched", "Mafia safehouse", "Space capsule", "Asteroid lighthouse",
                  "Clockwork heart", "Atomic lab", "Hurricane greenhouse", "Mood shelter", "Sinking skyscraper",
                  "Vending portal", "Blizzard tent", "Memory attic", "Universe campfire", "Digital cell"],
        "Mid-Tier": ["Dream-utility city", "Theater station", "Calendar mountain", "Leviathan metropolis",
                     "Glass forest", "Library archipelago", "Underground volcanic neo-Tokyo", "Memory oasis",
                     "Bioluminescent gothic", "Sky-dock needle", "Dragonfly swamp", "Lunar art colony",
                     "Arctic ghost base", "Echo valley", "Moon labyrinth", "Toy factory town", "Data canals",
                     "Gas giant school", "Intergalactic village", "Uphill lava island"],
        "Open World": ["Migratory forest", "Emotion archive", "Tidal super-region", "Dyson patchwork",
                       "Starlight nebula", "Silicon desert", "Hollow earth", "Crystal canyons", "Sky-ground void",
                       "Neon smog sprawl", "Sentient jungle", "Era-volcano chain", "Gear landscape",
                       "Bioluminescent web", "Lily-pad ocean", "Heat-currency winter", "Solar seed paradise",
                       "10-minute-behind wasteland", "Turtle-back kingdom", "Post-human tribes"]
    },
    "Game Rules": {
        "Micro": ["Tile-death reveal", "One verb turn", "Decision time", "Health is currency", "Hostile shadow AI",
                  "Wind movement", "Timer resources", "Death resets mechanics", "Minute removal", "RPS combat",
                  "Single-hit KO", "Limited oxygen", "Inventory weight speed", "Light-based safety",
                  "Sound attracts monsters", "Recycling parts", "No-jump restriction", "Color-coded damage",
                  "Magnetic attraction", "Shadow-only walking"],
        "Mid-Tier": ["Trust economy", "Grammar combat", "Entropy crafting", "Weather ecosystem", "Sanity rendering",
                     "Limb injury", "Memory crafting", "Terraforming walls", "Heart-rate stealth",
                     "Reputation visibility", "Seasonal migration", "Dynamic inflation", "Political favor",
                     "Skill-tree rot", "Blueprint hunting", "Biological energy", "Heat-signature tracking",
                     "Day/Night stats", "Weapon degradation", "NPC debt system"],
        "Open World": ["Ecosystem trade", "AI legal system", "Territory wars", "World decay", "Language physics",
                       "Hereditary aging", "Pollution meter", "Destructible world", "Tech eras", "Settlement scaling",
                       "Continental drift", "Cultural diffusion", "Satellite networking", "Deep-sea pressure",
                       "Global warming sim", "Interstellar logistics", "Species evolution", "Resource exhaustion",
                       "Atmospheric oxygen", "Tectonic movement"]
    },
    "Character Traits": {
        "Micro": ["Forgets names", "Luck focus", "Bee swarm", "Glass body", "Luck health", "Emotive coordinates",
                  "Meditation healing", "Shadow-strength", "Techno-glitches", "Thermal vision", "Heavy breather",
                  "Mute observer", "Fidgety hands", "Constant humming", "Night owl", "Sharp tongue", "Clumsy gait",
                  "Silver spoon", "Iron stomach", "Paper skin"],
        "Mid-Tier": ["Synesthesia diplomat", "Smuggler archivist", "Personality split", "AI virus hacker",
                     "Fading traveler", "Vibration monk", "Object reader", "Environment bard", "Berserker monk",
                     "Vow-breaker", "Telepathic static", "Gravity dancer", "Dream walker", "Soul merchant",
                     "Clockwork lungs", "Venomous blood", "Electric touch", "Magnetic pulse", "Weightless spirit",
                     "Echo singer"],
        "Open World": ["Policy aging", "Hereditary vows", "Ethics nemesis", "Social battery", "Fear biomes",
                       "Alignment dialogue", "Dream quests", "Bulk inventory", "Addiction stats", "Trait inheritance",
                       "Historical legend", "Faction pariah", "Prophecy carrier", "World-soul linker", "Memory thief",
                       "Time-dilated aging", "Ethereal anchor", "Chaos catalyst", "Law bringer", "Nature's herald"]
    },
    "Physical Traits": {
        "Micro": ["Glowing eye", "Stress-cracks", "Rotating limb", "Static halo", "Neon trails", "TV head",
                  "Liquid body", "Multiple arms", "Living pack", "Mirror skin", "Steam vents", "Crystalline hair",
                  "Floating gears", "Paper wings", "Third eye", "Animal ears", "Scaled neck", "Burn scars",
                  "Vibrating skin", "Ink-stained fingers"],
        "Mid-Tier": ["Spine display", "Choice face", "Crystal heart", "Bio tattoos", "Bark-skin", "Scent trail",
                     "Energy crystals", "Webbed limbs", "Grown armor", "Voice mimic", "Luminescent veins",
                     "Metallic sheen", "Wings of light", "Extra-sensory horns", "Branching antlers", "Coral growth",
                     "Shadow cloak", "Gemstone teeth", "Telescopic eyes", "Prehensile tail"],
        "Open World": ["Region evolution", "Narrative scars", "Ecosystem mutation", "Timeline transformation",
                       "Visible aging", "Cybernetic mods", "Journey tattoos", "Zone mutations",
                       "Ascension transparency", "World-scale size", "Galactic eyes", "Molten core", "Nebula aura",
                       "Void stomach", "Rooted feet", "Atmospheric lungs", "Shifting mass", "Dimensional bleed",
                       "Singularity navel", "Stellar crown"]
    },
    "Narrative Script": {
        "Micro": ["Three-scene loop", "Memory deletion", "Weapon perspective", "Poem script", "Explorer logs",
                  "Stop-playing AI", "Dream-wake", "Backward plot", "Receipt story", "Jar-label story", "Radio silence",
                  "Binary dialogue", "Coded letters", "Final wishes", "Found photos", "Lost keys", "Graffiti warnings",
                  "Mirror talk", "Echoed screams", "Silent goodbye"],
        "Mid-Tier": ["Witness conspiracy", "Myth court", "Character arcs", "Found-footage city", "Recursive loop",
                     "Toaster uprising", "Race vs Time", "Gray-area conflict", "Designer gods", "NPC daily-life",
                     "Political thriller", "Family feud", "Missing heir", "Religious schism", "Forbidden love",
                     "Stolen legacy", "Hidden truth", "Revenge path", "Ascension trial", "Downfall arc"],
        "Open World": ["Regional saga", "Quest-mesh", "Voted myth", "Written history", "Magic philosophy",
                       "Corporate-god revolution", "Repeating loop", "Pandemic search", "Lore-character",
                       "Galaxy migration", "Era collapse", "New world dawn", "Ancient awakening", "Forgotten war",
                       "Global treaty", "Space race", "Underground rebellion", "Sky kingdom fall", "Distant signal",
                       "Last stand"]
    }
}


# --- PERSISTENCE ---
@dataclass
class EngineState:
    game_size: str
    selected: Dict[str, List[str]]

    @classmethod
    def load(cls):
        if STATE_PATH.exists():
            data = json.loads(STATE_PATH.read_text())
            return cls(game_size=data.get("game_size", "Micro"),
                       selected=data.get("selected", {m: [] for m in MODULES}))
        return cls(game_size="Micro", selected={m: [] for m in MODULES})

    def save(self):
        STATE_PATH.write_text(json.dumps({"game_size": self.game_size, "selected": self.selected}))


# --- RENDERERS ---
def build_art_prompt(entry, module, game_size):
    style = "2D pixel-art" if game_size == "Micro" else "cinematic concept art"
    return f"{style}, {entry}, dramatic lighting, high detail, masterpiece."


def generate_unity_script(state):
    class_name = "GameCodexData"
    fields = ""
    for module in MODULES:
        clean_name = module.replace("/", "").replace(" ", "")
        items = state.selected.get(module, [])
        list_str = ", ".join([f'"{i}"' for i in items])
        fields += f"    public string[] {clean_name} = {{ {list_str} }};\n"

    return f"""using UnityEngine;

public class {class_name} : MonoBehaviour
{{
    public string gameSize = "{state.game_size}";

{fields}
    void Start()
    {{
        Debug.Log("Lore Weaver Codex Loaded: " + gameSize);
    }}
}}"""


def render_pitch(state):
    return "\n".join(
        [f"## {m}\n" + "\n".join([f"- {i}" for i in state.selected[m]]) for m in MODULES if state.selected[m]])


def render_aesthetic_scroll(state):
    st.markdown(f"""
    <div style="background-color: #fdf5e6; border: 15px double #8b5a2b; padding: 40px; font-family: 'serif'; text-align: center; color: #2a1a0f;">
        <h1 style="color: #4a3423;">The Great Prophecy</h1>
        <p><i>Scope: {state.game_size}</i></p><hr>
        {"".join([f"<h3>{m}</h3><p>{', '.join(state.selected[m])}</p>" for m in MODULES if state.selected[m]])}
    </div>
    """, unsafe_allow_html=True)


# --- MAIN APP ---
def main():
    st.set_page_config(page_title="Lore Weaver", layout="wide")
    state = EngineState.load()

    st.markdown("""
        <style>
        /* 1. External Asset Imports */
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap');

        /* 2. Background Layering */
        .stApp { 
            background-image: url("https://www.transparenttextures.com/patterns/stardust.png"), 
                              url("https://storage.needpix.com/rsynced_images/old-parchment.jpg"); 
            background-size: auto, cover; 
            background-attachment: fixed; 
            color: #3e2f24; 
        }

        /* 3. Global Text & Headers */
        h1 { 
            color: #1f120c !important; 
            text-align: center; 
            font-size: 5rem !important; 
            font-family: 'Cinzel', serif !important; 
        }

        /* Ensuring the Cinzel font carries to the rest of the UI */
        .stMarkdown, p, label, .stSelectbox {
            font-family: 'Cinzel', serif !important;
            color: #3e2f24 !important;
        }

        /* 4. Depth Styling for Interactive Elements */
        [data-testid="stCheckbox"] { 
            background: rgba(255,255,255,0.15); 
            border-radius: 8px; 
            padding: 6px; 
            margin: 6px 0; 
            box-shadow: 2px 2px 6px rgba(0,0,0,0.06); 
        }

        .stTextInput input, .stTextArea textarea { 
            background-color: rgba(255,255,255,0.4) !important; 
            border: 1px solid #c8a96b !important; 
            backdrop-filter: blur(2px); 
            border-radius: 10px; 
        }

        div.stButton > button { 
            background-color: #2a1a0f !important; 
            color: white !important; 
            border: 1px solid #d4af37 !important; 
            border-radius: 12px !important; 
            font-weight: bold !important; 
            transition: 0.3s; 
        }

        div.stButton > button:hover { 
            border-color: #ffd700 !important; 
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.7); 
            transform: translateY(-1px); 
        }

        div.stButton > button p { color: white !important; }
        </style>
        """, unsafe_allow_html=True)

    st.title("Lore Weaver")

    # 1. SCALE
    new_size = st.selectbox("Current Game Scale", GAME_SIZES, index=GAME_SIZES.index(state.game_size))
    if new_size != state.game_size:
        state.game_size = new_size
        state.save()
        st.rerun()

    module_choice = st.radio("Select Design Pillar", MODULES, horizontal=True)
    st.divider()

    # 2. SUGGESTION POOL (Logic for rolling 3 randoms from 20)
    suggest_key = f"pool_{module_choice}_{state.game_size}"
    if suggest_key not in st.session_state:
        st.session_state[suggest_key] = random.sample(SUGGESTION_LIBRARY[module_choice][state.game_size], 3)

    c1, c2 = st.columns([4, 1])
    with c1:
        st.subheader(f"Weaving: {module_choice}")
    with c2:
        if st.button("✨ Roll New Ideas"):
            st.session_state[suggest_key] = random.sample(SUGGESTION_LIBRARY[module_choice][state.game_size], 3)
            st.rerun()

    # 3. DISPLAY & SELECTION
    current_suggestions = st.session_state[suggest_key]
    saved_items = state.selected.get(module_choice, [])
    display_list = list(dict.fromkeys(saved_items + current_suggestions))

    checked_values = []
    for idx, item in enumerate(display_list):
        is_checked = item in saved_items
        label = f"✨ {item}" if item in current_suggestions and not is_checked else item
        if st.checkbox(label, key=f"chk_{module_choice}_{idx}", value=is_checked):
            checked_values.append(item)

    if st.button("💾 Etch Selections into Codex"):
        state.selected[module_choice] = checked_values
        state.save()
        st.success("Codex updated.")

    # 4. CUSTOM ENTRY
    custom = st.text_input(f"Add your own {module_choice} thought")
    if st.button("Add Custom Entry") and custom:
        state.selected[module_choice].append(custom)
        state.save()
        st.rerun()

    # 5. VISUAL CONCEPT GENERATOR
    if module_choice in {"Character Traits", "Setting", "Physical Traits"}:
        st.markdown("---")
        st.markdown("### 🎨 Visual Concept Generator")
        for i, entry in enumerate(state.selected.get(module_choice, [])):
            if st.button(f"Generate Art Prompt: {entry[:25]}...", key=f"art_{i}"):
                st.info(build_art_prompt(entry, module_choice, state.game_size))

    # 6. IMPROVED NARRATIVE LORE-LINKER
    if module_choice == "Narrative Script":
        st.markdown("---")
        st.markdown("### 📜 Natural Lore-Linker")


    # Mapping Traits to Categories
        CATEGORIES = {
            "Burden": ["Visible aging", "Burn scars", "Paper skin", "Stress-cracks", "Glass body"],
            "Machine": ["Clockwork lungs", "AI virus hacker", "Techno-glitches", "Steam vents", "Rotating limb"],
            "Ethereal": ["Dimensional bleed", "Static halo", "Ethereal anchor", "Void stomach", "Nebula aura"]
        }

    # Sensory Dictionary for Fillers
        FILLERS = {
            "Burden": {"desc": "the heavy weight of history", "dialogue": "this price I paid"},
            "Machine": {"desc": "a rhythmic, metallic grinding", "dialogue": "a glitch in the system"},
            "Ethereal": {"desc": "a cold, shimmering distortion", "dialogue": "the thinning of the veil"}
        }
        refs = state.selected.get("Character Traits", []) + state.selected.get("Physical Traits", [])



        col_a, col_b = st.columns(2)
        with col_a:
            mood = st.select_slider("Intensity", ["Subtle", "Standard", "Dramatic"])
            trait_ref = st.selectbox("Focus Trait:", refs) if refs else st.info("Add traits first.")
        with col_b:
            seed = st.text_area("Write your scene (Use '...' or '\"...\"' as triggers)",
                                placeholder="Character looks in the mirror. She says, \"...\"")

            if st.button("Weave Narrative") and seed:
                    # 1. Determine Category
                    cat = "Burden"  # Default
                    for category, trait_list in CATEGORIES.items():
                        if trait_ref in trait_list:
                            cat = category

                    # 2. Logic for Replacement
                    # Replace Dialogue Signpost "..."
                    processed = seed.replace('\"...\"', f'\"{FILLERS[cat]["dialogue"]}\"')
                    # Replace Narrative Signpost ...
                    processed = processed.replace('...', f'{FILLERS[cat]["desc"]}')

                    st.session_state["narrative_options"] = [processed]



        if "narrative_options" in st.session_state:
            for opt in st.session_state["narrative_options"]:
                st.write(f"> {opt}")
                if st.button("Save this line", key=opt):
                    state.selected["Narrative Script"].append(opt)
                    state.save()

    # 7. EXPORT (RESTORED UNITY + SCROLL)
    st.divider()
    ex_style = st.selectbox("Export Format", ["Plain Text", "Aesthetic Scroll", "Unity C# Script"])
    if st.button("Generate Final Codex"):
        if ex_style == "Plain Text":
            st.text_area("Final Output", render_pitch(state), height=300)
        elif ex_style == "Unity C# Script":
            st.code(generate_unity_script(state), language="csharp")
        else:
            render_aesthetic_scroll(state)


if __name__ == "__main__":
    main()