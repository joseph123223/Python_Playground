from itertools import combinations
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
import os

directory_path = '/home/miu7898/coding/python/joseph/basketball_analysis_tool/logos'
teams_png = [file for file in os.listdir(directory_path) if file.endswith('.png')]
teams = [ t.strip('.png') for t in teams_png ]
records = []
good_deals = []
bankroll = 2000
team_colors = {
    "Lakers": "plum1",
    "Celtics": "palegreen1",
    "Warriors": "lightblue",
    "Heat": "salmon1"
}

# Custom budget adjustment function
def custom_budget_partition(budget):
    partion_rate = 0.5
    return budget * partion_rate

# Evaluate parlay for a pair of matches
def evaluate_parlay_bet(p1, odds1, p2, odds2, bankroll):
    p_combined = p1 * p2
    odds_combined = odds1 * odds2
    b = odds_combined - 1
    q = 1 - p_combined
    expected_value = p_combined * odds_combined
    kelly_fraction = (b * p_combined - q) / b if b > 0 else 0
    kelly_fraction = max(kelly_fraction, 0)
    bet_size = kelly_fraction * bankroll

    return {
        "p_combined": p_combined,
        "odds_combined": odds_combined,
        "EV": expected_value,
        "Kelly": kelly_fraction,
        "Bet": custom_budget_partition(bet_size)
    }

def run_simulation():
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "Simulation results will be shown here after input window is implemented.\n")

