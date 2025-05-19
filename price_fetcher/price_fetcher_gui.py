import tkinter as tk
import json
import os
import datetime
import requests
from tkinter import messagebox, scrolledtext

# ------------------ Global Variables ------------------

total_owned, avg_cost, start_prices, current_prices = {} ,{}, {} ,{}
valid_extras = {"USDT", "USDC"}
fetch_interval = 5000
is_tracking_paused = False
active_view = None

# ------------------ Utility Functions ------------------

def get_valid_binance_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        response = requests.get(url)
        data = response.json()
        symbols = [s['symbol'] for s in data['symbols']]
        return set(symbols)
    except Exception as e:
        print("❌ Can't fetch data from Binance: ", e)
        return set()

def switch_view(view_name):
    global active_view, is_tracking_paused

    if active_view == view_name:
        return

    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)

    if view_name == "assets":
        success = calculate_assets()

        if not success:
            return

        is_tracking_paused = True
        toggle_button.config(text="⏸ Pause")
        tracking_status.config(text="⏸ Paused", fg="red")

        update_status("📊 Showing asset distributions...")
        dist_btn.config(state="disabled", relief="sunken")
        track_btn.config(state="normal", relief="raised")

    elif view_name == "tracker":
        is_tracking_paused = False
        toggle_button.config(text="⏸ Pause")
        tracking_status.config(text="🔄 Tracking", fg="black")

        start_price_tracker()
        update_status("📈 Price tracker started.")

        track_btn.config(state="disabled", relief="sunken")
        dist_btn.config(state="normal", relief="raised")

    active_view = view_name

def reset_buttons():
    global active_view

    active_view = None
    dist_btn.config(state="normal", relief="raised")
    track_btn.config(state="normal", relief="raised")

def show_error(title, message):
    err_win = tk.Toplevel(window)
    err_win.title(title)
    err_win.geometry("500x250")
    err_win.resizable(False, False)

    tk.Label(err_win, text=message, fg="red", font=("Arial", 12), wraplength=380, justify="left").pack(pady=30, padx=20)
    tk.Button(err_win, text="OK", command=err_win.destroy).pack(pady=10)

def show_info(title, message):
    info_win = tk.Toplevel(window)
    info_win.title(title)
    info_win.geometry("500x250")
    info_win.resizable(False, False)

    tk.Label(
        info_win,
        text=message,
        fg="blue",
        font=("Arial", 12),
        wraplength=400,
        justify="left"
    ).pack(pady=30, padx=20)

    tk.Button(info_win, text="OK", command=info_win.destroy).pack(pady=10)

def update_status(message, timeout=3000):
    status_var.set(message)
    window.after(timeout, lambda: status_var.set(""))

# Save Data

