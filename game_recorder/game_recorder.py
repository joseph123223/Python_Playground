import tkinter as tk
import os, json
from tkinter import Toplevel, Label, Button, StringVar, Entry, Checkbutton
from tkinter import ttk
import tkinter.font as tkFont
from dataclasses import dataclass, asdict, fields
from typing import List
from datetime import datetime

###  -----  Data Class  -----
@dataclass
class GameRecord:
    id: int
    date: str
    home: str
    away: str
    home_scores: List[int]
    away_scores: List[int]
    home_total_scores: int
    away_total_scores: int
    total_score: int
    winning_team: str
    is_overtime: bool
    winning_side: str

### -----  Global Varients  -----
teams = [
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets",
    "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets",
    "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers",
    "LA Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat",
    "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks",
    "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns",
    "Portland Trail Blazers", "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors",
    "Utah Jazz", "Washington Wizards"
]
records = []
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR, "nba_records.json")
sort_states = {
    "id": True, "date": True, "home": True, "away": True,
    "home_total_scores": True, "away_total_scores": True,
    "total_score": True, "winning_team": True
}


### -----  Functions  -----

## Save records
def save_records_to_file():
    with open(SAVE_FILE, 'w', encoding="utf-8") as f:
        json.dump([asdict(r) for r in records], f, indent=2)

## Load records
def load_records_from_file(tree):
    if not os.path.exists(SAVE_FILE):
        return

    with open(SAVE_FILE, 'r', encoding="utf-8") as f:
        loaded = json.load(f)

    records.clear()
    records.extend(GameRecord(**r) for r in loaded)
    refresh_treeview(tree)

## Sort by Tab
def sort_by_column(tree, column):
    reverse = sort_states.get(column, True)

    if column == "id":
        records.sort(key=lambda r: r.id, reverse=not reverse)
    elif column == "date":
        records.sort(key=lambda r: r.date, reverse=not reverse)
    elif column in ["home", "away", "winning_team"]:
        records.sort(key=lambda r: getattr(r, column).lower(), reverse=not reverse)
    elif column in ["home_total_scores", "away_total_scores", "total_score"]:
        records.sort(key=lambda r: getattr(r, column), reverse=not reverse)

    sort_states[column] = not reverse
    refresh_treeview(tree)

## Refresh the tree
def refresh_treeview(tree):
    for row in tree.get_children():
        tree.delete(row)

    for i, record in enumerate(records):
        #record.id = i + 1
        tree.insert("", "end", values=(
            record.id,
            record.date,
            record.home,
            record.away,
            record.home_total_scores,
            record.away_total_scores,
            record.total_score,
            record.winning_team
        ))
    update_summary_stats()
    adjust_column_width(tree)

## Adjust width of table
def adjust_column_width(tree):
    font = tkFont.Font()
    for col in tree["columns"]:
        header_width = font.measure(tree.heading(col)["text"])
        max_item_width = max((font.measure(str(tree.set(row, col))) for row in tree.get_children()), default=0)
        final_width = max(header_width, max_item_width) + 20
        tree.column(col, width=final_width)

## Delete a row of data
def delete_selected_record(tree):
    selected = tree.selection()
    if not selected:
        show_custom_warning("Error - Delete", "Please select a data to delete.")
        return

    for item in selected:
        values = tree.item(item, "values")
        record_id = int(values[0])
        records[:] = [r for r in records if r.id != record_id]

    refresh_treeview(tree)

## Calculate summary
def get_team_records_summary(records, teams):
    team_records = {team: {"W": 0, "L": 0, "T": 0} for team in teams}
    for r in records:
        if r.winning_team != "Tied":
            team_records[r.winning_team]["W"] += 1
        else:
            team_records[r.home]["T"] += 1
            team_records[r.away]["T"] += 1

        ## Check the lose team
        if r.winning_team == r.home:
            team_records[r.away]["L"] += 1
        elif r.winning_team == r.away:
            team_records[r.home]["L"] += 1

    sorted_team_records = sorted(team_records.items(), key=lambda item: (-item[1]["W"], item[1]["L"]))
    return sorted_team_records

