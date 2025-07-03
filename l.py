import sys
import threading
import requests
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTextEdit, QHBoxLayout,
    QSizePolicy, QSpacerItem, QFileDialog, QGraphicsOpacityEffect
)
from transformers import pipeline

# Google Custom Search API credentials
API_KEY = "AIzaSyBryMskx_DgR5kuitDJk60nhNlsRYQNk9k"
SEARCH_ENGINE_ID = "734837c73550d4dba"

# NLI label mapping
NLI_LABELS = {
    'ENTAILMENT': 'Supports (Likely Real News)',
    'CONTRADICTION': 'Refutes (Likely Fake News)',
    'NEUTRAL': 'Neutral'
}

class FakeNewsNLIApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fake News Detector - NLI Powered")
        self.setWindowIcon(QIcon.fromTheme("dialog-information"))
        self.setMinimumSize(650, 500)
        self.nli_classifier = None
        self.error_message = ""
        self.setup_ui()
        self.load_model_async()

    def setup_ui(self):
        font_title = QFont("Segoe UI", 22, QFont.Bold)
        font_label = QFont("Segoe UI", 11)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(30, 20, 30, 20)

        self.title_label = QLabel("Fake News Detector - NLI Powered")
        self.title_label.setFont(font_title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.add_animation(self.title_label)
        main_layout.addWidget(self.title_label)

        self.instruction_label = QLabel(
            "Enter a news headline or claim below. The system will analyze if it is supported or refuted by natural language inference and search the web."
        )
        self.instruction_label.setFont(font_label)
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setWordWrap(True)
        main_layout.addWidget(self.instruction_label)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type or paste a news headline or claim here...")
        self.input_line.setFont(font_label)
        self.input_line.setMinimumHeight(42)
        self.input_line.setEnabled(False)
        main_layout.addWidget(self.input_line)

        self.upload_button = QPushButton("Upload Article/Image")
        self.upload_button.setFont(font_label)
        self.upload_button.setEnabled(False)
        self.upload_button.clicked.connect(self.upload_file)
        main_layout.addWidget(self.upload_button)

        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.check_button = QPushButton("Check")
        self.check_button.setFont(font_label)
        self.check_button.setMinimumHeight(40)
        self.check_button.setEnabled(False)
        self.check_button.clicked.connect(self.on_check_clicked)
        button_layout.addWidget(self.check_button)

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        main_layout.addLayout(button_layout)

        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        main_layout.addWidget(self.result_label)

        self.links_box = QTextEdit()
        self.links_box.setFont(QFont("Segoe UI", 10))
        self.links_box.setReadOnly(True)
        self.links_box.setVisible(False)
        self.links_box.setStyleSheet("background-color: #fefefe; border: 1px solid #ddd; padding: 10px;")
        main_layout.addWidget(self.links_box)

        self.footer_label = QLabel("Model: albert-base-v2 | Powered by Hugging Face Transformers and Google Custom Search API")
        self.footer_label.setFont(QFont("Segoe UI", 8))
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("color: gray;")
        main_layout.addWidget(self.footer_label)

        self.setLayout(main_layout)

    def add_animation(self, widget):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        for i in range(0, 11):
            QTimer.singleShot(i * 100, lambda value=i: effect.setOpacity(value / 10.0))

    def load_model_async(self):
        def load():
            try:
                self.nli_classifier = pipeline("zero-shot-classification", model="juliensalinas/albert-base-v2-nli")
                QTimer.singleShot(0, self.on_model_loaded)
            except Exception as e:
                self.error_message = f"Model load failed:\n{e}"
                QTimer.singleShot(0, self.on_model_load_failed)

        threading.Thread(target=load, daemon=True).start()
        self.result_label.setText("Loading NLI model... Please wait.")
        self.check_button.setEnabled(False)

    def on_model_loaded(self):
        self.result_label.setText("Model loaded. Please enter a headline or upload a file.")
        self.input_line.setEnabled(True)
        self.upload_button.setEnabled(True)
        self.check_button.setEnabled(True)

        # Prompt the user with message box
        QMessageBox.information(
            self,
            "Ready",
            "Model loaded successfully!\n\nYou can now enter a news headline or upload an article/image to verify."
        )

    def on_model_load_failed(self):
        QMessageBox.critical(self, "Model Load Error", self.error_message)
        self.result_label.setText(self.error_message)
        self.check_button.setEnabled(False)

    def upload_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Upload Article/Image", "", "Text Files (*.txt);;Image Files (*.png;*.jpg;*.jpeg)", options=options)
        if file_name:
            self.input_line.setText(file_name)
            self.result_label.setText("File uploaded. You can now check the claim.")

    def on_check_clicked(self):
        claim = self.input_line.text().strip()
        if len(claim) < 5:
            QMessageBox.warning(self, "Input Error", "Please enter at least 5 characters in the headline or claim.")
            return

        self.check_button.setEnabled(False)
        self.result_label.setText("Analyzing claim with NLI...")
        self.links_box.clear()
        self.links_box.setVisible(False)

        def classify_and_search():
            try:
                candidate_labels = ["ENTAILMENT", "CONTRADICTION", "NEUTRAL"]
                results = self.nli_classifier(claim, candidate_labels, multi_label=False)
                label = results['labels'][0].upper()
                score = results['scores'][0]
                verdict = NLI_LABELS.get(label, "Unknown")
                QTimer.singleShot(0, lambda: self.result_label.setText(f"Prediction: {verdict} ({score * 100:.1f}%)"))

                if label == "ENTAILMENT":
                    links = self.search_news_articles(claim)
                    QTimer.singleShot(0, lambda: self.show_links(links))
                else:
                    QTimer.singleShot(0, lambda: self.show_links([]))
            except Exception as e:
                QTimer.singleShot(0, lambda: self.result_label.setText(f"Error during analysis: {e}"))
            finally:
                QTimer.singleShot(0, lambda: self.check_button.setEnabled(True))

        threading.Thread(target=classify_and_search, daemon=True).start()

    def show_links(self, links):
        self.links_box.setVisible(True)
        if links:
            self.links_box.append("Related Articles Found:\n")
            for idx, link in enumerate(links, start=1):
                self.links_box.append(f"{idx}. {link}")
        else:
            self.links_box.setText("No related articles found.")

    def search_news_articles(self, query):
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": API_KEY,
                "cx": SEARCH_ENGINE_ID,
                "q": query,
                "num": 5
            }
            response = requests.get(url, params=params)
            results = response.json()
            if "items" in results:
                return [item["link"] for item in results["items"]]
            return []
        except Exception as e:
            print(f"Search error: {e}")
            return []

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FakeNewsNLIApp()
    window.show()
    sys.exit(app.exec())
