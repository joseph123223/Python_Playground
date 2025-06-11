import tkinter as tk
from tkinter import ttk

total_cost = 0.0
total_revenue = 0.0

def add_entry():
    global total_cost, total_revenue

    item = item_entry.get()
    price = price_entry.get()
    cost = cost_entry.get()

    try:
        price_val = float(price)
        cost_val = float(cost)
    except ValueError:
        return

    if item and price and cost:
        tree.insert("", "end", values=(item, f"{price_val:.2f}", f"{cost_val:.2f}"))
        item_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        cost_entry.delete(0, tk.END)

        total_cost += cost_val
        total_revenue += price_val
        update_summary()

def update_summary():
    profit = total_revenue - total_cost
    summary_line1.set(f"Total Cost:    {total_cost:8.2f}")
    summary_line2.set(f"Total Revenue: {total_revenue:8.2f}")
    summary_line3.set(f"Total Profit:  {profit:8.2f}")

root = tk.Tk()
root.title("Profit Recorder")

w, h = 1400, 900
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 4) - (w // 2)
y = (screen_height // 2) - (h // 2)
root.geometry(f"{w}x{h}+{x}+{y}")

input_frame = tk.Frame(root)
input_frame.pack(pady=5)

tk.Label(input_frame, text="Item:").grid(row=0, column=0, padx=5)
item_entry = tk.Entry(input_frame)
item_entry.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Price:").grid(row=0, column=2, padx=5)
price_entry = tk.Entry(input_frame)
price_entry.grid(row=0, column=3, padx=5)

tk.Label(input_frame, text="Cost:").grid(row=0, column=4, padx=5)
cost_entry = tk.Entry(input_frame)
cost_entry.grid(row=0, column=5, padx=5)

submit_btn = tk.Button(input_frame, text="Add", command=add_entry)
submit_btn.grid(row=0, column=6, padx=5)

tree_frame = tk.Frame(root)
tree_frame.pack(fill=tk.BOTH, expand=True)

tree = ttk.Treeview(tree_frame, columns=("Item", "Price", "Cost"), show="headings")
tree.heading("Item", text="Item")
tree.heading("Price", text="Price")
tree.heading("Cost", text="Cost")
tree.pack(fill=tk.BOTH, expand=True)

summary_frame = tk.Frame(root, bg="#ddd", height=55)
summary_frame.pack(fill=tk.X, pady=10, ipady=10)

summary_line1 = tk.StringVar()
summary_line2 = tk.StringVar()
summary_line3 = tk.StringVar()

tk.Label(summary_frame, textvariable=summary_line1, font=("Courier", 11), anchor="w", bg="#ddd").pack(anchor="w", padx=15, pady=5)
tk.Label(summary_frame, textvariable=summary_line2, font=("Courier", 11), anchor="w", bg="#ddd").pack(anchor="w", padx=15)
tk.Label(summary_frame, textvariable=summary_line3, font=("Courier", 11), anchor="w", bg="#ddd").pack(anchor="w", padx=15)

update_summary()
root.mainloop()
