import tkinter as tk

def bind_submit_on_enter(root: tk.Tk, can_submit, on_submit) -> None:
    """
    Bind ENTER so that:

    - If can_submit() returns True, call on_submit().
    - Otherwise, let the normal focus/entry behavior happen.

    This is meant to be shared between UIs like the Task Create Run, etc.
    """

    def _handler(event):
        # Only trigger if user has filled in required fields
        try:
            if can_submit():
                on_submit()
                # Prevent default "ding" or focus changes
                return "break"
        except Exception as e:
            print(f"Error in can_submit/on_submit: {e}")
        # else allow normal behavior

    # Global within this application
    root.bind_all("<Return>", _handler)
