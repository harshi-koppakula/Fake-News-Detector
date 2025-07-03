import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Sample dataset
fake_news_samples = [
    ("The sky is green and aliens live there.", "fake"),
    ("Vaccines have been proven safe by multiple studies.", "real"),
    ("Government confirms the moon landing was fake.", "fake"),
    ("Scientists developed a new renewable energy source.", "real"),
    ("Celebrity endorses miracle cure for cancer.", "fake"),
    ("New technology improves battery life by 50%.", "real"),
    ("Fake news site reports political conspiracy without evidence.", "fake"),
    ("Research confirms benefits of exercise on mental health.", "real"),
]

texts = [text for text, label in fake_news_samples]
labels = [1 if label == "fake" else 0 for text, label in fake_news_samples]

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words='english', max_df=0.85)),
    ('clf', LogisticRegression(solver='lbfgs'))
])

pipeline.fit(texts, labels)

def predict_article(text):
    proba = pipeline.predict_proba([text])[0]
    pred = pipeline.predict([text])[0]
    confidence = proba[pred]
    label = "Fake News" if pred == 1 else "Real News"
    return label, confidence

def predict_multiple(texts):
    probas = pipeline.predict_proba(texts)
    preds = pipeline.predict(texts)
    results = []
    for pred, proba in zip(preds, probas):
        label = "Fake News" if pred == 1 else "Real News"
        confidence = proba[pred]
        results.append((label, confidence))
    return results

