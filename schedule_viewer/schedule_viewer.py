import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta

# PREDEFINED DATA
names = ["Alice", "Bob", "Charlie"]
locations = ["Room A", "Room B", "Conference Hall"]

root = tk.Tk()
root.title("Schedule Viewer")

w, h = 1400, 1000
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 4) - (w // 2)
y = (screen_height // 2) - (h // 2)
root.geometry(f"{w}x{h}+{x}+{y}")

style = ttk.Style()
style.theme_use("default")

style.configure("TNotebook", background="#cccccc", borderwidth=0)
style.configure("TNotebook.Tab", background="#C0C0C0", foreground="black", width=w//2, anchor="center", padding=[0, 10])
style.map("TNotebook.Tab", background=[("selected", "#F0FFF0")], foreground=[("selected", "black")])

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

tab1 = tk.Frame(notebook, bg="#F0F8FF")
tab2 = tk.Frame(notebook, bg="#FAF0E6")

notebook.add(tab1, text="Add Schedule")
notebook.add(tab2, text="Schedule Display")

form_frame = tk.Frame(tab1, bg="#F0F8FF")
form_frame.pack(pady=50)

# Name
tk.Label(form_frame, text="Name:", font=("Arial", 14), bg="#F0F8FF").grid(row=0, column=0, padx=10, pady=20, sticky="e")
name_var = tk.StringVar()
name_select = ttk.Combobox(form_frame, textvariable=name_var, values=names, state="readonly", width=30)
name_select.grid(row=0, column=1, padx=10, pady=10)

# Date generator
def generate_future_dates(days=30):
    today = date.today()
    return [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, days + 1)]

# Date
tk.Label(form_frame, text="Date:", font=("Arial", 14), bg="#F0F8FF").grid(row=1, column=0, padx=10, pady=20, sticky="e")
date_var = tk.StringVar()
date_select = ttk.Combobox(form_frame, textvariable=date_var, values=generate_future_dates(), state="readonly", width=30)
date_select.grid(row=1, column=1, padx=10, pady=10)

# Location
tk.Label(form_frame, text="Location:", font=("Arial", 14), bg="#F0F8FF").grid(row=2, column=0, padx=10, pady=20, sticky="e")
location_var = tk.StringVar()
location_select = ttk.Combobox(form_frame, textvariable=location_var, values=locations, state="readonly", width=30)
location_select.grid(row=2, column=1, padx=10, pady=10)

tk.Label(tab2, text="This is the Schedule Display tab", font=("Arial", 16), bg="#fff2e6").pack(pady=30)

root.mainloop()