def save_data():
    if not total_owned:
        show_error("Empty Data", "❗ No assets to save. Please add some data first.")
        return

    try:
        data = {
            "total_owned": total_owned,
            "avg_cost": avg_cost
        }
        path = os.path.abspath("assets_data.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        show_info("Saved", f"✅ Asset data saved to:\n{path}")
        update_status("✅ Data saved to assets_data.json")
    except Exception as e:
        show_error("Save Error", str(e))

# Load Data

def load_data():
    if not os.path.exists("assets_data.json"):
        show_error("Not Found", "⚠️ No saved asset data found.")
        return

    try:
        with open("assets_data.json", "r") as f:
            data = json.load(f)

        loaded_total = data.get("total_owned", {})
        loaded_costs = data.get("avg_cost", {})

        if not loaded_total:
            show_error("Empty Data", "⚠️ The saved asset data is empty and cannot be loaded.")
            return

        total_owned.clear()
        avg_cost.clear()
        total_owned.update(loaded_total)
        avg_cost.update(loaded_costs)

        calculate_assets()
        show_info("Loaded", "✅ Asset data loaded successfully!")
        update_status("✅ Data loaded from assets_data.json")
    except Exception as e:
        show_error("Load Error", str(e))

def clear_data():
    confirm = messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all current asset data?")
    if not confirm:
        return

    total_owned.clear()
    avg_cost.clear()

    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.config(state="disabled")
    update_status("🗑 All asset data has been cleared.")

# Add Distributions

def add_assets():

    window.update_idletasks()
    main_x = window.winfo_x()
    main_y = window.winfo_y()
    main_width = window.winfo_width()

    popup_x = main_x + main_width + 20
    popup_y = main_y + 50

    add_win = tk.Toplevel(window)
    add_win.title("Add Assets")
    add_win.geometry(f"1300x550+{popup_x}+{popup_y}")

    input_frame = tk.Frame(add_win)
    input_frame.pack(pady=15)

    # -- Input --

    tk.Label(input_frame, text="Type:").grid(row=0, column=0, padx=5)
    coin_entry = tk.Entry(input_frame, width=25)
    coin_entry.grid(row=0, column=1, padx=5)

    tk.Label(input_frame, text="Amount:").grid(row=0, column=2, padx=5)
    amount_entry = tk.Entry(input_frame, width=12)
    amount_entry.grid(row=0, column=3, padx=5)

    tk.Label(input_frame, text="Avg Cost:").grid(row=0, column=4, padx=5)
    cost_entry = tk.Entry(input_frame, width=18)
    cost_entry.grid(row=0, column=5, padx=5)

    # -- PlaceHolder --
    def set_placeholder(entry, placeholder_text):
        def on_focus_in(event):
            if entry.get() == placeholder_text and entry['fg'] == 'gray':
                entry.delete(0, tk.END)
                entry.config(fg='black')

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder_text)
                entry.config(fg='gray')

        def reset_if_placeholder():
            if entry.get() == placeholder_text and entry['fg'] == 'gray':
                entry.delete(0, tk.END)
                entry.config(fg='black')

        entry.insert(0, placeholder_text)
        entry.config(fg='gray')

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        return reset_if_placeholder

    set_placeholder(coin_entry, "ex: BTCUSDT/USDT")
    set_placeholder(amount_entry, "ex: 0.5")
    clear_cost_placeholder = set_placeholder(cost_entry, "ex: 80000")

    # Display Output

    popup_output = scrolledtext.ScrolledText(add_win, width=70, height=12, wrap=tk.WORD)
    popup_output.config(state="disabled")
    popup_output.pack(pady=10)

    # Lock cost

    def handle_coin_entry_change(event):
        coin = coin_entry.get().strip().upper()
        if coin in valid_extras:
            clear_cost_placeholder()
            cost_entry.config(state="normal", fg="black")
            cost_entry.delete(0, tk.END)
            cost_entry.insert(0, "1")
            cost_entry.config(state="disabled")
        else:
            cost_entry.config(state="normal")
            cost_entry.delete(0, tk.END)
            set_placeholder(cost_entry, "ex: 80000")

    coin_entry.bind("<KeyRelease>", handle_coin_entry_change)

    # Add Item

    def add_one():
        coin = coin_entry.get().strip().upper()
        amount_input = amount_entry.get().strip()
        cost_input = cost_entry.get().strip()

        if not coin:
            show_error("Invalid Type", "'Type' cannot be empty!")
            return

        if coin not in valid_binance_symbols and coin not in valid_extras:
            show_error("Error:", f"The type [{coin}] is invalid or unsupported by Binance.")
            return

        try:
            amount = float(amount_input)
            if amount <= 0:
                raise ValueError
        except ValueError:
            show_error("Invalid Amount", "Amount should be a positive number.")
            return

        if coin in valid_extras:
            new_cost = 1.0
        else:
            if cost_input:
                try:
                    new_cost = float(cost_input)
                    if new_cost <= 0:
                        raise ValueError
                except ValueError:
                    show_error("Invalid Cost", "Cost should be a positive number.")
                    return
            else:
                new_cost = None

        total_owned[coin] = total_owned.get(coin, 0) + amount

        if coin in valid_extras:
            avg_cost[coin] = 1.0
        elif new_cost is not None:
            if coin in avg_cost:
                old_total_amount = total_owned[coin] - amount
                old_cost = avg_cost[coin]
                total_value = old_total_amount * old_cost + amount * new_cost
                avg_cost[coin] = round(total_value / (old_total_amount + amount), 5)
            else:
                avg_cost[coin] = new_cost

        # Display Added Record

        popup_output.config(state="normal")
        popup_output.insert(tk.END, f"✅ Added asset: {coin} = {amount}")
        if coin not in valid_extras and cost_input:
            popup_output.insert(tk.END, f"， Average cost = {cost_input}")
        popup_output.insert(tk.END, "\n")
        popup_output.config(state="disabled")

        # Clean the Outputs

        coin_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        cost_entry.config(state="normal")
        cost_entry.delete(0, tk.END)
        clear_cost_placeholder()
        calculate_assets()

    # Key Binding
    add_win.bind("<Return>", lambda event: add_one())

    btn_frame = tk.Frame(add_win)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Add", command=add_one).pack(side="left", padx=10)