## Display summary stats
def update_summary_stats():
    global home_avg_label, away_avg_label, total_avg_label, record_text

    record_text.config(state="normal")
    if not records:
        home_avg_label.config(text="Home Avg: Empty")
        away_avg_label.config(text="Away Avg: Empty")
        total_avg_label.config(text="Total Avg: Empty")
        record_text.delete(1.0, tk.END)
        record_text.insert(tk.END, "Record Summary: Empty", "spacing")
        record_text.config(state="disabled")
        return

    total_home = sum(r.home_total_scores for r in records)
    total_away = sum(r.away_total_scores for r in records)
    total_score = sum(r.total_score for r in records)
    num_games = len(records)

    avg_home = total_home / num_games
    avg_away = total_away / num_games
    avg_total = total_score / num_games

    home_avg_label.config(text=f"Home Avg: {avg_home:.2f}")
    away_avg_label.config(text=f"Away Avg: {avg_away:.2f}")
    total_avg_label.config(text=f"Total Avg: {avg_total:.2f}")

    result = ""
    sorted_team_records = get_team_records_summary(records, teams)

    for team, rec in sorted_team_records:
        if rec["W"] > 0 or rec["L"] > 0:
            result += f"{team}: {rec['W']}W - {rec['L']}L\n"

    record_text.delete(1.0, tk.END)
    record_text.insert(tk.END, result, "spacing")
    record_text.config(state="disabled")

