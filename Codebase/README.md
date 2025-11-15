## Repo layout

- `Codebase/GUI/`
  - `GUI/` – Tkinter windows (task creator, DAG canvas, etc.)
  - `Logic/` – DAG building / level computation
  - `IO/` – finding `Tasks/`, loading JSON, etc.
  - `Run/` – Python entrypoints (`dag_viewer.py`, `task_create_gui.py`)
- `Codebase/Run/`
  - `create_task.sh` – open task creator GUI
  - `view_dag.sh` – open DAG viewer GUI
- `Codebase/Setup/`
  - `bind_hotkey.sh` – bind global hotkeys via `xbindkeys`
- `Codebase/Template/`
  - `task_template.json.j2` – template for new task JSONs
- `Tasks/`
  - Individual task `.json` files
- `UserData/`
  - Geometry + prefs (remember window position, intro toggle, etc.)
- `run.sh`
  - Top-level helper that asks what you want to do