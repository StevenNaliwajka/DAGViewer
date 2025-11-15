# DAGViewer

A small tool to **plan tasks as a DAG** (Directed Acyclic Graph).

---

## How to run (simple flow)

- Create venv + install deps (once)
  - `./setup.sh`
- Use the main launcher:
  - `./run.sh`
    - Option to:
      - Bind **global hotkeys** (recommended)
      - Open **Create Task** window
      - Open **DAG Viewer**
- Or run scripts directly:
  - `Codebase/Run/create_task.sh`
  - `Codebase/Run/view_dag.sh`


---

## What it does

- Stores tasks as simple **JSON files** in `Tasks/`
- Uses a **Jinja2 template** (`Codebase/Template/task_template.json.j2`) for new tasks
- Shows tasks as **nodes in a graph**
- Lets you **drag & drop** nodes to rearrange layout
- Lets you **visually connect tasks** with edges (right-click & drag)
- Persists **positions and edges** between sessions
- Colors nodes by **group**, with a legend to **toggle groups on/off**



---

## Future Plans

- Re-write in more performant oriented language.
- Improved Plotting order
- Live Refresh
- Further Improve GUI Graphics
- Add a done/Not color. Darker = Ongoing. Light = done.