## Display details
def open_stat_window(records):
    stat_win = Toplevel()
    stat_win.title("Team Statistics")

    w, h = 1000, 800
    screen_width = stat_win.winfo_screenwidth()
    screen_height = stat_win.winfo_screenheight()
    x = (screen_width // 4) - (w // 2)
    y = (screen_height // 2) - (h // 2)
    stat_win.geometry(f"{w}x{h}+{x}+{y}")

    Label(stat_win, text="Team Name:").pack(pady=5)
    team_var = StringVar()
    team_combo = ttk.Combobox(stat_win, textvariable=team_var, values=teams, state="readonly")
    team_combo.pack()

    home_var = tk.BooleanVar(value=True)
    away_var = tk.BooleanVar(value=True)
    Checkbutton(stat_win, text="Home", variable=home_var).pack()
    Checkbutton(stat_win, text="Away", variable=away_var).pack()

    result_text = tk.Text(stat_win, height=15, width=60)
    result_text.pack(pady=10)

    def calculate_stats():
        team = team_var.get().strip()
        if not team:
            show_custom_warning("Missing", "Please enter a team name.")
            return

        result_text.delete(1.0, tk.END)

        home_data = []
        away_data = []
        for r in records:
            if home_var.get() and r.home == team:
                home_data.append(r)
            if away_var.get() and r.away == team:
                away_data.append(r)

        if not home_data and not away_data:
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "No records found for this team.\n")
            return

        total_home_games = len(home_data)
        total_away_games = len(away_data)
        home_total_team_points, away_total_team_points = 0, 0
        home_total_opponent_points, away_total_opponent_points = 0, 0
        home_quarter_sums, away_quarter_sums = [], []
        home_quarter_counts, away_quarter_counts = [], []

        for r in home_data:
            team_scores = r.home_scores
            opp_scores = r.away_scores
            home_total_team_points += sum(team_scores)
            home_total_opponent_points += sum(opp_scores)

            for i in range(len(team_scores)):
                if i >= len(home_quarter_sums):
                    home_quarter_sums.append(0)
                    home_quarter_counts.append(0)
                home_quarter_sums[i] += team_scores[i]
                home_quarter_counts[i] += 1

        for r in away_data:
            team_scores = r.away_scores
            opp_scores = r.home_scores
            away_total_team_points += sum(team_scores)
            away_total_opponent_points += sum(opp_scores)

            for i in range(len(team_scores)):
                if i >= len(away_quarter_sums):
                    away_quarter_sums.append(0)
                    away_quarter_counts.append(0)
                away_quarter_sums[i] += team_scores[i]
                away_quarter_counts[i] += 1

        if home_data:
            home_avg_team_score = home_total_team_points / total_home_games
            home_avg_opp_score = home_total_opponent_points / total_home_games
            home_avg_quarter_scores = [round(q / c, 2) if c > 0 else 0 for q, c in zip(home_quarter_sums, home_quarter_counts)]

        if away_data:
            away_avg_team_score = away_total_team_points / total_away_games
            away_avg_opp_score = away_total_opponent_points / total_away_games
            away_avg_quarter_scores = [round(q / c, 2) if c > 0 else 0 for q, c in zip(away_quarter_sums, away_quarter_counts)]

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Total Games: {total_home_games + total_away_games}\n")
        result_text.insert(tk.END, "==="*12 + '\n')
        result_text.insert(tk.END, f"Home Statistic:\n")
        result_text.insert(tk.END, "---"*12 + '\n')

        if total_home_games > 0:
            result_text.insert(tk.END, f"Avg Points by {team}: {home_avg_team_score:.2f}\n")
            result_text.insert(tk.END, f"Avg Points by Opponent: {home_avg_opp_score:.2f}\n\n")
            result_text.insert(tk.END, "Avg points by quarter:\n")
            for i, val in enumerate(home_avg_quarter_scores):
                if i < 4:
                    label = f"Q{i+1}"f"OT{i-3}"
                    result_text.insert(tk.END, f"  {label}: {val}\n")
        else:
            result_text.insert(tk.END, f"No home record so far\n")

        result_text.insert(tk.END, "==="*12 + '\n')
        result_text.insert(tk.END, f"Away Statistic:\n")
        result_text.insert(tk.END, "---"*12 + '\n')

        if total_away_games > 0:
            result_text.insert(tk.END, f"Avg Points by {team}: {away_avg_team_score:.2f}\n")
            result_text.insert(tk.END, f"Avg Points by Opponent: {away_avg_opp_score:.2f}\n\n")
            result_text.insert(tk.END, "Avg points by quarter:\n")
            for i, val in enumerate(away_avg_quarter_scores):
                label = f"Q{i+1}" if i < 4 else f"OT{i-3}\n"
                result_text.insert(tk.END, f"  {label}: {val}\n")
        else:
            result_text.insert(tk.END, f"No away record so far\n")

    Button(stat_win, text="Show Stats", command=calculate_stats).pack(pady=5)

## Custom warning window
def show_custom_warning(title, message):
    warn = Toplevel()
    warn.title(title)
    warn.geometry("900x200")

    Label(warn, text=message, fg="red", font=("Arial", 12)).pack(pady=20)
    Button(warn, text="OK", command=warn.destroy).pack(pady=10)

## Add window
def open_add_window(tree):
    add_win = Toplevel()
    add_win.title("Add record")

    win_width, win_height = 1000, 600
    screen_width = add_win.winfo_screenwidth()
    screen_height = add_win.winfo_screenheight()
    x = (screen_width // 4) - (win_width // 2)
    y = (screen_height // 2) - (win_height // 2)
    add_win.geometry(f"{win_width}x{win_height}+{x}+{y}")

    Label(add_win, text="Date (YYYY-MM-DD):").pack(pady=5)
    date_entry = Entry(add_win)
    date_entry.pack()

    Label(add_win, text="Home team:").pack(pady=5)
    home_team_var = StringVar()
    home_team_combo = ttk.Combobox(add_win, textvariable=home_team_var, values=teams, state="readonly")
    home_team_combo.pack()

    Label(add_win, text="Away team:").pack(pady=5)
    away_team_var = StringVar()
    away_team_combo = ttk.Combobox(add_win, textvariable=away_team_var, values=teams, state="readonly")
    away_team_combo.pack()

    Label(add_win, text="Home team's score").pack(pady=5)
    home_scores_entry = Entry(add_win)
    home_scores_entry.pack()

    Label(add_win, text="Away team's score").pack(pady=5)
    away_scores_entry = Entry(add_win)
    away_scores_entry.pack()

    def save_record():
        game_id = len(records) + 1
        date = date_entry.get().strip()
        home_team = home_team_var.get()
        away_team = away_team_var.get()
        home_scores_raw = home_scores_entry.get()
        away_scores_raw = away_scores_entry.get()

        if not date:
            show_custom_warning("Error - Date", "Please enter the game's date. Ex: 2025-04-23")
            return
        if not home_team or not away_team:
            show_custom_warning("Error - Empty", "Please select Home and Away team.")
            return
        if home_team == away_team:
            show_custom_warning("Error - Same", "Home and Away team couldn't be same.")
            return

        try:
            home_scores = [int(s.strip()) for s in home_scores_raw.split(",")]
            away_scores = [int(s.strip()) for s in away_scores_raw.split(",")]
        except ValueError:
            show_custom_warning("Error - Format", "Please confirm the format.(ex: 14, 30, 31, 25)")
            return

        if len(home_scores) < 4:
            show_custom_warning("Error - Quarters", "Please enter at least four quarters of score for Home team.")
            return
        if len(away_scores) < 4:
            show_custom_warning("Error - Quarters", "Please enter at least four quarters of score for Away team.")
            return
        if len(home_scores) != len(away_scores):
            show_custom_warning("Error - Quarters", "Please enter the same amount of quarters for two teams.")
            return

        total_home = sum(home_scores)
        total_away = sum(away_scores)
        total_score = total_home + total_away

        if total_home > total_away:
            winning_team = home_team
            winning_side = "Home"
        elif total_away > total_home:
            winning_team = away_team
            winning_side = "Away"
        else:
            winning_team = 'Tied'
            winning_side = "Tied"

        is_overtime = len(home_scores) > 4

        record = GameRecord(
            id=game_id,
            date=date,
            home=home_team,
            away=away_team,
            home_scores=home_scores,
            away_scores=away_scores,
            home_total_scores=total_home,
            away_total_scores=total_away,
            total_score=total_score,
            winning_team=winning_team,
            is_overtime=is_overtime,
            winning_side=winning_side
        )
        records.append(record)

        refresh_treeview(tree)
        add_win.destroy()

    Button(add_win, text="Save", command=save_record).pack(pady=20)

## Main program
def main():
    global home_avg_label, away_avg_label, total_avg_label, record_text

    window = tk.Tk()
    window.title("NBA Recorder")
    window.geometry("2600x1400")

    win_width, win_height = 2200, 1200
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 4) - (win_width // 2)
    y = (screen_height // 2) - (win_height // 2)
    window.geometry(f"{win_width}x{win_height}+{x}+{y}")

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
    style.configure("Treeview", font=("Arial", 11), rowheight=30)

    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    add_button = tk.Button(button_frame, text="Add", font=("Arial", 14))
    add_button.grid(row=0, column=0, padx=15)

    save_button = tk.Button(button_frame, text="Save", font=("Arial", 14), command=save_records_to_file)
    save_button.grid(row=0, column=1, padx=15)

    load_button = tk.Button(button_frame, text="Load", font=("Arial", 14), command=lambda: load_records_from_file(tree))
    load_button.grid(row=0, column=2, padx=15)

    delete_button = tk.Button(button_frame, text="Delete", font=("Arial", 14), command=lambda: delete_selected_record(tree))
    delete_button.grid(row=0, column=3, padx=15)

    stats_button = tk.Button(button_frame, text="Statistic", font=("Arial", 14), command=lambda: open_stat_window(records))
    stats_button.grid(row=0, column=4, padx=15)

    columns = ("id", "date", "home", "away", "home_score", "away_score", "total", "winner")
    tree = ttk.Treeview(window, columns=columns, show="headings", height=20)

    tree.heading("id", text="ID", command=lambda: sort_by_column(tree, "id"))
    tree.heading("date", text="Date", command=lambda: sort_by_column(tree, "date"))
    tree.heading("home", text="Home Team", command=lambda: sort_by_column(tree, "home"))
    tree.heading("away", text="Away Team", command=lambda: sort_by_column(tree, "away"))
    tree.heading("home_score", text="Home Total", command=lambda: sort_by_column(tree, "home_total_scores"))
    tree.heading("away_score", text="Away Total", command=lambda: sort_by_column(tree, "away_total_scores"))
    tree.heading("total", text="Total Score", command=lambda: sort_by_column(tree, "total_score"))
    tree.heading("winner", text="Winner", command=lambda: sort_by_column(tree, "winning_team"))

    tree.column("id", width=50, anchor="center")
    tree.column("date", width=120, anchor="center")
    tree.column("home", width=250, anchor="center", stretch=True)
    tree.column("away", width=250, anchor="center", stretch=True)
    tree.column("home_score", width=50, anchor="center")
    tree.column("away_score", width=50, anchor="center")
    tree.column("total", width=50, anchor="center")
    tree.column("winner", width=250, anchor="center", stretch=True)

    tree.pack(pady=10, fill="x")

    add_button.config(command=lambda: open_add_window(tree))

    # Main stats section

    stats_frame = tk.Frame(window, bg="#dddddd")
    stats_frame.pack(fill="both", expand=True)

    home_avg_label = Label(stats_frame, text="Home Avg: Empty", font=("Arial", 12), bg="#dddddd")
    home_avg_label.pack(anchor="w", padx=20, pady=2)

    away_avg_label = Label(stats_frame, text="Away Avg: Empty", font=("Arial", 12), bg="#dddddd")
    away_avg_label.pack(anchor="w", padx=20, pady=2)

    total_avg_label = Label(stats_frame, text="Total Avg: Empty", font=("Arial", 12), bg="#dddddd")
    total_avg_label.pack(anchor="w", padx=20, pady=2)

    record_text_frame = tk.Frame(stats_frame, bg="#dddddd")
    record_text_frame.pack(fill="both", expand=True, padx=20, pady=5)

    record_text_scrollbar = tk.Scrollbar(record_text_frame)
    record_text_scrollbar.pack(side="right", fill="y")
    record_text = tk.Text(record_text_frame, height=10, font=("Arial", 12), bg="#eeeeee", wrap="word", yscrollcommand=record_text_scrollbar.set, state="disabled")
    record_text.pack(side="left", fill="both", expand=True)
    record_text_scrollbar.config(command=record_text.yview)
    record_text.tag_configure("spacing", spacing3=8)

    window.mainloop()

if __name__ == "__main__":
    main()