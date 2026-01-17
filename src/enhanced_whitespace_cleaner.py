import sys
import re
import os
import unicodedata
from collections import Counter
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QCheckBox, QLabel, QComboBox, QMessageBox,
    QFileDialog, QLineEdit, QStatusBar, QProgressBar
)
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class UnicodeHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Highlight standard whitespace
        space_format = QTextCharFormat()
        space_format.setForeground(QColor("blue"))
        self.highlighting_rules.append((re.compile(r'·'), space_format))
        
        tab_format = QTextCharFormat()
        tab_format.setForeground(QColor("red"))
        self.highlighting_rules.append((re.compile(r'→'), tab_format))
        
        newline_format = QTextCharFormat()
        newline_format.setForeground(QColor("green"))
        self.highlighting_rules.append((re.compile(r'¶'), newline_format))
        
        # Highlight invisible Unicode (watermark suspects)
        invisible_format = QTextCharFormat()
        invisible_format.setForeground(QColor("purple"))
        invisible_format.setBackground(QColor("yellow"))
        self.highlighting_rules.append((re.compile(r'◆|※'), invisible_format))  # ◆ for zero-width, ※ for NNBSP

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.start(), match.end()
                self.setFormat(start, end - start, format)

class WatermarkScanThread(QThread):
    finished = pyqtSignal(dict)
    
    def __init__(self, text):
        super().__init__()
        self.text = text
    
    def run(self):
        # Scan for invisible Unicode chars (common AI watermarks)
        invisible_chars = []
        unicode_pattern = re.compile(r'[\u200B\u200C\u200D\u202F\u00A0\u2060\uFEFF\u2014\u2013]')  # ZWSP, ZWJ, NNBSP, NBSP, WJ, ZWNBSP, Em/En Dash
        for match in unicode_pattern.finditer(self.text):
            char = match.group()
            name = unicodedata.name(char, "Unknown")
            invisible_chars.append(f"{char} (U+{ord(char):04X}: {name})")
        
        # Basic statistical check for token patterns (simplified AI likelihood)
        words = re.findall(r'\b\w+\b', self.text.lower())
        word_counter = Counter(words)
        top_words = [word for word, count in word_counter.most_common(10)]
        entropy = -sum((count / len(words)) * re.log2(count / len(words) + 1e-10) for count in word_counter.values()) if words else 0
        ai_likelihood = "High" if entropy < 4.5 else "Low"  # Rough heuristic: AI text often has lower entropy
        
        stats = {
            'invisible_chars': len(invisible_chars),
            'details': invisible_chars[:10],  # Limit to first 10
            'word_entropy': entropy,
            'ai_likelihood': ai_likelihood,
            'top_words': top_words
        }
        self.finished.emit(stats)