def open_input_window():
    input_win = tk.Toplevel(root)
    input_win.title("Add Match Info")
    input_win.geometry("1100x800")

    # Position the input window to the right of the main window
    x = root.winfo_x() + root.winfo_width() + 10
    y = root.winfo_y()
    input_win.geometry(f"+{x}+{y}")

    # Labels
    ttk.Label(input_win, text="Home Team:").grid(row=0, column=0, padx=20, pady=10)
    ttk.Label(input_win, text="Away Team:").grid(row=1, column=0, padx=20, pady=10)
    ttk.Label(input_win, text="Select Team:").grid(row=2, column=0, padx=20, pady=10)
    ttk.Label(input_win, text="Win Rate (%):").grid(row=3, column=0, padx=20, pady=10)
    ttk.Label(input_win, text="Odds:").grid(row=4, column=0, padx=20, pady=10)

    # Dropdowns and entries
    home_team_var = tk.StringVar()
    away_team_var = tk.StringVar()
    select_team_var = tk.StringVar()

    home_dropdown = ttk.Combobox(input_win, textvariable=home_team_var, values=teams, state="readonly")
    away_dropdown = ttk.Combobox(input_win, textvariable=away_team_var, values=teams, state="readonly")
    select_dropdown = ttk.Combobox(input_win, textvariable=select_team_var, values=[], state="readonly")

    home_dropdown.grid(row=0, column=1, padx=5, pady=5)
    away_dropdown.grid(row=1, column=1, padx=5, pady=5)
    select_dropdown.grid(row=2, column=1, padx=5, pady=5)

    result_display = tk.Text(input_win, height=10, width=60)
    result_display.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    # Update Select Team dropdown when home/away changes
    def update_select_options(*args):
        options = []
        if home_team_var.get():
            options.append(home_team_var.get())
        if away_team_var.get() and away_team_var.get() != home_team_var.get():
            options.append(away_team_var.get())
        select_dropdown["values"] = options
        if select_team_var.get() not in options:
            select_team_var.set("")

    home_team_var.trace_add('write', update_select_options)
    away_team_var.trace_add('write', update_select_options)

    # Entries for win rate and odds
    entry_p = ttk.Entry(input_win)
    entry_odds = ttk.Entry(input_win)
    entry_p.grid(row=3, column=1, padx=5, pady=5)
    entry_odds.grid(row=4, column=1, padx=5, pady=5)

    # Confirm button placeholder
    def submit_match():
        home = home_team_var.get()
        away = away_team_var.get()
        selected = select_team_var.get()
        win_rate_input = entry_p.get()
        odds_input = entry_odds.get()

        if not home or not away or not selected or not win_rate_input or not odds_input:
            messagebox.showwarning("Missing Input", "Please fill in all fields.")
            return
        if home == away:
            messagebox.showerror("Invalid Match", "Home and Away teams must be different.")
            return

        try:
            win_rate = float(win_rate_input) / 100
            odds = float(odds_input)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for win rate and odds.")
            return

        records.append({
            "match": f"{home} vs {away}",
            "selected_team": selected,
            "win_rate": win_rate,
            "odds": odds,
        })

        result_display.delete("1.0", tk.END)
        result_display.insert(tk.END, "==============================\n")
        result_display.insert(tk.END, "The record has been added by the following info:\n")
        result_display.insert(tk.END, f"🏟️ Match: {home} vs {away}\n")
        result_display.insert(tk.END, f"🎯  Selected Team: {selected}\n")
        result_display.insert(tk.END, f"📈  Win Rate: {win_rate}\n")
        result_display.insert(tk.END, f"💰  Odds: {odds}\n")
        result_display.insert(tk.END, "==============================\n")

        home_team_var.set("")
        away_team_var.set("")
        select_team_var.set("")
        entry_p.delete(0, tk.END)
        entry_odds.delete(0, tk.END)

    ttk.Button(input_win, text="Add", command=submit_match).grid(row=5, column=0, padx=10, pady=10)

    def clear_combinations():
        records.clear()
        result_display.delete("1.0", tk.END)
        result_display.insert(tk.END, "All records have been cleared.")

    ttk.Button(input_win, text="Clear", command=clear_combinations).grid(row=5, column=1, padx=10, pady=10)

    def finish_and_calculate():
        def update_color(deal):
            pass

        global bankroll, good_deals
        output_text.delete("1.0", tk.END)
        if records:
            for i, j in combinations(range(len(records)), 2):
                m1 = records[i]
                m2 = records[j]
                result = evaluate_parlay_bet(m1["win_rate"], m1["odds"], m2["win_rate"], m2["odds"], bankroll)
                if result["EV"] > 1:
                    good_deals.append({
                        "match1": m1["match"],
                        "match1_selected": m1["selected_team"],
                        "match2": m2["match"],
                        "match2_selected": m2["selected_team"],
                        "EV": result["EV"],
                        "Kelly": result["Kelly"],
                        "Bet": result["Bet"]
                    })

                output_text.delete("1.0", tk.END)
                output_text.insert(tk.END, "===== Good Deals (EV > 1.0) =====\n", "bg")

            output_text.tag_configure("team1", background="lightblue")
            output_text.tag_configure("team2", background="lightgreen")
            good_deals = sorted(good_deals, key=lambda x: x['Bet'], reverse=True)

            for deal in good_deals:
                #update_color(deal)

                output_text.insert(tk.END, f"🔁 Good Deal Combs:\n", "title_bg")
                output_text.insert(tk.END, f"{deal['match1']}\n", "team1_bg")
                output_text.insert(tk.END, f"Selected team: {deal['match1_selected']}\n", "team1_bg")
                output_text.insert(tk.END, f"{deal['match2']}\n", "team2_bg")
                output_text.insert(tk.END, f"Selected team: {deal['match2_selected']}\n", "team2_bg")
                output_text.insert(tk.END, f"📈 EV: {deal['EV']:.3f}, 📉 Kelly: {deal['Kelly']*100:.2f}%, 💵 Bet: ${deal['Bet']:.2f}\n", "result_bg")
                output_text.insert(tk.END, "=================================\n", "bg")

        input_win.destroy()

    ttk.Button(input_win, text="Finish", command=finish_and_calculate).grid(row=7, column=0, columnspan=2, pady=20)

def open_recorder_window():
    global good_deals

    if not good_deals:
        messagebox.showwarning("Error","No combinations found. Please run 'Set up Combinations' first.")
        return

    recorder_win = tk.Toplevel(root)
    recorder_win.title("Select Winning Combinations")
    recorder_win.geometry("1100x800")

    x = root.winfo_x() + root.winfo_width() + 10
    y = root.winfo_y()
    recorder_win.geometry(f"+{x}+{y}")

# GUI setup
root = tk.Tk()
root.title("NBA Parlay Analyzer")
root.geometry("1350x800")

# Open input window button
popup_button = ttk.Button(root, text="Set up Combinations", command=open_input_window)
popup_button.grid(row=0, column=0, padx=10, pady=10)

recorder_button = ttk.Button(root, text="Calculate Records", command=open_recorder_window)
recorder_button.grid(row=0, column=1, padx=10, pady=10)

# Output Text
output_text = tk.Text(root, height=20, width=80)
output_text.grid(row=1, column=0, columnspan=6, padx=10, pady=10)
output_text.tag_configure("title_bg", background="lightyellow")
output_text.tag_configure("team1_bg", background="lightblue")
output_text.tag_configure("team2_bg", background="lightgreen")
output_text.tag_configure("result_bg", background="lightpink")
output_text.tag_configure("bg", background="lightgray")

root.mainloop()