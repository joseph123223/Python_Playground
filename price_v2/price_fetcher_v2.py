import tkinter as tk
import requests
import json
import os
from tkinter import ttk

# Fixed Variables
SAVE_FILE = "assets_data.json"
DEFAULT_W, DEFAULT_H = 600, 300

# Fetch symbol data
def fetch_valid_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        symbols = set()
        for s in data['symbols']:
            symbols.add(s['baseAsset'])
            symbols.add(s['quoteAsset'])
        return symbols
    except Exception as e:
        print("Error fetching symbols:", e)
        return set()

# Custom message box
def show_custom_messagebox(w, h, title, message, color):
    err = tk.Toplevel()
    err.title(title)

    screen_width = err.winfo_screenwidth()
    screen_height = err.winfo_screenheight()
    x = (screen_width // 4) - (w // 2)
    y = (screen_height // 2) - (h // 2)
    err.geometry(f"{w}x{h}+{x}+{y}")

    err.resizable(False, False)

    tk.Label(err, text=message, font=("Arial", 12), fg=color, wraplength=380).pack(pady=20)
    tk.Button(err, text="OK", font=("Arial", 12), command=err.destroy).pack(pady=10)

def main():
    window = tk.Tk()
    window.title("Crypto Tool")

    w, h = 1400, 1000
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 4) - (w // 2)
    y = (screen_height // 2) - (h // 2)
    window.geometry(f"{w}x{h}+{x}+{y}")

    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)

    main_frame = tk.Frame(window, bg="#f0f0f0")
    main_frame.grid(sticky="nsew")

    button_frame = tk.Frame(main_frame, bg="#f0f0f0")
    button_frame.pack(pady=20)

    content_container = tk.Frame(main_frame, bg="#f0f0f0")
    content_container.pack(expand=True, fill="both", padx=20, pady=10)

    # --- Distribution Page ---
    distribution_page = tk.Frame(content_container, bg="#ffffff", bd=2, relief="groove")
    distribution_page.place(relwidth=1, relheight=1)

    action_frame = tk.Frame(distribution_page, bg="#e0e0e0")
    action_frame.pack(fill="x", pady=10)

    valid_symbols = fetch_valid_symbols()
    asset_data = {}

    display_frame = tk.Frame(distribution_page, bg="#ffffff")
    display_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))

    summary_frame = tk.Frame(display_frame, bg="#e8f4fc")
    summary_frame.pack(fill="both", expand=True)
    # summary_label = tk.Label(summary_frame, text="Summary / Statistics Area", font=("Arial", 14), bg="#e8f4fc")
    # summary_label.pack(pady=10)

    summary_text = tk.Text(summary_frame, font=("Consolas", 12), height=8, state="disabled", bg="#e8f4fc", bd=0)
    summary_text.pack(expand=True, fill="both", padx=10, pady=(0, 10))

    log_frame = tk.Frame(display_frame, height=120, bg="#f9f9f9")
    log_frame.pack(fill="x", pady=(10, 0))

    scrollbar = tk.Scrollbar(log_frame)
    scrollbar.pack(side="right", fill="y")

    log_text = tk.Text(log_frame, font=("Consolas", 11), height=5, yscrollcommand=scrollbar.set)
    log_text.pack(side="left", fill="both", expand=True)
    log_text.config(state="disabled")

    scrollbar.config(command=log_text.yview)

    # Log Section
    def log_action(message):
        log_text.config(state="normal")
        log_text.insert("end", message + "\n")
        log_text.see("end")
        log_text.config(state="disabled")

    # Summary Section
    def update_summary():
        summary_text.config(state="normal")
        summary_text.delete("1.0", "end")
        summary_text.insert("end", "Owned Assets:\n")
        for coin, (amount, total_cost, avg_cost) in asset_data.items():
            summary_text.insert("end", f"{amount:.4f} {coin} - avg cost: {avg_cost:.2f} USD | total cost: {total_cost:.2f} USD.\n")
        summary_text.config(state="disabled")

    # Buy Window
    def open_buy_window():
        buy_window = tk.Toplevel(window)
        buy_window.title("Buy Crypto")

        w, h = 1000, 600
        screen_width = buy_window.winfo_screenwidth()
        screen_height = buy_window.winfo_screenheight()
        x = (screen_width // 4) - (w // 2)
        y = (screen_height // 2) - (h // 2)
        buy_window.geometry(f"{w}x{h}+{x}+{y}")

        tk.Label(buy_window, text="Coin Name:", font=("Arial", 12)).pack(pady=5)
        name_entry = tk.Entry(buy_window, font=("Arial", 12))
        name_entry.pack(pady=5)

        tk.Label(buy_window, text="Buy Price:", font=("Arial", 12)).pack(pady=5)
        price_entry = tk.Entry(buy_window, font=("Arial", 12))
        price_entry.pack(pady=5)

        tk.Label(buy_window, text="Amount:", font=("Arial", 12)).pack(pady=5)
        amount_entry = tk.Entry(buy_window, font=("Arial", 12))
        amount_entry.pack(pady=5)

        def submit_event(event):
            submit()

        def submit():
            name = name_entry.get().upper()
            try:
                price = float(price_entry.get())
                amount = float(amount_entry.get())
                cost = price * amount
            except ValueError:
                show_custom_messagebox(DEFAULT_W, DEFAULT_H, "Invalid Input", "Price and Amount must be numbers.", "red")
                return

            if name not in valid_symbols:
                show_custom_messagebox(DEFAULT_W, DEFAULT_H, "Invalid Coin", f"'{name}' is not a valid symbol on Binance.", "red")
                return

            if name in asset_data:
                old_amount, old_cost, _ = asset_data[name]
                new_amount = old_amount + amount
                new_cost = old_cost + cost
                avg_cost = new_cost / new_amount
                asset_data[name] = (new_amount, new_cost, avg_cost)
            else:
                asset_data[name] = (amount, cost, price)

            log_action(f"BUY: {amount} {name} at price: {price} USD")
            update_summary()
            buy_window.destroy()

        buy_window.bind("<Return>", submit_event)
        buy_window.bind("<KP_Enter>", submit_event)

        tk.Button(buy_window, text="Submit", font=("Arial", 12), command=submit).pack(pady=15)

    # Sell Window
    def open_sell_window():
        sell_window = tk.Toplevel(window)
        sell_window.title("Sell Crypto")

        w, h = 1000, 600
        screen_width = sell_window.winfo_screenwidth()
        screen_height = sell_window.winfo_screenheight()
        x = (screen_width // 4) - (w // 2)
        y = (screen_height // 2) - (h // 2)
        sell_window.geometry(f"{w}x{h}+{x}+{y}")

        tk.Label(sell_window, text="Coin Name:", font=("Arial", 12)).pack(pady=5)
        name_entry = tk.Entry(sell_window, font=("Arial", 12))
        name_entry.pack(pady=5)

        tk.Label(sell_window, text="Sell Price:", font=("Arial", 12)).pack(pady=5)
        price_entry = tk.Entry(sell_window, font=("Arial", 12))
        price_entry.pack(pady=5)

        tk.Label(sell_window, text="Amount:", font=("Arial", 12)).pack(pady=5)
        amount_entry = tk.Entry(sell_window, font=("Arial", 12))
        amount_entry.pack(pady=5)

        def submit_event(event):
            submit()

        def submit():
            name = name_entry.get().upper()
            try:
                price = float(price_entry.get())
                amount = float(amount_entry.get())
            except ValueError:
                show_custom_messagebox(DEFAULT_W, DEFAULT_H, "Invalid Input", "Price and Amount must be numbers.", "red")
                return

            if name not in asset_data:
                show_custom_messagebox(DEFAULT_W, DEFAULT_H, "No Asset", f"You do not own any {name} to sell.", "red")
                return

            owned_amount, total_cost, avg_cost = asset_data[name]
            if amount > owned_amount:
                show_custom_messagebox(DEFAULT_W, DEFAULT_H, "Insufficient Asset", f"You only own {owned_amount:.4f} {name}.", "red")
                return

            new_amount = owned_amount - amount
            realized_cost = avg_cost * amount
            new_total_cost = total_cost - realized_cost

            if new_amount == 0:
                del asset_data[name]
            else:
                asset_data[name] = (new_amount, new_total_cost, avg_cost)

            log_action(f"SELL: {amount} {name} at {price} USD")
            update_summary()
            sell_window.destroy()

        sell_window.bind("<Return>", submit_event)
        sell_window.bind("<KP_Enter>", submit_event)

        tk.Button(sell_window, text="Submit", font=("Arial", 12), command=submit).pack(pady=15)

    # Saving Function
    def save_assets():
        try:
            with open("assets_data.json", "w") as f:
                json.dump(asset_data, f)
            show_custom_messagebox(400, 200 ,"", "Saving Successful", "green")
            log_action("[INFO] Asset data saved successfully.")
        except Exception as e:
            show_custom_messagebox(DEFAULT_W, DEFAULT_H, "Save Error", str(e), "red")

    # Loading Function
    def load_assets():
        nonlocal asset_data
        if not os.path.exists("assets_data.json"):
            log_action("[WARN] No save file found.")
            return
        try:
            with open("assets_data.json", "r") as f:
                asset_data = {k: tuple(v) for k, v in json.load(f).items()}
            show_custom_messagebox(400, 200, "", "Loading Successful", "green")
            update_summary()
            log_action("[INFO] Asset data loaded successfully.")
        except Exception as e:
            show_custom_messagebox(DEFAULT_W, DEFAULT_H, "Load Error", str(e), "red")

    # Clear function
    def clear_assets():
        asset_data.clear()
        update_summary()
        log_action("[INFO] All asset data cleared.")

    # Buttons
    buy_button = tk.Button(action_frame, text="Buy", font=("Arial", 12), width=10, command=open_buy_window)
    buy_button.pack(side="left", padx=10, pady=5)
    sell_button = tk.Button(action_frame, text="Sell", font=("Arial", 12), width=10, command=open_sell_window)
    sell_button.pack(side="left", padx=10, pady=5)
    save_button = tk.Button(action_frame, text="Save", font=("Arial", 12), width=10, command=save_assets)
    save_button.pack(side="left", padx=10, pady=5)
    load_button = tk.Button(action_frame, text="Load", font=("Arial", 12), width=10, command=load_assets)
    load_button.pack(side="left", padx=10, pady=5)
    clean_button = tk.Button(action_frame, text="Clean", font=("Arial", 12), width=10, command=clear_assets)
    clean_button.pack(side="left", padx=10, pady=5)

    # --- Price Fetcher Page ---
    price_fetcher_page = tk.Frame(content_container, bg="#ffffff", bd=2, relief="groove")
    price_fetcher_page.place(relwidth=1, relheight=1)

    # --- Page switch ---
    def show_page(page):
        page.tkraise()

    dist_button = tk.Button(button_frame, text="Asset Distribution", font=("Arial", 14), width=20, command=lambda: show_page(distribution_page))
    dist_button.grid(row=0, column=0, padx=10)

    price_button = tk.Button(button_frame, text="Price Fetcher", font=("Arial", 14), width=20, command=lambda: show_page(price_fetcher_page))
    price_button.grid(row=0, column=1, padx=10)

    show_page(distribution_page)

    window.mainloop()

if __name__ == "__main__":
    main()
