# Lore-Weaver

## Game Design Module Engine

A Python + Streamlit app that walks through a **Master Design Flow** for game concepting.

### Features

- **Module Menu / Stuck Points**
  - Jump directly into:
    - Genre/Theme
    - Setting
    - Game Rules
    - Character Traits
    - Physical Traits
    - Narrative Script
- **Smart Suggest**
  - Each module has a **Suggest** button.
  - Generates 3 non-cliché ideas tuned to **Game Size**: `Micro`, `Mid-Tier`, `Open World`.
- **Selective Persistence**
  - Checkmark ideas you like and save them to local JSON (`game_design_state.json`).
- **Visual Concept Generator**
  - In **Setting** and **Character Traits**, each saved entry can generate a high-detail AI art prompt.
  - Prompts are shown in a **Copy to Clipboard** text area for easy reuse.
- **Smart Script: Live Dialogue Assistant**
  - In **Narrative Script**, write a dialogue seed and click **Finish the Thought**.
  - The app generates 3 dialogue variations influenced by selected character traits.
  - **Approve** appends a line into a session-based **Approved Dialogue** list using `st.session_state`, so the script can be built line-by-line.
  - **Reject** regenerates options.
- **Multi-Output Export**
  - **Paragraph Form** → Markdown pitch (`exports/game_pitch.md`)
  - **IDE Style** → structured design tree in markdown (`exports/ide_export.md`)
  - **Unity Engine** → `GameDesignData.cs` ScriptableObject (`exports/GameDesignData.cs`)

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install streamlit
streamlit run game_design_module_engine.py
```
