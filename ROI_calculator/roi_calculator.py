import tkinter as tk

def update_sell_inputs(*args):
    for widget in sell_inputs_frame.winfo_children():
        widget.destroy()

    try:
        garbage_level = int(garbage_var.get())
    except ValueError:
        return

    for i in range(garbage_level, 8):
        tk.Label(sell_inputs_frame, text=f"+{i} Price:", font=("Arial", 11), bg="#e8f0ff").grid(row=i-garbage_level, column=0, padx=10, pady=5, sticky="e")
        entry = tk.Entry(sell_inputs_frame, font=("Arial", 11), width=15)
        entry.grid(row=i-garbage_level, column=1, padx=10, pady=5)
        sell_price_entries[i] = entry

root = tk.Tk()
root.title("ROI Calculator")

COMMON_MIDDLE = 700
cost_gap_text_input = 300
sell_gap_text_input = 300

w, h = 1400, 1400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 4) - (w // 2)
y = (screen_height // 2) - (h // 2)
root.geometry(f"{w}x{h}+{x}+{y}")

## Section 1 - Cost
cost_frame = tk.Frame(root, bg="#f0f0f0", height=h//4, width=w)
cost_frame.place(x=0, y=0)

tk.Label(cost_frame, text="Equipment Cost:", font=("Arial", 11), bg="#f0f0f0", anchor='e' ).place(x=50, y=50)
entry_base_cost = tk.Entry(cost_frame, font=("Arial", 11), width=15)
entry_base_cost.place(x=cost_gap_text_input, y=50)

tk.Label(cost_frame, text="Scroll Cost:", font=("Arial", 11), bg="#f0f0f0", anchor='e' ).place(x=COMMON_MIDDLE + 50, y=50)
entry_scroll_cost = tk.Entry(cost_frame, font=("Arial", 11), width=15)
entry_scroll_cost.place(x=COMMON_MIDDLE + cost_gap_text_input, y=50)

## Section 2 - Sell
sell_frame = tk.Frame(root, bg="#e8f0ff", height=h//3, width=w)
sell_frame.place(x=0, y=h//4)

tk.Label(sell_frame, text="🗑️ Price:", font=("Arial", 11), bg="#e8f0ff").place(x=50, y=30)
entry_store_price = tk.Entry(sell_frame, font=("Arial", 11), width=15)
entry_store_price.place(x=sell_gap_text_input, y=30)

tk.Label(sell_frame, text="Below +X is garbage:", font=("Arial", 11), bg="#e8f0ff").place(x=COMMON_MIDDLE + 50, y=30)
garbage_var = tk.StringVar()
garbage_var.set("4")  # default
option = tk.OptionMenu(sell_frame, garbage_var, *[str(i) for i in range(1, 8)], command=update_sell_inputs)
option.config(font=("Arial", 11))
option.place(x=COMMON_MIDDLE + sell_gap_text_input, y=25)

sell_inputs_frame = tk.Frame(sell_frame, bg="#e8f0ff")
sell_inputs_frame.place(x=50, y=80)

sell_price_entries = {}

update_sell_inputs()

root.mainloop()