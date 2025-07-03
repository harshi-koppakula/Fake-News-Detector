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
    def __init__(self):
        super().__init__()
        self.title("Fake News Detector")
        self.geometry("800x600")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self._set_style()
        self.create_widgets()
        self.current_theme = "light"  # Start with light theme

    def _set_style(self):
        # Light color palette
        self.light_colors = {
            "bg": "#F9FAFB",
            "fg": "#1F1F1F",
            "select_button": "#3B82F6",
            "select_hover": "#2563EB",
            "upload_button": "#10B981",
            "upload_hover": "#059669",
            "run_button": "#F59E0B",
            "run_hover": "#D97706",
            "clear_button": "#EF4444",
            "clear_hover": "#DC2626",
            "entry_bg": "#FFFFFF",
            "entry_fg": "#1F1F1F",
            "tree_bg": "#FFFFFF",
            "tree_fg": "#1F1F1F",
            "tree_alt": "#F3F4F6",
            "status_bg": "#F3F4F6",
            "status_fg": "#6B7280",
        }

        # Dark color palette
        self.dark_colors = {
            "bg": "#1E1E1E",
            "fg": "#D4D4D4",
            "select_button": "#3B82F6",
            "select_hover": "#2563EB",
            "upload_button": "#10B981",
            "upload_hover": "#059669",
            "run_button": "#F59E0B",
            "run_hover": "#D97706",
            "clear_button": "#EF4444",
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
        self.colors = colors  # Save current colors for access in other methods

        self.style.configure("TLabel", background=colors["bg"], foreground=colors["fg"], font=("Segoe UI", 9))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground=colors["fg"])

        for style, btn_color, hover_color in [
            ("Select.TButton", colors["select_button"], colors["select_hover"]),
            ("Upload.TButton", colors["upload_button"], colors["upload_hover"]),
            ("Run.TButton", colors["run_button"], colors["run_hover"]),
            ("Clear.TButton", colors["clear_button"], colors["clear_hover"])
        ]:
            self.style.configure(style,
                                 font=("Segoe UI", 9, "bold"),
                                 foreground="white",
                                 background=btn_color,
                                 borderwidth=1,
                                 padding=(6, 4),
                                 relief="flat")
            self.style.map(style,
                           background=[('active', hover_color), ('disabled', '#6B7280')],
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
        self.style.map('Treeview',
                       background=[('selected', colors["select_button"])],
                       foreground=[('selected', "#FFFFFF")])
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
            fg_color = "#6B7280" if self.current_theme == "light" else "#A3A3A3"
            self.csv_file_label.configure(foreground=fg_color)

        if hasattr(self, 'tree'):
            alt_bg = colors["tree_alt"]
            self.tree.tag_configure("evenrow", background=alt_bg)

    def create_widgets(self):
        main_container = ttk.Frame(self, style="TFrame", borderwidth=0)
        main_container.pack(fill="both", expand=True, padx=8, pady=8)

        header = ttk.Label(main_container, text="Fake News Detector", style="Header.TLabel")
        header.pack(pady=(10, 8))

        main_frame = ttk.Frame(main_container, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)

        # Theme toggle button uses unicode sun and moon symbols
        self.theme_button = ttk.Button(
            main_frame,
            text="☀",  # Sun symbol represents light theme currently active, click to dark
            command=self.toggle_theme,
            width=3,
            style="Run.TButton"
        )
        self.theme_button.grid(row=0, column=1, sticky="ne", padx=(0, 5), pady=(5, 0))

        left_panel = ttk.Frame(main_frame, style="TFrame")
        left_panel.grid(row=1, column=0, sticky="nswe", padx=(0, 8))

        csv_label = ttk.Label(left_panel, text="Upload CSV file (.csv):")
        csv_label.pack(anchor="w", pady=(0, 4))

        # Buttons with Unicode icons
        # Select CSV button - folder icon 📁
        csv_button = ttk.Button(
            left_panel,
            text="📁 Select CSV",
            command=self.load_csv_file,
            style="Select.TButton",
            compound="left",
            width=18
        )
        csv_button.pack(fill="x", pady=(0, 8))

        self.csv_file_label = ttk.Label(left_panel, text="No file selected", foreground="#6B7280")
        self.csv_file_label.pack(anchor="w", pady=(0, 8))

        single_label = ttk.Label(left_panel, text="Enter article headline:")
        single_label.pack(anchor="w", pady=(4, 4))

        self.text_input = ttk.Entry(left_panel, font=("Segoe UI", 9), width=25)
        self.text_input.pack(fill="x", pady=(0, 8))

        # Upload Text button - page icon 📄
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

        # Run button - play symbol ▶
        run_btn = ttk.Button(
            buttons_frame,
            text="▶ Run",
            command=self.run_detection,
            style="Run.TButton",
            compound="left",
            width=12
        )
        run_btn.pack(side="left", padx=(0, 4))

        # Clear button - cross symbol ✖
        clear_btn = ttk.Button(
            buttons_frame,
            text="✖ Clear",
            command=self.clear_all,
            style="Clear.TButton",
            compound="left",
            width=12
        )
        clear_btn.pack(side="left", padx=(4, 0))

        right_panel = ttk.Frame(main_frame, style="TFrame")
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

        # Configure Treeview tags after tree is created
        self.tree.tag_configure("evenrow", background=self.colors["tree_alt"])

        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_container, textvariable=self.status_var, style="Status.TLabel", anchor="w")
        status_bar.pack(fill="x", side="bottom", padx=5, pady=2)

        self.csv_data = None

    def toggle_theme(self):
        if self.current_theme == "light":
            # Switch to dark theme
            self.apply_theme(self.dark_colors)
            self.current_theme = "dark"
            self.theme_button.config(text="☾")  # Moon symbol indicates dark mode active
            self.csv_file_label.configure(foreground="#A3A3A3")
            self.tree.tag_configure("evenrow", background=self.dark_colors["tree_alt"])
            self.status_var.set("Dark theme activated.")
        else:
            # Switch to light theme
            self.apply_theme(self.light_colors)
            self.current_theme = "light"
            self.theme_button.config(text="☀")  # Sun symbol indicates light mode active
            self.csv_file_label.configure(foreground="#6B7280")
            self.tree.tag_configure("evenrow", background=self.light_colors["tree_alt"])
            self.status_var.set("Light theme activated.")

    def load_csv_file(self):
        filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(title="Select CSV File", filetypes=filetypes)
        if filepath:
            fg_color = "#6B7280" if self.current_theme == "light" else "#A3A3A3"
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
        if self.csv_data is not None and len(self.csv_data) > 0:
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
        fg_color = "#6B7280" if self.current_theme == "light" else "#A3A3A3"
        self.csv_file_label.configure(text="No file selected", foreground=fg_color)
        self.clear_results()
        self.status_var.set("Inputs and results cleared.")

if __name__ == "__main__":
    app = FakeNewsDetectorApp()
    app.mainloop()

