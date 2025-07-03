import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
import webbrowser

# Main window
root = tk.Tk()
root.title("📰 Fake News Detector")
root.geometry("600x400")
root.config(bg="#1F1F1F")

# --- Colors ---
bg_color = "#1F1F1F"
text_color = "#E0E0E0"
entry_bg = "#2C2C2C"
entry_fg = "#FFFFFF"
button_font = ("Segoe UI", 10, "bold")

# --- Functions ---
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            input_text.delete("1.0", tk.END)
            input_text.insert(tk.END, text)

def analyze():
    headline = input_text.get("1.0", tk.END).strip()
    if not headline:
        messagebox.showwarning("Warning", "Please enter a headline or upload a file.")
        return

    params = {
        "q": headline,
        "key": "AIzaSyBryMskx_DgR5kuitDJk60nhNlsRYQNk9k",
        "cx": "734837c73550d4dba"
    }
    try:
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        response.raise_for_status()
        data = response.json()

        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, f"🔍 Results for: {headline}\n\n")

        if "items" in data:
            for item in data["items"]:
                result_text.insert(tk.END, f"🔗 Title: {item['title']}\n")
                result_text.insert(tk.END, f"📄 Snippet: {item['snippet']}\n")
                result_text.insert(tk.END, f"🌐 Link: {item['link']}\n\n")
        else:
            result_text.insert(tk.END, "No results found.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def clear_text():
    input_text.delete("1.0", tk.END)
    result_text.delete("1.0", tk.END)

def open_link():
    webbrowser.open("https://news.google.com")

# --- Widgets ---

input_label = tk.Label(root, text="📝 Enter Headline / News Article:", fg=text_color, bg=bg_color, font=("Segoe UI", 11, "bold"))
input_label.pack(pady=(10, 2))

input_text = scrolledtext.ScrolledText(root, height=4, bg=entry_bg, fg=entry_fg, insertbackground=entry_fg, font=("Segoe UI", 10))
input_text.pack(fill="x", padx=10)

button_frame = tk.Frame(root, bg=bg_color)
button_frame.pack(pady=10)

select_button = tk.Button(button_frame, text="📁 Upload File", bg="#6A5ACD", fg="white", font=button_font, command=select_file)
select_button.grid(row=0, column=0, padx=5)

analyze_button = tk.Button(button_frame, text="🔎 Analyze", bg="#4CAF50", fg="white", font=button_font, command=analyze)
analyze_button.grid(row=0, column=1, padx=5)

clear_button = tk.Button(button_frame, text="🗑️ Clear", bg="#DC3545", fg="white", font=button_font, command=clear_text)
clear_button.grid(row=0, column=2, padx=5)

open_button = tk.Button(button_frame, text="🌐 Open News", bg="#FF8C00", fg="white", font=button_font, command=open_link)
open_button.grid(row=0, column=3, padx=5)

result_label = tk.Label(root, text="📋 Results:", fg=text_color, bg=bg_color, font=("Segoe UI", 11, "bold"))
result_label.pack(pady=(10, 2))

result_text = scrolledtext.ScrolledText(root, height=10, bg=entry_bg, fg=entry_fg, insertbackground=entry_fg, font=("Segoe UI", 10))
result_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

root.mainloop()