def calculate_assets():
    if not total_owned:
        show_error("No Assets", "Please add assets before calculating.")
        return False

    update_status("📊 Showing asset distributions...")

    try:
        combined_owned = {}
        combined_cost = {}

        for key, amount in total_owned.items():
            if key.endswith("USDT") or key.endswith("USDC"):
                symbol = key[:-4]
                base_key = f"{symbol}/USD" if symbol else "USD"
            else:
                base_key = key

            combined_owned[base_key] = combined_owned.get(base_key, 0) + amount

            if key in avg_cost:
                old_amount = combined_owned[base_key] - amount
                old_cost = combined_cost.get(base_key, 0)
                combined_cost[base_key] = (
                    (old_amount * old_cost + amount * avg_cost[key]) /
                    (old_amount + amount)
                )
            elif base_key not in combined_cost:
                combined_cost[base_key] = 0

        portion = {
            key: round(combined_owned[key] * combined_cost.get(key, 1), 5)
            for key in combined_owned
        }
        total_cost = sum(portion.values())

        percentage = {
            key: round(value / total_cost * 100, 2)
            for key, value in portion.items()
        }

        result = "Your current owned assets:\n"
        for key, value in combined_owned.items():
            cost_str = f"{round(combined_cost[key], 5)}" if key in combined_cost else "[Not Available]"
            result += f"{key}: {value} - with avg cost {cost_str}\n"

        result += "\nYour current asset's distribution is:\n"
        for key, value in percentage.items():
            result += f"{key}: {value}%\n"

        result += f"\nTotal cost so far: {round(total_cost, 2)}"

        output_box.config(state="normal")
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, result)
        output_box.config(state="disabled")

        return True

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return False

def start_price_tracker():
    global start_prices, current_prices
    start_prices = {}
    current_prices = {}

    if not total_owned:
        show_error("No Assets", "Please add assets first before tracking prices.")
        to_reset_button = True
        return

    for key in total_owned:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={key}"
        try:
            response = requests.get(url)
            data = response.json()
            if 'price' in data:
                start_prices[key] = float(data['price'])
        except:
            continue

    update_status("📈 Price tracker started.")
    update_price_display()
    tracking_status.config(text="🔄 Tracking", fg="black")
    toggle_button.config(text="⏸ Pause")


def toggle_price_tracking():
    global is_tracking_paused
    is_tracking_paused = not is_tracking_paused
    if is_tracking_paused:
        toggle_button.config(text="▶ Resume")
        tracking_status.config(text="⏸ Paused", fg="red")
        update_status("⏸ Price tracking paused.")
    else:
        toggle_button.config(text="⏸ Pause")
        tracking_status.config(text="🔄 Tracking", fg="black")
        update_status("🔄 Price tracking resumed.")


