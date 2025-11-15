#!/usr/bin/env python3
import json
import re
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# ========== CONFIG ==========
TASKS_DIR = Path("Tasks")
DEFAULT_OWNER = "Steven"
DEFAULT_DEPENDS_ON = []   # e.g. ["clean_data"] if you want a default
DEFAULT_GROUP = "AAAA"
# ============================


def slugify(text: str) -> str:
    """Turn task title into a safe filename fragment."""
    text = text.strip().lower()
    text = re.sub(r"\s+", "_", text)        # spaces -> underscores
    text = re.sub(r"[^a-z0-9_]", "", text)  # keep only a-z, 0-9, _
    return text or "task"


def get_next_id(tasks_dir: Path) -> int:
    """Scan existing JSON files and return the next integer id."""
    tasks_dir.mkdir(parents=True, exist_ok=True)

    max_id = 0
    for path in tasks_dir.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("id"), int):
                max_id = max(max_id, data["id"])
        except Exception:
            # Ignore invalid JSON files
            continue
    return max_id + 1


class TaskCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Creator")

        # ensure tasks dir exists
        TASKS_DIR.mkdir(parents=True, exist_ok=True)

        # Track current ID
        self.current_id = get_next_id(TASKS_DIR)

        # ----- Widgets -----
        # Task label + entry
        tk.Label(root, text="Task:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.task_entry = tk.Entry(root, width=50)
        self.task_entry.grid(row=0, column=1, columnspan=2, sticky="we", padx=5, pady=5)

        # Description label + text
        tk.Label(root, text="Description:").grid(row=1, column=0, sticky="ne", padx=5, pady=5)
        self.desc_text = tk.Text(root, width=50, height=6)
        self.desc_text.grid(row=1, column=1, columnspan=2, sticky="we", padx=5, pady=5)

        # Group label + entry
        tk.Label(root, text="Group:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.group_entry = tk.Entry(root, width=20)
        self.group_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.group_entry.insert(0, DEFAULT_GROUP)

        # Save button
        self.save_button = tk.Button(root, text="Save Task", command=self.save_task)
        self.save_button.grid(row=3, column=1, sticky="e", padx=5, pady=10)

        # Quit button
        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.grid(row=3, column=2, sticky="w", padx=5, pady=10)

        # Status label
        self.status_label = tk.Label(root, text=f"Next ID: {self.current_id}", anchor="w")
        self.status_label.grid(row=4, column=0, columnspan=3, sticky="we", padx=5, pady=5)

        # Make columns resize nicely
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=0)

    def save_task(self):
        task = self.task_entry.get().strip()
        if not task:
            messagebox.showwarning("Missing Task", "Please enter a task title.")
            return

        description = self.desc_text.get("1.0", "end-1c").strip()
        group = self.group_entry.get().strip() or DEFAULT_GROUP

        # Build task dict based on your template
        task_dict = {
            "task": task,
            "description": description,
            "id": self.current_id,
            "group": group,
            "owner": DEFAULT_OWNER,
            "depends_on": DEFAULT_DEPENDS_ON,
            "updates": []  # start empty; you can add updates later
        }

        slug = slugify(task)
        filename = f"{self.current_id:04d}_{slug}.json"
        path = TASKS_DIR / filename

        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(task_dict, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save task:\n{e}")
            return

        # Confirmation + prepare for next task
        self.status_label.config(text=f"Saved: {path.name}")
        self.task_entry.delete(0, "end")
        self.desc_text.delete("1.0", "end")
        self.task_entry.focus_set()

        self.current_id += 1
        # show next ID in window title / status
        self.root.title(f"Task Creator (Next ID: {self.current_id})")

    # You could add more methods later (e.g., for default owner, depends_on, etc.)


def main():
    root = tk.Tk()
    app = TaskCreatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
