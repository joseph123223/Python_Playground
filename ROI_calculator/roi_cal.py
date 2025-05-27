import tkinter as tk
from tkinter import ttk

def preview_inputs():
    base = base_price_var.get()
    scroll_price = scroll_price_var.get()
    scrolls = int(num_scrolls_var.get())

    # Collect selling prices
    sell_prices = {}
    for level in price_entries:
        try:
            sell_prices[level] = float(price_entries[level].get())
        except ValueError:
            sell_prices[level] = 0.0

    # Assume all scrolls use 60% success rate
    fixed_success_rate = 0.6

    # Strategy 1: Try all the way to +N
    roi_results = []
    result = (
        f"Base Price: {base} w\n"
        f"Scroll Price: {scroll_price} w\n"
        f"Scrolls Used: {scrolls}\n\n"
        "--- Strategy: Go +0 to +N with 60% scrolls ---\n"
    )

    prob = 1.0
    best_roi = float('-inf')
    best_level = 0

    for i in range(scrolls + 1):
        if i > 0:
            prob *= fixed_success_rate

        total_cost = base + scroll_price * i
        expected_value = sell_prices.get(i, 0.0)
        roi = expected_value * prob - total_cost

        roi_results.append((i, prob, expected_value, roi))

        if roi > best_roi:
            best_roi = roi
            best_level = i

        result += f"+{i} => Prob: {prob*100:.2f}%, Value: {expected_value} w, ROI: {roi:.2f} w\n"

    result += f"\nBest Level to Aim: +{best_level} with ROI {best_roi:.2f} w\n"

    # Output to display
    result_text.config(state='normal')
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, result)
    result_text.config(state='disabled')

def update_price_inputs(*args):
    for widget in price_scrollable_frame.winfo_children():
        widget.destroy()

    try:
        max_level = int(num_scrolls_var.get())
    except ValueError:
        return

    label = ttk.Label(price_scrollable_frame, text="Sell Price +0 (w):")
    price_entry = ttk.Entry(price_scrollable_frame)
    label.grid(row=0, column=0, sticky='w', padx=5, pady=2)
    price_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
    price_entries[0] = price_entry

    for i in range(1, max_level + 1):
        label = ttk.Label(price_scrollable_frame, text=f"Sell Price +{i} (w):")
        price_entry = ttk.Entry(price_scrollable_frame)

        rate_label = ttk.Label(price_scrollable_frame, text=f"Rate:")
        rate_combo = ttk.Combobox(price_scrollable_frame, values=["10%", "60%", "100%"], state="readonly")
        rate_combo.set("60%")

        label.grid(row=i, column=0, sticky='w', padx=5, pady=2)
        price_entry.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
        rate_label.grid(row=i, column=2, sticky='w', padx=5, pady=2)
        rate_combo.grid(row=i, column=3, sticky='ew', padx=5, pady=2)

        price_entries[i] = price_entry
        rate_selectors[i] = rate_combo

    price_scrollable_frame.columnconfigure(1, weight=1)
    price_scrollable_frame.columnconfigure(3, weight=1)

## Main Func
root = tk.Tk()
root.title("Maplestory Artale ROI Input")

w, h = 1100, 1400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 4) - (w // 2)
y = (screen_height // 2) - (h // 2)
root.geometry(f"{w}x{h}+{x}+{y}")

base_price_var = tk.DoubleVar(value=250.0)
scroll_price_var = tk.DoubleVar(value=10.0)
num_scrolls_var = tk.StringVar(value="0")
success_rate_var = tk.StringVar(value="60%")
price_entries = {}
rate_selectors = {}

ttk.Label(root, text="Base Price (w):").pack(anchor='w', padx=10, pady=(10, 0))
ttk.Entry(root, textvariable=base_price_var).pack(fill='x', padx=10)

ttk.Label(root, text="Scroll Price (w):").pack(anchor='w', padx=10, pady=(10, 0))
ttk.Entry(root, textvariable=scroll_price_var).pack(fill='x', padx=10)

ttk.Label(root, text="Scrolls Used:").pack(anchor='w', padx=10, pady=(10, 0))
ttk.Combobox(root, textvariable=num_scrolls_var, values=[str(i) for i in range(1, 11)], state="readonly").pack(fill='x', padx=10)

num_scrolls_var.trace_add("write", update_price_inputs)

price_canvas = tk.Canvas(root, height=550)
price_scrollbar = ttk.Scrollbar(root, orient="vertical", command=price_canvas.yview)
price_scrollable_frame = ttk.Frame(price_canvas)

price_scrollable_frame.bind("<Configure>", lambda e: price_canvas.configure(scrollregion=price_canvas.bbox("all")))

price_canvas.create_window((0, 0), window=price_scrollable_frame, anchor="nw")
price_canvas.configure(yscrollcommand=price_scrollbar.set)

price_canvas.pack(fill='x', padx=10, pady=(10, 0))
price_scrollbar.pack(fill='y', side='right', padx=(0, 10))

ttk.Button(root, text="Enter", command=preview_inputs).pack(pady=15)

result_text = tk.Text(root, height=14, state='disabled')
result_text.pack(fill='both', padx=10, pady=(0, 10))

root.mainloop()