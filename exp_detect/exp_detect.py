import tkinter as tk
from tkinter import ttk

class App:
    def __init__(self, root: tk.Tk):
        root.title("Simple Tkinter UI")
        root.geometry("1000x400")

        container = ttk.Frame(root, padding=20)
        container.pack(fill="both", expand=True)

        self.select_btn = ttk.Button(container, text="Select", command=self.on_select)
        self.select_btn.pack(pady=(0, 12))

        self.info_label = ttk.Label(container, text="Press Select to start the recording.")
        self.info_label.pack(anchor="w")

        self.topleft_output_var = tk.StringVar(value="Last position: ( , )")
        self.buttonright_output_var = tk.StringVar(value="Last position: ( , )")
        ttk.Label(container, textvariable=self.topleft_output_var).pack(anchor="w")
        ttk.Label(container, textvariable=self.buttonright_output_var).pack(anchor="w")

        self.output = ttk.Label(container, text="")
        self.output.pack(anchor="w")

        root.bind("1", self.on_key_1)        # top-row '1'
        root.bind("<KP_1>", self.on_key_1)   # numpad '1'

        root.bind("2", self.on_key_2)        # top-row '2'
        root.bind("<KP_2>", self.on_key_2)   # numpad '2'

        root.bind("<Return>", self.on_enter) # Enter to exit selecting mode

        self.root = root
        self.selecting = False   # are we currently in "selecting mode"?
        self.top_left = None     # (x, y) recorded by '1'
        self.bottom_right = None # (x, y) recorded by '2'

    def on_select(self):
        """Enter selecting mode and reset previous points."""
        self.selecting = True
        self.top_left = None
        self.bottom_right = None
        self.topleft_output_var.set("Last position: ( , )")
        self.buttonright_output_var.set("Last position: ( , )")
        self.info_label.config(text="Selecting mode: Press '1': Top-Left, '2': Bottom-Right, Enter: Finish.")
        self.root.focus_set()

    def on_key_1(self, event: tk.Event):
        if not self.selecting:
            return

        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        self.top_left = (x, y)
        self.topleft_output_var.set(f"Last position: TopLeft ({x}, {y})")
        print(f"Recorded at screen coords: TopLeft ({x}, {y})")

    def on_key_2(self, event: tk.Event):
        if not self.selecting:
            return

        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        self.bottom_right = (x, y)
        self.buttonright_output_var.set(f"Last position: ButtomRight ({x}, {y})")
        print(f"Recorded at screen coords: ButtomRight ({x}, {y})")

    def on_enter(self, event: tk.Event):
        """Exit selecting mode. If both corners exist, normalize and report."""
        if not self.selecting:
            return
        self.selecting = False

        if self.top_left and self.bottom_right:
            x1, y1 = self.top_left
            x2, y2 = self.bottom_right
            left, right = min(x1, x2), max(x1, x2)
            top, bottom = min(y1, y2), max(y1, y2)
            width, height = right - left, bottom - top
            self.output.config(
                text=f"Rect: left={left}, top={top}, right={right}, bottom={bottom},\n"
                     f"size=({width}x{height})"
            )
            print(
                f"Normalized rect -> TL=({left},{top}), TR=({right},{top}), "
                f"BL=({left},{bottom}), BR=({right},{bottom}), size=({width}x{height})"
            )
        else:
            # Not enough points; just exit mode cleanly
            self.output.config(text="Selection cancelled (points incomplete). Press Select to start again.")
            print("Selection cancelled: need both Top-Left (1) and Bottom-Right (2).")

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