class FakeNewsDetectorApp(tk.Tk):
    TOAST_DURATION_MS = 2500

    def __init__(self):
        super().__init__()
        self.title("Fake News Detector")
        self.geometry("800x600")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self._set_style()
        self.create_widgets()
        self.current_theme = "light"  # Start with light theme
        self.toast = None  # for tracking toast popup

    def _set_style(self):
        # Colors for light and dark themes
        self.light_colors = {
            "bg": "#F9FAFB",
            "fg": "#1F1F1F",
            "select_button": "#3B82F6",
            "select_hover": "#2563EB",
            "upload_button": "#279BFF",     # Spark blue shade
            "upload_hover": "#1D71D0",
            "run_button": "#F59E0B",        # Keep original orange for Run
            "run_hover": "#D97706",
            "clear_button": "#EF4444",      # Keep original red for Clear
            "clear_hover": "#DC2626",
            "entry_bg": "#FFFFFF",
            "entry_fg": "#1F1F1F",
            "tree_bg": "#FFFFFF",
            "tree_fg": "#1F1F1F",
            "tree_alt": "#F3F4F6",
            "status_bg": "#ECECEC",
            "status_fg": "#4B5563",
        }

        self.dark_colors = {
            "bg": "#1E1E1E",
            "fg": "#D4D4D4",
            "select_button": "#4AAE9B",  # Mermaid green shade
            "select_hover": "#357E73",
            "upload_button": "#10B981",
            "upload_hover": "#059669",
            "run_button": "#F59E0B",       # Keep original orange for Run
            "run_hover": "#D97706",
            "clear_button": "#EF4444",     # Keep original red for Clear
            "clear_hover": "#DC2626",
            "entry_bg": "#2D2D2D",
            "entry_fg": "#D4D4D4",
            "tree_bg": "#252526",
            "tree_fg": "#D4D4D4",
            "tree_alt": "#2A2A2A",
            "status_bg": "#181818",
            "status_fg": "#A3A3A3",
        }

        self.apply_theme(self.light_colors)  # Start with light theme

    def apply_theme(self, colors):
        self.colors = colors

        self.configure(bg=colors["bg"])
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["fg"], font=("Segoe UI", 9))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground=colors["fg"])

        for style, bg, hover in [
            ("Select.TButton", colors["select_button"], colors["select_hover"]),
            ("Upload.TButton", colors["upload_button"], colors["upload_hover"]),
            ("Run.TButton", self.light_colors["run_button"], self.light_colors["run_hover"]),  # Keep fixed orange both themes
            ("Clear.TButton", self.light_colors["clear_button"], self.light_colors["clear_hover"]),
        ]:
            self.style.configure(style,
                                 font=("Segoe UI", 9, "bold"),
                                 foreground="white",
                                 background=bg,
                                 borderwidth=1,
                                 padding=(6, 4),
                                 relief="flat")
            self.style.map(style,
                           background=[('active', hover), ('disabled', '#6B7280')],
                           relief=[('pressed', 'sunken')])

        self.style.configure("TEntry",
                             font=("Segoe UI", 9),
                             fieldbackground=colors["entry_bg"],
                             foreground=colors["entry_fg"],
                             padding=6,
                             borderwidth=1,
                             relief="solid")

        self.style.configure("TFrame", background=colors["bg"])

        self.style.configure("Treeview",
                             background=colors["tree_bg"],
                             foreground=colors["tree_fg"],
                             fieldbackground=colors["tree_bg"],
                             font=("Segoe UI", 9),
                             borderwidth=0)
        self.style.map("Treeview",
                       background=[("selected", colors["select_button"])],
                       foreground=[("selected", "#FFFFFF")])
        self.style.configure("Treeview.Row", background=colors["tree_alt"])

        self.style.configure("Status.TLabel",
                             background=colors["status_bg"],
                             foreground=colors["status_fg"],
                             font=("Segoe UI", 8),
                             relief="sunken",
                             padding=4)

        self.configure(bg=colors["bg"])

        # Update widget colors if already created
        if hasattr(self, 'csv_file_label'):
            fg_color = self.light_colors["fg"] if self.current_theme == "light" else self.dark_colors["fg"]
            self.csv_file_label.configure(foreground=fg_color)

        if hasattr(self, 'tree'):
            alt_bg = colors["tree_alt"]
            self.tree.tag_configure("evenrow", background=alt_bg)

        # Toggle button color: black on light, white on dark, transparent bg
        if hasattr(self, 'theme_button'):
            fg = "#000000" if self.current_theme == "light" else "#FFFFFF"
            bg = colors["bg"]
            self.theme_button.configure(
                bg=bg,
                fg=fg,
                activebackground=bg,
                activeforeground=fg,
                relief="flat",
                borderwidth=0,
                highlightthickness=0,
                font=("Segoe UI", 12, "bold"),
                cursor="hand2"
            )

    def create_widgets(self):
        main_container = ttk.Frame(self, style="TFrame", borderwidth=0)
        main_container.pack(fill="both", expand=True, padx=8, pady=8)

        header = ttk.Label(main_container, text="Fake News Detector", style="Header.TLabel")
        header.pack(pady=(10, 8))

        self.main_frame = ttk.Frame(main_container, style="TFrame")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=2)

        # Theme toggle button with transparent background and black/white text
        self.theme_button = tk.Button(
            self.main_frame,
            text="☀",
            command=self.toggle_theme,
            width=3,
            height=1,
            bg=self.light_colors["bg"],
            fg="#000000",
            activebackground=self.light_colors["bg"],
            activeforeground="#000000",
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 12, "bold"),
            cursor="hand2"
        )
        self.theme_button.grid(row=0, column=1, sticky="ne", padx=(0, 5), pady=(5, 0))

        left_panel = ttk.Frame(self.main_frame, style="TFrame")
        left_panel.grid(row=1, column=0, sticky="nswe", padx=(0, 8))

        csv_label = ttk.Label(left_panel, text="Upload CSV file (.csv):")
        csv_label.pack(anchor="w", pady=(0, 4))

        # Upload CSV button with blue shades (spark blue)
        csv_button = ttk.Button(
            left_panel,
            text="📁 Select CSV",
            command=self.load_csv_file,
            style="Upload.TButton",
            compound="left",
            width=18
        )
        csv_button.pack(fill="x", pady=(0, 8))

        self.csv_file_label = ttk.Label(left_panel, text="No file selected", foreground=self.light_colors["fg"])
        self.csv_file_label.pack(anchor="w", pady=(0, 8))

        single_label = ttk.Label(left_panel, text="Enter article headline:")
        single_label.pack(anchor="w", pady=(4, 4))

        self.text_input = ttk.Entry(left_panel, font=("Segoe UI", 9), width=25)
        self.text_input.pack(fill="x", pady=(0, 8))

        # Upload Text button (light green)
        txt_upload_button = ttk.Button(
            left_panel,
            text="📄 Upload Text (.txt)",
            command=self.load_text_file,
            style="Upload.TButton",
            compound="left",
            width=18
        )
        txt_upload_button.pack(fill="x", pady=(0, 8))

        buttons_frame = ttk.Frame(left_panel, style="TFrame")
        buttons_frame.pack(fill="x", pady=(4, 0))

        run_btn = ttk.Button(
            buttons_frame,
            text="▶ Run",
            command=self.run_detection,
            style="Run.TButton",
            compound="left",
        )
        run_btn.pack(side="left", fill="both", expand=True, padx=(0, 4))

        clear_btn = ttk.Button(
            buttons_frame,
            text="✖ Clear",
            command=self.clear_all,
            style="Clear.TButton",
            compound="left",
        )
        clear_btn.pack(side="left", fill="both", expand=True, padx=(4, 0))

        right_panel = ttk.Frame(self.main_frame, style="TFrame")
        right_panel.grid(row=1, column=1, sticky="nswe")

        results_label = ttk.Label(right_panel, text="Detection Results:")
        results_label.pack(anchor="w", pady=(0, 4))

        columns = ("Article Snippet", "Prediction", "Confidence")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w", width=150 if col == "Article Snippet" else 90)
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("evenrow", background=self.light_colors["tree_alt"])

        self.status_var = tk.StringVar(value="")
        # Moved status bar right below buttons & results (inside main_frame for exact positioning)
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, style="Status.TLabel", anchor="w")
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="we", padx=8, pady=(2, 10))

        self.csv_data = None

    def _show_toast(self, message, bg_color):
        if self.toast and self.toast.winfo_exists():
            self.toast.destroy()
        self.toast = tk.Toplevel(self)
        self.toast.overrideredirect(True)
        self.toast.attributes("-topmost", True)
        self.toast.configure(bg=bg_color, padx=10, pady=5)
        label = tk.Label(self.toast, text=message, bg=bg_color, fg="white", font=("Segoe UI", 10, "bold"))
        label.pack()
        self.update_idletasks()
        main_x = self.winfo_rootx()
        main_y = self.winfo_rooty()
        main_width = self.winfo_width()
        x = main_x + main_width - self.toast.winfo_reqwidth() - 20
        y = main_y + 20
        self.toast.geometry(f"+{x}+{y}")
        self.toast.after(self.TOAST_DURATION_MS, self.toast.destroy)

    def toggle_theme(self):
        if self.current_theme == "light":
            self.apply_theme(self.dark_colors)
            self.current_theme = "dark"
            self.theme_button.config(text="☾")  # Moon icon
            self.theme_button.config(bg=self.dark_colors["bg"], fg="white", activebackground=self.dark_colors["bg"], activeforeground="white")
            self.csv_file_label.configure(foreground=self.dark_colors["fg"])
            self.tree.tag_configure("evenrow", background=self.dark_colors["tree_alt"])
            self._show_toast("Dark theme activated.", bg_color="#444444")
        else:
            self.apply_theme(self.light_colors)
            self.current_theme = "light"
            self.theme_button.config(text="☀")  # Sun icon
            self.theme_button.config(bg=self.light_colors["bg"], fg="black", activebackground=self.light_colors["bg"], activeforeground="black")
            self.csv_file_label.configure(foreground=self.light_colors["fg"])
            self.tree.tag_configure("evenrow", background=self.light_colors["tree_alt"])
            self._show_toast("Light theme activated.", bg_color="#888888")

    def load_csv_file(self):
        filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(title="Select CSV File", filetypes=filetypes)
        if filepath:
            fg_color = self.light_colors["fg"] if self.current_theme == "light" else self.dark_colors["fg"]
            self.csv_file_label.configure(text=os.path.basename(filepath), foreground=fg_color)
            try:
                data = pd.read_csv(filepath)
                if 'article' not in [col.lower() for col in data.columns]:
                    messagebox.showerror("Error", "CSV must contain an 'article' column.")
                    self.csv_data = None
                    self.csv_file_label.configure(text="No file selected", foreground=fg_color)
                    return
                col_map = {col.lower(): col for col in data.columns}
                article_col = col_map['article']
                self.csv_data = data[[article_col]].copy()
                self.csv_data.rename(columns={article_col: 'article'}, inplace=True)
                self.status_var.set(f"Loaded CSV with {len(self.csv_data)} articles.")
                self.clear_results()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV file: {e}")
                self.csv_data = None
                self.csv_file_label.configure(text="No file selected", foreground=fg_color)

    def load_text_file(self):
        filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(title="Select Text File", filetypes=filetypes)
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_input.delete(0, tk.END)
                self.text_input.insert(tk.END, content)
                self.status_var.set(f"Loaded article text from {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read text file: {e}")

    def run_detection(self):
        self.clear_results()
        text = self.text_input.get().strip()
        if self.csv_data and len(self.csv_data) > 0:
            self.status_var.set("Running fake news detection on CSV articles...")
            threading.Thread(target=self._run_csv_detection_thread, daemon=True).start()
        elif text:
            self.status_var.set("Running fake news detection on input article...")
            threading.Thread(target=self._run_single_detection_thread, args=(text,), daemon=True).start()
        else:
            messagebox.showinfo("Info", "Please upload a CSV file or enter article text to analyze.")

    def _run_single_detection_thread(self, text):
        try:
            label, confidence = predict_article(text)
            snippet = (text[:120] + "...") if len(text) > 120 else text
            tag = "evenrow" if len(self.tree.get_children()) % 2 == 0 else ""
            self.tree.insert('', 'end', values=(snippet, label, f"{confidence*100:.2f}%"), tags=(tag,))
            self.status_var.set("Detection completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Detection failed: {e}")
            self.status_var.set("Error occurred.")

    def _run_csv_detection_thread(self):
        try:
            texts = self.csv_data['article'].tolist()
            results = predict_multiple(texts)
            for idx, (txt, (label, confidence)) in enumerate(zip(texts, results)):
                snippet = (txt[:120] + "...") if len(txt) > 120 else txt
                tag = "evenrow" if idx % 2 == 0 else ""
                self.tree.insert('', 'end', values=(snippet, label, f"{confidence*100:.2f}%"), tags=(tag,))
            self.status_var.set(f"Detection completed for {len(texts)} articles.")
        except Exception as e:
            messagebox.showerror("Error", f"Detection failed: {e}")
            self.status_var.set("Error occurred.")

    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_var.set("Ready")

    def clear_all(self):
        self.text_input.delete(0, tk.END)
        self.csv_data = None
        fg_color = self.light_colors["fg"] if self.current_theme == "light" else self.dark_colors["fg"]
        self.csv_file_label.configure(text="No file selected", foreground=fg_color)
        self.clear_results()
        self.status_var.set("Inputs and results cleared.")

if __name__ == "__main__":
    app = FakeNewsDetectorApp()
    app.mainloop()