def update_price_display():
    if is_tracking_paused:
        window.after(fetch_interval, update_price_display)
        return
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)

    now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    output_box.insert(tk.END, f"[{now}]\n", "header")
    output_box.insert(tk.END, "The current price of your owned coins are:\n\n", "header")
    output_box.insert(tk.END, "Type/Pair     | Price        | Change    | Change%\n")
    output_box.insert(tk.END, "-" * 55 + "\n")

    merged_assets = {}
    merged_costs = {}
    merged_start_price = {}
    merged_current_price = {}

    for key in total_owned:
        if key.endswith("USDT") or key.endswith("USDC"):
            symbol = key[:-4]
            base_key = f"{symbol}/USD" if symbol else "USD"
        else:
            base_key = key


        merged_assets[base_key] = merged_assets.get(base_key, 0) + total_owned[key]

        if key in avg_cost:
            prev_amount = merged_assets[base_key] - total_owned[key]
            prev_cost = merged_costs.get(base_key, 0)
            merged_costs[base_key] = (
                (prev_amount * prev_cost + total_owned[key] * avg_cost[key]) /
                (prev_amount + total_owned[key])
            )

        if key in start_prices:
            prev_amount = merged_assets[base_key] - total_owned[key]
            prev_price = merged_start_price.get(base_key, 0)
            merged_start_price[base_key] = (
                (prev_amount * prev_price + total_owned[key] * start_prices[key]) /
                (prev_amount + total_owned[key])
            )

        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={key}"
            response = requests.get(url)
            data = response.json()
            if 'price' in data:
                price = float(data['price'])
                prev_amount = merged_assets[base_key] - total_owned[key]
                prev_price = merged_current_price.get(base_key, 0)
                merged_current_price[base_key] = (
                    (prev_amount * prev_price + total_owned[key] * price) /
                    (prev_amount + total_owned[key])
                )
        except:
            continue

    for key in merged_assets:
        if key in merged_current_price and key in merged_start_price:
            cur = merged_current_price[key]
            start = merged_start_price[key]
            diff = round(cur - start, 5)
            percent = round(diff / start * 100, 2) if start else 0
            sign = '+' if diff > 0 else '-' if diff < 0 else ' '
            color_tag = "green" if diff > 0 else "red" if diff < 0 else "black"

            output_box.insert(tk.END, f"{key:<13} | {cur:>11.5f} | ", "default")
            output_box.insert(tk.END, f"{sign}{abs(diff):>8.5f} | ", color_tag)
            output_box.insert(tk.END, f"{sign}{abs(percent):>6.2f}%\n", color_tag)

    output_box.insert(tk.END, "\nUnrealized Profits:\n", "header")
    total_pnl = 0
    for key in merged_assets:
        if key in merged_current_price and key in merged_costs:
            pnl = round((merged_current_price[key] - merged_costs[key]) * merged_assets[key], 5)
            total_pnl += pnl
            sign = '+' if pnl > 0 else '-' if pnl < 0 else ' '
            color_tag = "green" if pnl > 0 else "red" if pnl < 0 else "black"

            output_box.insert(tk.END, f"{key}:\t", "default")
            output_box.insert(tk.END, f"{sign}{abs(pnl)}\n", color_tag)


    output_box.insert(tk.END, "\nTotal unrealized profit: ", "default")
    color_tag = "green" if total_pnl > 0 else "red" if total_pnl < 0 else "black"
    output_box.insert(tk.END, f"{round(total_pnl, 5)}\n", color_tag)

    output_box.config(state="disabled")

    output_box.tag_config("green", foreground="green")
    output_box.tag_config("red", foreground="red")
    output_box.tag_config("black", foreground="black")
    output_box.tag_config("error", foreground="gray")
    output_box.tag_config("header", font=("Arial", 11, "bold"))
    output_box.tag_config("subheader", font=("Arial", 10, "underline"))
    output_box.tag_config("default", foreground="black")

    window.after(fetch_interval, update_price_display)

valid_binance_symbols = get_valid_binance_symbols()

window = tk.Tk()
window.title("🔍 Crypto Calculator")
window.geometry("1300x900")

button_frame = tk.Frame(window, bg="#ddd")
button_frame.pack(fill="x", pady=10, padx=20)

action_frame = tk.Frame(window, bg="#ddd")
action_frame.pack(pady=5)

dist_btn = tk.Button(button_frame, text="📊 Display Distributions", height=2, command=lambda: switch_view("assets"))
track_btn = tk.Button(button_frame, text="📈 Start Tracker", height=2, command=lambda: switch_view("tracker"))

dist_btn.pack(side="left", expand=True, fill="x", padx=10)
track_btn.pack(side="right", expand=True, fill="x", padx=10)

tk.Button(action_frame, text="➕ Add", command=add_assets).pack(side="left", padx=5)
tk.Button(action_frame, text="💾 Save", command=save_data).pack(side="left", padx=5)
tk.Button(action_frame, text="📂 Load", command=load_data).pack(side="left", padx=5)
tk.Button(action_frame, text="🗑 Clear", command=clear_data).pack(side="left", padx=5)

toggle_button = tk.Button(action_frame, text="⏸ Pause", command=toggle_price_tracking)
toggle_button.pack(side="right", padx=5)

output_box = scrolledtext.ScrolledText(window, width=70, height=20, wrap=tk.WORD, font=("Courier New", 10))
output_box.config(state="disabled")
output_box.pack(pady=10)

tracking_status = tk.Label(window, text="", fg="black", font=("Arial", 9, "italic"))
tracking_status.pack(anchor="e", padx=20, pady=(0, 5))

status_var = tk.StringVar()
status_var.set("")

status_bar = tk.Label(window, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor="w", bg="#eee")
status_bar.pack(side="bottom", fill="x")

window.mainloop()