class WhitespaceCleaner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced AI Whitespace & Watermark Cleaner")
        self.setGeometry(100, 100, 1200, 800)
        
        # History for undo/redo
        self.history = []
        self.history_index = -1
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Input text area
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter or paste text here...")
        self.input_text.textChanged.connect(self.update_stats)
        self.layout.addWidget(QLabel("Input Text:"))
        self.layout.addWidget(self.input_text)
        
        # Output text area with syntax highlighting
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Visible whitespace and watermarks will appear here...")
        self.highlighter = UnicodeHighlighter(self.output_text.document())
        self.layout.addWidget(QLabel("Output with Visible Whitespace & Watermarks:"))
        self.layout.addWidget(self.output_text)
        
        # Whitespace and watermark statistics
        self.stats_label = QLabel("Spaces: 0 | Tabs: 0 | Newlines: 0 | Invisible Unicode: 0 | AI Likelihood: Low")
        self.layout.addWidget(self.stats_label)
        self.detailed_stats = QTextEdit()
        self.detailed_stats.setMaximumHeight(100)
        self.detailed_stats.setReadOnly(True)
        self.layout.addWidget(QLabel("Detailed Watermark Stats:"))
        self.layout.addWidget(self.detailed_stats)
        
        # Options for cleaning (existing + watermark-specific)
        self.options_layout = QHBoxLayout()
        self.remove_spaces = QCheckBox("Remove Extra Spaces")
        self.remove_tabs = QCheckBox("Remove Tabs")
        self.remove_newlines = QCheckBox("Remove Extra Newlines")
        self.trim_lines = QCheckBox("Trim Leading/Trailing Whitespace")
        self.remove_invisible = QCheckBox("Remove Invisible Unicode (Watermarks)")
        self.remove_invisible.setToolTip("Targets zero-width spaces, NNBSP, etc. used in AI watermarks")
        self.options_layout.addWidget(self.remove_spaces)
        self.options_layout.addWidget(self.remove_tabs)
        self.options_layout.addWidget(self.remove_newlines)
        self.options_layout.addWidget(self.trim_lines)
        self.options_layout.addWidget(self.remove_invisible)
        self.layout.addLayout(self.options_layout)
        
        # Replace tabs with spaces
        self.tab_replace_layout = QHBoxLayout()
        self.replace_tabs = QCheckBox("Replace Tabs with Spaces")
        self.tab_spaces = QComboBox()
        self.tab_spaces.addItems(["2", "4", "8"])
        self.tab_replace_layout.addWidget(self.replace_tabs)
        self.tab_replace_layout.addWidget(QLabel("Spaces per Tab:"))
        self.tab_replace_layout.addWidget(self.tab_spaces)
        self.tab_replace_layout.addStretch()
        self.layout.addLayout(self.tab_replace_layout)
        
        # Custom regex cleaning
        self.regex_layout = QHBoxLayout()
        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("Enter custom regex (e.g., \\u202F for NNBSP watermark)")
        self.regex_replace = QLineEdit()
        self.regex_replace.setPlaceholderText("Replace with (e.g., ' ')")
        self.regex_layout.addWidget(QLabel("Custom Regex:"))
        self.regex_layout.addWidget(self.regex_input)
        self.regex_layout.addWidget(QLabel("Replace:"))
        self.regex_layout.addWidget(self.regex_replace)
        self.layout.addLayout(self.regex_layout)
        
        # Watermark presets
        self.preset_layout = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["None", "ChatGPT Unicode Watermarks", "All Invisible Chars"])
        self.preset_combo.currentTextChanged.connect(self.set_preset_regex)
        self.preset_layout.addWidget(QLabel("Watermark Preset:"))
        self.preset_layout.addWidget(self.preset_combo)
        self.layout.addLayout(self.preset_layout)
        
        # File handling and buttons
        self.button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load File")
        self.save_button = QPushButton("Save Output")
        self.detect_button = QPushButton("Detect Whitespace & Watermarks")
        self.clean_button = QPushButton("Clean Whitespace & Watermarks")
        self.scan_button = QPushButton("Scan for AI Patterns")
        self.undo_button = QPushButton("Undo")
        self.redo_button = QPushButton("Redo")
        self.clear_button = QPushButton("Clear")
        self.load_button.clicked.connect(self.load_file)
        self.save_button.clicked.connect(self.save_file)
        self.detect_button.clicked.connect(self.detect_whitespace)
        self.clean_button.clicked.connect(self.clean_whitespace)
        self.scan_button.clicked.connect(self.scan_watermarks)
        self.undo_button.clicked.connect(self.undo)
        self.redo_button.clicked.connect(self.redo)
        self.clear_button.clicked.connect(self.clear_text)
        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.detect_button)
        self.button_layout.addWidget(self.clean_button)
        self.button_layout.addWidget(self.scan_button)
        self.button_layout.addWidget(self.undo_button)
        self.button_layout.addWidget(self.redo_button)
        self.button_layout.addWidget(self.clear_button)
        self.layout.addLayout(self.button_layout)
        
        # Progress bar for scans
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)
        
        # Keyboard shortcuts
        self.load_button.setShortcut("Ctrl+O")
        self.save_button.setShortcut("Ctrl+S")
        self.detect_button.setShortcut("Ctrl+D")
        self.clean_button.setShortcut("Ctrl+C")
        self.scan_button.setShortcut("Ctrl+W")
        self.undo_button.setShortcut("Ctrl+Z")
        self.redo_button.setShortcut("Ctrl+Y")
        self.clear_button.setShortcut("Ctrl+R")
        
    def set_preset_regex(self, preset):
        if preset == "ChatGPT Unicode Watermarks":
            self.regex_input.setText(r'[\u202F\u200B\uFEFF]')  # NNBSP, ZWSP, ZWNBSP
            self.regex_replace.setText(" ")
        elif preset == "All Invisible Chars":
            self.regex_input.setText(r'[\u200B\u200C\u200D\u202F\u00A0\u2060\uFEFF\u2014\u2013]')
            self.regex_replace.setText(" ")
        else:
            self.regex_input.clear()
            self.regex_replace.clear()
    
    def update_stats(self):
        """Update basic whitespace statistics."""
        text = self.input_text.toPlainText()
        spaces = len(re.findall(r' ', text))
        tabs = len(re.findall(r'\t', text))
        newlines = len(re.findall(r'\n', text))
        self.stats_label.setText(f"Spaces: {spaces} | Tabs: {tabs} | Newlines: {newlines} | Invisible Unicode: 0 | AI Likelihood: Low")
        self.status_bar.showMessage("Statistics updated")
        
    def scan_watermarks(self):
        """Scan for watermarks and AI patterns."""
        text = self.input_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "Warning", "Input text is empty!")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.thread = WatermarkScanThread(text)
        self.thread.finished.connect(self.on_scan_finished)
        self.thread.start()
        
    def on_scan_finished(self, stats):
        self.progress_bar.setVisible(False)
        details = "\n".join(stats['details']) if stats['details'] else "No invisible chars found."
        ai_note = f"AI Likelihood: {stats['ai_likelihood']} (Entropy: {stats['word_entropy']:.2f})\nTop Words: {', '.join(stats['top_words'][:5])}"
        self.detailed_stats.setPlainText(f"Invisible Unicode Chars Found: {stats['invisible_chars']}\n{details}\n\n{ai_note}")
        self.stats_label.setText(self.stats_label.text().replace("?", f"{stats['invisible_chars']} | {stats['ai_likelihood']}"))
        self.status_bar.showMessage(f"Watermark scan complete: {stats['invisible_chars']} invisible chars detected")
        
    def detect_whitespace(self):
        """Display text with visible whitespace and basic Unicode."""
        text = self.input_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "Warning", "Input text is empty!")
            return
        
        # Replace standard whitespace
        visible_text = text.replace(" ", "·")
        visible_text = visible_text.replace("\t", "→")
        visible_text = visible_text.replace("\n", "¶\n")
        
        # Mark invisible Unicode
        def replace_invisible(match):
            char = match.group()
            if char == "\u202F":  # NNBSP
                return "※"  # Visible marker
            elif char in ["\u200B", "\uFEFF"]:  # Zero-width
                return "◆"
            return char
        
        visible_text = re.sub(r'[\u200B\u200C\u200D\u202F\u00A0\u2060\uFEFF\u2014\u2013]', replace_invisible, visible_text)
        
        self.output_text.setPlainText(visible_text)
        self.status_bar.showMessage("Whitespace and watermarks detected")
        
    def clean_whitespace(self):
        """Clean whitespace and watermarks based on options."""
        text = self.input_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "Warning", "Input text is empty!")
            return
        
        original_text = text
        
        # Standard cleaning
        if self.remove_spaces.isChecked():
            text = re.sub(r'\s+', ' ', text)
        
        if self.remove_tabs.isChecked():
            text = text.replace("\t", "")
        
        if self.replace_tabs.isChecked():
            spaces = " " * int(self.tab_spaces.currentText())
            text = text.replace("\t", spaces)
        
        if self.remove_newlines.isChecked():
            text = re.sub(r'\n+', '\n', text)
        
        if self.trim_lines.isChecked():
            lines = text.splitlines()
            text = "\n".join(line.strip() for line in lines)
        
        # Invisible Unicode cleaning (watermarks)
        if self.remove_invisible.isChecked():
            text = re.sub(r'[\u200B\u200C\u200D\u202F\u00A0\u2060\uFEFF\u2014\u2013]', ' ', text)
        
        # Custom regex
        if self.regex_input.text():
            try:
                text = re.sub(self.regex_input.text(), self.regex_replace.text(), text)
            except re.error:
                QMessageBox.warning(self, "Error", "Invalid regex pattern!")
                return
        
        # Save to history
        self.history = self.history[:self.history_index + 1]
        self.history.append(original_text)
        self.history_index += 1
        
        # Update
        self.input_text.setPlainText(text)
        self.detect_whitespace()
        self.update_stats()
        self.status_bar.showMessage("Whitespace and watermarks cleaned")
        
    def load_file(self):
        """Load text from a file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    self.input_text.setPlainText(file.read())
                self.detect_whitespace()
                self.status_bar.showMessage(f"Loaded: {os.path.basename(file_name)}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load file: {str(e)}")
        
    def save_file(self):
        """Save cleaned text to a file."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(self.input_text.toPlainText())
                self.status_bar.showMessage(f"Saved: {os.path.basename(file_name)}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file: {str(e)}")
        
    def undo(self):
        """Undo the last operation."""
        if self.history_index > 0:
            self.history_index -= 1
            self.input_text.setPlainText(self.history[self.history_index])
            self.detect_whitespace()
            self.update_stats()
            self.status_bar.showMessage("Undo applied")
        
    def redo(self):
        """Redo the last undone operation."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.input_text.setPlainText(self.history[self.history_index])
            self.detect_whitespace()
            self.update_stats()
            self.status_bar.showMessage("Redo applied")
        
    def clear_text(self):
        """Clear both text areas and reset history."""
        self.input_text.clear()
        self.output_text.clear()
        self.detailed_stats.clear()
        self.history = []
        self.history_index = -1
        self.update_stats()
        self.status_bar.showMessage("Cleared")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhitespaceCleaner()
    window.show()
    sys.exit(app.exec())