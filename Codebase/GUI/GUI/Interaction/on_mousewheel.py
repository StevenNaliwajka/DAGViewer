def on_mousewheel(self, event):
    if getattr(event, "num", None) == 4 or event.delta > 0:
        self.yview_scroll(-2, "units")
    else:
        self.yview_scroll(2, "units")