import requests
import tkinter as tk
from tkinter import messagebox
from transformers import pipeline

# -----------------------------
# Replace with your credentials
API_KEY = "AIzaSyBryMskx_DgR5kuitDJk60nhNlsRYQNk9k"
SEARCH_ENGINE_ID = "734837c73550d4dba"

# -----------------------------

# Load BART-MNLI model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Google Custom Search function
def search_web(headline, num_results=3):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": headline,
        "num": num_results
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return [item.get("snippet", "") for item in data.get("items", [])]
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Search Error", f"An error occurred: {str(e)}")
        return []

# Classification logic
def assess_headline(headline):
    snippets = search_web(headline)
    if not snippets:
        return "NO EVIDENCE FOUND", (0.0, 0.0)

    scores = {"real": 0.0, "fake": 0.0}
    for text in snippets:
        result = classifier(
            text,
            candidate_labels=["real", "fake"],
            hypothesis_template="This text supports that the news is {}."
        )
        label, score = result["labels"][0], result["scores"][0]
        scores[label] += score

    real = scores["real"]
    fake = scores["fake"]

    if real > fake + 1.0:
        verdict = "REAL"
    elif fake > real + 1.0:
        verdict = "FAKE"
    else:
        verdict = "UNCERTAIN"
    return verdict, (real, fake)

# Button action
def check_headline():
    headline = entry.get().strip()
    if not headline:
        messagebox.showwarning("Missing Input", "Please enter a headline.")
        return
    verdict, (r, f) = assess_headline(headline)
    result_label.config(text=f"Verdict: {verdict}\nSupport: {r:.2f}  Refute: {f:.2f}", fg="blue")

# GUI setup
def setup_gui():
    window = tk.Tk()
    window.title("Fake News Checker")
    window.geometry("500x300")
    window.resizable(False, False)
    window.configure(bg="#f0f0f0")

    tk.Label(window, text="Fake News Detector", font=("Helvetica", 16, "bold"), bg="#f0f0f0").pack(pady=15)
    tk.Label(window, text="Enter a news headline:", font=("Arial", 12), bg="#f0f0f0").pack()

    global entry
    entry = tk.Entry(window, width=60, font=("Arial", 10))
    entry.pack(pady=10)

    tk.Button(window, text="Check", command=check_headline, bg="#4CAF50", fg="white",
              font=("Arial", 10, "bold")).pack(pady=10)

    global result_label
    result_label = tk.Label(window, text="", font=("Arial", 12), bg="#f0f0f0", wraplength=460, justify="center")
    result_label.pack(pady=15)

    tk.Label(window, text="Powered by Google CSE & BART-MNLI", font=("Arial", 9), bg="#f0f0f0", fg="#777").pack(side="bottom", pady=10)

    return window

# Main execution
if __name__ == "__main__":
    try:
        app_window = setup_gui()
        app_window.mainloop()
    except Exception as e:
        messagebox.showerror("Application Error", f"An unexpected error occurred: {str(e)}")
