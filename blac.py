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
        self.geometry("820x640")
        self.resizable(False, False)
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._set_styles()
        self.create_widgets()
        self.current_theme = "dark"
        self.toast = None

    def _set_styles(self):
        # Professional color palettes
        self.dark_colors = {
            "bg": "#1E1E1E",
            "fg": "#D4D4D4",
            "select_button": "#3B82F6",
            "select_hover": "#2563EB",
            "upload_button": "#10B981",  # Green shade for upload
            "upload_hover": "#059669",
            "run_button": "#00A5EF",  # Spark blue for Run button
            "run_hover": "#008DD0",
            "clear_button": "#EF4444",
            "clear_hover": "#DC2626",
            "entry_bg": "#2D2D2D",
            "entry_fg": "#D4D4D4",
            "tree_bg": "#252526",
            "tree_fg": "#D4D4D4",
            "tree_alt": "#2A2A2A",
            "status_bg": "#004BA0",  # Spark blue light background for status bar in dark
            "status_fg": "#D4D4D4",
        }

        self.light_colors = {
            "bg": "#FFFFFF",
            "fg": "#1F1F1F",
            "select_button": "#3B82F6",
            "select_hover": "#2563EB",
            # Light green shade for upload
            "upload_button": "#7CCD7C",
            "upload_hover": "#5CA85C",
            "run_button": "#00A5EF",  # Spark blue same as dark's run button
            "run_hover": "#008DD0",
            "clear_button": "#EF4444",
            "clear_hover": "#DC2626",
            "entry_bg": "#F3F4F6",
            "entry_fg": "#1F1F1F",
            "tree_bg": "#FFFFFF",
            "tree_fg": "#1F1F1F",
            "tree_alt": "#F9FAFB",
            "status_bg": "#E0F0FF",  # Lighter spark blue for status bar in light
            "status_fg": "#134e96",
        }
        self.apply_theme(self.dark_colors)

    def apply_theme(self, colors):
        self.colors = colors

        self.configure(bg=colors["bg"])
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["fg"], font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground=colors["fg"])

        for style, bg, hover in [
            ("Select.TButton", colors["select_button"], colors["select_hover"]),
            ("Upload.TButton", colors["upload_button"], colors["upload_hover"]),
            ("Run.TButton", colors["run_button"], colors["run_hover"]),
            ("Clear.TButton", colors["clear_button"], colors["clear_hover"]),
        ]:
            self.style.configure(
                style,
                font=("Segoe UI", 10, "bold"),
                foreground="white",
                background=bg,
                borderwidth=0,
                padding=8,
                relief="flat",
            )
            self.style.map(style, background=[("active", hover), ("disabled", "#767676")])

        self.style.configure(
            "TEntry",
            font=("Segoe UI", 10),
            fieldbackground=colors["entry_bg"],
            foreground=colors["entry_fg"],
            borderwidth=1,
            relief="solid",
            padding=6,
        )

        self.style.configure(
            "Treeview",
            background=colors["tree_bg"],
            foreground=colors["tree_fg"],
            fieldbackground=colors["tree_bg"],
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        self.style.map(
            "Treeview", background=[("selected", colors["select_button"])], foreground=[("selected", "#FFFFFF")]
        )
        self.style.configure("Treeview.Row", background=colors["tree_alt"])

        self.style.configure(
            "Status.TLabel",
            background=colors["status_bg"],
            foreground=colors["status_fg"],
            font=("Segoe UI", 9),
            relief="flat",
            padding=(6, 5),
        )

        if hasattr(self, "csv_file_label"):
            self.csv_file_label.configure(foreground=colors["fg"])

        if hasattr(self, "tree"):
            self.tree.tag_configure("evenrow", background=colors["tree_alt"])

        # Toggle icon color black or white, with transparent bg
        if hasattr(self, "theme_button"):
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
                cursor="hand2",
                text="☀" if self.current_theme == "light" else "☾",
            )

    def create_widgets(self):
        main_container = ttk.Frame(self, style="TFrame", borderwidth=0)
        main_container.pack(fill="both", expand=True, padx=8, pady=8)

        # Add icon to the title using emoji
        header = ttk.Label(main_container, text="📰  Fake News Detector", style="Header.TLabel")
        header.pack(pady=(10, 8))

        self.main_frame = ttk.Frame(main_container, style="TFrame")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=2)

        self.theme_button = tk.Button(
            self.main_frame,
            text="☾",  # Moon for startup dark theme
            command=self.toggle_theme,
            width=3,
            height=1,
            bg=self.dark_colors["bg"],
            fg="white",
            activebackground=self.dark_colors["bg"],
            activeforeground="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 12, "bold"),
            cursor="hand2",
        )
        self.theme_button.grid(row=0, column=1, sticky="ne", padx=(0, 5), pady=(5, 0))

        left_panel = ttk.Frame(self.main_frame, style="TFrame")
        left_panel.grid(row=1, column=0, sticky="nswe", padx=(0, 8))

        csv_label = ttk.Label(left_panel, text="Upload CSV file (.csv):")
        csv_label.pack(anchor="w", pady=(0, 4))

        csv_button = ttk.Button(
            left_panel,
            text="📁 Select CSV",
            command=self.load_csv_file,
            style="Upload.TButton",
            compound="left",
            width=18,
        )
        csv_button.pack(fill="x", pady=(0, 8))

        self.csv_file_label = ttk.Label(left_panel, text="No file selected", foreground=self.dark_colors["fg"])
        self.csv_file_label.pack(anchor="w", pady=(0, 8))

        single_label = ttk.Label(left_panel, text="Enter article headline:")
        single_label.pack(anchor="w", pady=(4, 4))

        self.text_input = ttk.Entry(left_panel, font=("Segoe UI", 9), width=25)
        self.text_input.pack(fill="x", pady=(0, 8))

        upload_text_button = ttk.Button(
            left_panel,
            text="📄 Upload Text (.txt)",
            command=self.load_text_file,
            style="Upload.TButton",
            compound="left",
            width=18,
        )
        upload_text_button.pack(fill="x", pady=(0, 8))

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

        self.tree.tag_configure("evenrow", background=self.dark_colors["tree_alt"])

        self.status_var = tk.StringVar(value="Ready")
        # Position status bar just below buttons and results
        self.status_bar = ttk.Label(
            self.main_frame, textvariable=self.status_var, style="Status.TLabel", anchor="w"
        )
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(4, 10))

        self.csv_data = None

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.apply_theme(self.light_colors)
            self.current_theme = "light"
            self.theme_button.config(text="☀", fg="#000000", bg=self.light_colors["bg"], activebackground=self.light_colors["bg"], activeforeground="#000000")
            self.csv_file_label.configure(foreground=self.light_colors["fg"])
            self.tree.tag_configure("evenrow", background=self.light_colors["tree_alt"])
            self.status_var.set("Light theme activated.")
        else:
            self.apply_theme(self.dark_colors)
            self.current_theme = "dark"
            self.theme_button.config(text="☾", fg="#FFFFFF", bg=self.dark_colors["bg"], activebackground=self.dark_colors["bg"], activeforeground="#FFFFFF")
            self.csv_file_label.configure(foreground=self.dark_colors["fg"])
            self.tree.tag_configure("evenrow", background=self.dark_colors["tree_alt"])
            self.status_var.set("Dark theme activated.")

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
