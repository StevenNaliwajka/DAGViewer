import json
from pathlib import Path
from tkinter import messagebox

from Codebase.GUI.GUI.JsonUpdate.create_edge_line import create_edge_line


def connect_nodes(self, parent_key: str, child_key: str) -> None:
    """
    Connect parent -> child in-memory and on disk.

    - Adds the parent's ID/key to the child's ``depends_on`` list in its JSON file.
    - Updates the in-memory TaskNode objects.
    - Draws a new edge on the canvas.
    """
    parent = self.nodes.get(parent_key)
    child = self.nodes.get(child_key)
    if parent is None or child is None:
        return

    # Avoid duplicates when we know deps_resolved is present.
    existing_deps = getattr(child, "deps_resolved", None)
    if isinstance(existing_deps, list) and parent_key in existing_deps:
        messagebox.showinfo(
            "Already connected",
            f"'{child.label}' already depends on '{parent.label}'.",
        )
        return

    # Confirm with the user.
    if not messagebox.askyesno(
            "Connect tasks",
            f"Make '{child.label}' depend on '{parent.label}'?",
    ):
        return

    # Determine dependency string to write into JSON.
    # Preferred: group + id (e.g. "EEEE1"), fallback: key.
    parent_group = getattr(parent, "group", None)
    parent_id = getattr(parent, "id", None)
    if parent_group is not None and parent_id is not None:
        dep_str = f"{parent_group}{parent_id}"
    else:
        dep_str = parent_key

    # --- Update JSON on disk ---
    child_path = getattr(child, "file_path", None)
    if not isinstance(child_path, Path):
        messagebox.showerror(
            "Error",
            "Selected child node does not have a valid file_path; "
            "cannot update JSON.",
        )
        return

    try:
        data = json.loads(child_path.read_text(encoding="utf-8"))
    except Exception as e:
        messagebox.showerror(
            "Error reading task file",
            f"Could not read JSON file:\n{child_path}\n\n{e}",
        )
        return

    depends_on = data.get("depends_on", [])
    if not isinstance(depends_on, list):
        depends_on = []

    if dep_str not in depends_on:
        depends_on.append(dep_str)
        data["depends_on"] = depends_on
        try:
            child_path.write_text(
                json.dumps(data, indent=2, sort_keys=False),
                encoding="utf-8",
            )
        except Exception as e:
            messagebox.showerror(
                "Error writing task file",
                f"Could not write JSON file:\n{child_path}\n\n{e}",
            )
            return

    # --- Update in-memory structures for this session ---

    # Raw dependency strings (what dag_builder originally reads)
    dep_raw = getattr(child, "depends_on_raw", None)
    if isinstance(dep_raw, list) and dep_str not in dep_raw:
        dep_raw.append(dep_str)

    # Resolved dependency keys (what DAGCanvas uses for edges/info)
    if isinstance(existing_deps, list) and parent_key not in existing_deps:
        existing_deps.append(parent_key)

    # Parent children list (may store keys or TaskNode objects)
    children_list = getattr(parent, "children", None)
    if isinstance(children_list, list):
        if children_list:
            first = children_list[0]
            if isinstance(first, str):
                if child_key not in children_list:
                    children_list.append(child_key)
            else:
                # Assume TaskNode instances
                if child not in children_list:
                    children_list.append(child)
        else:
            # Empty list: use keys (matches DAGCanvas' info rendering)
            children_list.append(child_key)

    # Finally, draw the new edge visually
    create_edge_line(self, parent_key, child_key)