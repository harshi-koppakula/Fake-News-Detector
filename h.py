import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
import webbrowser
import os

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class FakeNewsDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fake News Detector Tool")
        self.root.geometry("900x700")
        self.root.configure(bg="#f9f9f9")  # Very light gray background

        self.api_key = "AIzaSyBryMskx_DgR5kuitDJk60nhNlsRYQNk9k"
        self.cx = "734837c73550d4dba"

        self.create_widgets()

    def create_widgets(self):
        header_frame = tk.Frame(self.root, bg="#273746", height=60)
        header_frame.pack(fill=tk.X)
        header_label = tk.Label(
            header_frame, text="Fake News Detector", bg="#273746", fg="#ecf0f1",
            font=("Segoe UI", 22, "bold")
        )
        header_label.pack(pady=10)

        input_frame = tk.Frame(self.root, bg="#f9f9f9", pady=10)
        input_frame.pack(fill=tk.X, padx=30)

        headline_label = tk.Label(input_frame, text="Enter Headline:", font=("Segoe UI", 14), bg="#f9f9f9", anchor="w", fg="#34495e")
        headline_label.pack(fill=tk.X, pady=(0, 6))

        self.headline_var = tk.StringVar()
        self.headline_entry = tk.Entry(
            input_frame, textvariable=self.headline_var, font=("Segoe UI", 14), fg="#34495e",
            relief=tk.FLAT, bd=1, bg="#ffffff", insertbackground='black'
        )
        self.headline_entry.pack(fill=tk.X, ipady=8, pady=(0,16))
        self.headline_entry.insert(0, "Enter headline here...")
        self.headline_entry.bind("<FocusIn>", self.clear_placeholder)
        self.headline_entry.bind("<FocusOut>", self.restore_placeholder)

        # Buttons frame for better horizontal layout on larger screens
        btns_frame = tk.Frame(input_frame, bg="#f9f9f9")
        btns_frame.pack(fill=tk.X)

        button_style = {
            "font": ("Segoe UI", 12, "bold"),
            "relief": tk.FLAT,
            "cursor": "hand2",
            "height": 2,
            "width": 25,
            "bd": 0,
            "padx": 10,
            "pady": 8,
        }

        # Professional color palette for buttons:
        # Upload Article - Deep Blue
        self.upload_btn = tk.Button(
            btns_frame, text="Upload Article (TXT or Image)", bg="#2e86c1", fg="white",
            activebackground="#1b4f72", **button_style
        )
        self.upload_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.upload_btn.config(command=self.upload_article)

        # Upload CSV - Dark Slate Gray
        self.upload_csv_btn = tk.Button(
            btns_frame, text="Upload CSV File", bg="#34495e", fg="white",
            activebackground="#232f34", **button_style
        )
        self.upload_csv_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.upload_csv_btn.config(command=self.upload_csv)

        # Analyze Article - Emerald Green
        self.analyze_btn = tk.Button(
            btns_frame, text="Analyze Article", bg="#27ae60", fg="white",
            activebackground="#196f3d", **button_style
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.analyze_btn.config(command=self.analyze_article)

        # Results frame
        self.result_frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief=tk.FLAT)
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        self.result_title = tk.Label(
            self.result_frame, text="Analysis Result", font=("Segoe UI", 18, "bold"),
            bg="#ffffff", anchor="w", pady=10, fg="#2c3e50"
        )
        self.result_title.pack(fill=tk.X, padx=15)

        self.result_text = tk.Label(
            self.result_frame, text="No analysis yet.", font=("Segoe UI", 15),
            bg="#ffffff", justify=tk.LEFT, wraplength=800,
            anchor="nw", padx=15, pady=15, fg="#2c3e50"
        )
        self.result_text.pack(fill=tk.X, padx=10)

        self.related_label = tk.Label(
            self.result_frame, text="Related Links:", font=("Segoe UI", 15, "bold"),
            bg="#ffffff", anchor="w", pady=10, fg="#2c3e50"
        )
        self.related_label.pack(fill=tk.X, padx=15)
        self.related_label.pack_forget()

        self.links_frame = tk.Frame(self.result_frame, bg="#ffffff")
        self.links_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.links_frame.pack_forget()

        self.scrolled_links = scrolledtext.ScrolledText(
            self.links_frame, height=10, font=("Segoe UI", 13), bg="#fefefe",
            state=tk.DISABLED, cursor="arrow", relief=tk.FLAT, wrap=tk.WORD, fg="#34495e"
        )
        self.scrolled_links.pack(fill=tk.BOTH, expand=True)
        self.scrolled_links.bind("<Button-1>", self.on_link_click)

        self.uploaded_article_text = ""
        self.uploaded_file_path = None

    def clear_placeholder(self, event=None):
        if self.headline_entry.get() == "Enter headline here...":
            self.headline_entry.delete(0, tk.END)
            self.headline_entry.config(fg="#000000")

    def restore_placeholder(self, event=None):
        if not self.headline_entry.get():
            self.headline_entry.insert(0, "Enter headline here...")
            self.headline_entry.config(fg="#7f8c8d")

    def upload_article(self):
        file_path = filedialog.askopenfilename(
            title="Select Article File",
            filetypes=[("Text files", "*.txt"), ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")],
        )
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            try:
                if ext == ".txt":
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read().strip()
                        self.uploaded_article_text = text
                        messagebox.showinfo("Success", "Text file uploaded.")
                        self.headline_entry.delete(0, tk.END)
                        self.headline_entry.insert(0, text.splitlines()[0])
                elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"] and OCR_AVAILABLE:
                    image = Image.open(file_path)
                    text = pytesseract.image_to_string(image).strip()
                    self.uploaded_article_text = text
                    messagebox.showinfo("Success", "Image text extracted.")
                    self.headline_entry.delete(0, tk.END)
                    self.headline_entry.insert(0, text.splitlines()[0])
                else:
                    messagebox.showerror("Error", "Unsupported file or OCR not available.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def upload_csv(self):
        csv_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv")],
        )
        if csv_path:
            try:
                import pandas as pd
                df = pd.read_csv(csv_path)

                if 'text' not in df.columns or 'label' not in df.columns:
                    messagebox.showerror("Error", "CSV must contain both 'text' and 'label' columns.")
                    return

                classified = []
                for i, row in df.iterrows():
                    text = str(row['text']).strip()
                    label_raw = str(row['label']).strip().lower()
                    label = "True" if label_raw in ["true", "real", "genuine", "verified", "fact"] else "Fake"
                    classified.append(f"{i+1}. {label}\n{text[:150]}...\n")

                self.result_text.config(
                    text="CSV Classification Results:",
                    fg="#2c3e50"
                )
                self.related_label.pack_forget()
                self.links_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
                self.scrolled_links.config(state=tk.NORMAL)
                self.scrolled_links.delete("1.0", tk.END)
                self.scrolled_links.insert(tk.END, "\n".join(classified))
                self.scrolled_links.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process CSV:\n{e}")

    def analyze_article(self):
        query = self.headline_entry.get()
        if not query or query.strip() == "Enter headline here...":
            if not self.uploaded_article_text:
                messagebox.showwarning("Input Required", "Enter headline or upload article first.")
                return
            query = self.uploaded_article_text[:200]

        self.result_text.config(text="Analyzing article, please wait...", fg="#34495e")
        self.related_label.pack_forget()
        self.links_frame.pack_forget()
        self.scrolled_links.config(state=tk.NORMAL)
        self.scrolled_links.delete("1.0", tk.END)
        self.scrolled_links.config(state=tk.DISABLED)
        self.root.update_idletasks()

        try:
            related_links = self.google_custom_search(query)
            credible_domains = ["bbc.com", "reuters.com", "nytimes.com", "factcheck.org", "snopes.com"]
            credible_sources = [
                link for link in related_links if any(domain in link['link'] for domain in credible_domains)
            ]

            # Simplified result output as requested
            if len(credible_sources) >= 2:
                self.result_text.config(
                    fg="#27ae60",
                    text="Result: TRUE"
                )
            else:
                self.result_text.config(
                    fg="#e74c3c",
                    text="Result: FAKE"
                )

            if related_links:
                self.related_label.pack(fill=tk.X, padx=15)
                self.links_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
                self.scrolled_links.config(state=tk.NORMAL)
                self.scrolled_links.delete("1.0", tk.END)
                for item in related_links:
                    self.scrolled_links.insert(tk.END, f"{item['title']}\n{item['link']}\n\n")
                self.scrolled_links.config(state=tk.DISABLED)
        except Exception as e:
            self.result_text.config(fg="#c0392b", text=f"Error: {e}")

    def google_custom_search(self, query):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": self.api_key, "cx": self.cx, "q": query, "num": 5}
        response = requests.get(url, params=params)
        data = response.json()
        return [{"title": item.get("title"), "link": item.get("link")} for item in data.get("items", [])]

    def on_link_click(self, event):
        index = self.scrolled_links.index(f"@{event.x},{event.y}")
        line_index = index.split(".")[0]
        next_line = str(int(line_index) + 1)
        link = self.scrolled_links.get(f"{next_line}.0", f"{next_line}.end").strip()
        if link.startswith("http"):
            webbrowser.open(link)

def main():
    root = tk.Tk()
    app = FakeNewsDetectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

