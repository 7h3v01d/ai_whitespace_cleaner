# AI Whitespace & Watermark Cleaner

⚠️ **LICENSE & USAGE NOTICE — READ FIRST**

This repository is **source-available for private technical evaluation and testing only**.

- ❌ No commercial use  
- ❌ No production use  
- ❌ No academic, institutional, or government use  
- ❌ No research, benchmarking, or publication  
- ❌ No redistribution, sublicensing, or derivative works  
- ❌ No independent development based on this code  

All rights remain exclusively with the author.  
Use of this software constitutes acceptance of the terms defined in **LICENSE.txt**.

---

A powerful PyQt6-based desktop application designed to detect, visualize, and clean whitespace characters and potential AI-generated text watermarks (e.g., from ChatGPT). This tool is ideal for text preprocessing, data cleaning, or analyzing text for hidden Unicode characters and AI patterns.

## Features

- **Whitespace Detection & Visualization**:
  - Displays standard whitespace (spaces as `·`, tabs as `→`, newlines as `¶`).
  - Highlights invisible Unicode characters (e.g., zero-width spaces `◆`, narrow no-break spaces `※`) often used as AI watermarks.
- **Cleaning Options**:
  - Remove extra spaces, tabs, or newlines.
  - Replace tabs with a specified number of spaces (2, 4, or 8).
  - Trim leading/trailing whitespace from lines.
  - Remove invisible Unicode characters (e.g., U+200B, U+202F) associated with AI watermarks.
  - Custom regex-based cleaning for advanced users.
- **Watermark Detection**:
  - Scans for known AI watermark characters (e.g., zero-width spaces, narrow no-break spaces).
  - Basic statistical analysis to estimate AI-generated text likelihood via word entropy.
- **File Handling**:
  - Load text from `.txt` files and save cleaned output.
- **Undo/Redo**:
  - Supports undoing and redoing cleaning operations with a history stack.
- **Statistics**:
  - Real-time counts of spaces, tabs, newlines, and invisible Unicode characters.
  - Detailed watermark stats, including AI likelihood and top words.
- **User Interface**:
  - Syntax highlighting for visualized whitespace and watermarks.
  - Keyboard shortcuts (e.g., Ctrl+O to load, Ctrl+S to save, Ctrl+Z to undo).
  - Progress bar for watermark scanning and status bar for feedback.

## Installation

### Prerequisites
- Python 3.8 or higher
- PyQt6 library

### Steps
1. **Install Python**:
   - Download and install Python from [python.org](https://www.python.org/downloads/).
   - Ensure `pip` is available.

2. **Install PyQt6**:
   ```bash
   pip install PyQt6
   ```

3. **Download the Script**:
   - Save the main script as `enhanced_whitespace_cleaner.py` from this repository or your source.

4. **Run the Application**:
   ```bash
   python enhanced_whitespace_cleaner.py
   ```

## Usage

1. **Launch the Application**:
   - Run the script to open the GUI.

2. **Input Text**:
   - Paste text into the "Input Text" area or use **Load File** (Ctrl+O) to import a `.txt` file (e.g., `secret_ai_whitespace_test.txt`).

3. **Detect Whitespace & Watermarks**:
   - Click **Detect Whitespace & Watermarks** (Ctrl+D) to visualize:
     - Spaces (`·`), tabs (`→`), newlines (`¶`).
     - Invisible Unicode like zero-width spaces (`◆`) or narrow no-break spaces (`※`).

4. **Scan for AI Patterns**:
   - Click **Scan for AI Patterns** (Ctrl+W) to analyze:
     - Counts and details of invisible Unicode characters.
     - Word entropy and AI likelihood (low entropy may indicate AI-generated text).

5. **Clean Text**:
   - Select cleaning options:
     - Remove Extra Spaces, Tabs, or Newlines.
     - Trim Leading/Trailing Whitespace.
     - Remove Invisible Unicode (Watermarks).
     - Replace Tabs with Spaces (choose 2, 4, or 8 spaces).
   - Use **Watermark Preset** dropdown for common AI watermark patterns (e.g., ChatGPT Unicode Watermarks: `[\u202F\u200B\uFEFF]`).
   - Enter custom regex patterns (e.g., `[\u200B]` for zero-width spaces) and replacements.
   - Click **Clean Whitespace & Watermarks** (Ctrl+C) to apply.

6. **Save Output**:
   - Use **Save Output** (Ctrl+S) to export cleaned text to a `.txt` file.

7. **Undo/Redo**:
   - Use **Undo** (Ctrl+Z) or **Redo** (Ctrl+Y) to navigate cleaning history.

8. **Clear**:
   - Click **Clear** (Ctrl+R) to reset all fields and history.

## Example: Testing with ChatGPT Text
To test for ChatGPT watermarks:
1. Generate a long text (e.g., a 500-word essay) using ChatGPT (preferably newer models like GPT-o3 or GPT-o4-mini).
2. Save it as a `.txt` file or paste it into the input area.
3. Click **Detect Whitespace & Watermarks** to spot Unicode characters (e.g., `◆` for U+200B).
4. Click **Scan for AI Patterns** to check for invisible chars and AI likelihood.
5. Use the **ChatGPT Unicode Watermarks** preset or check **Remove Invisible Unicode** and clean.
6. Verify stats to confirm watermark removal.

## Sample Test File
Use the provided `secret_ai_whitespace_test.txt` to test:
```
Sample   text   with    multiple     spaces.
This	line	has	tabs	and spaces.
    Indented    line    with    mixed    whitespace.
Extra



newlines



here.
Secret AI message:		hidden		in		whitespace.
Normal text follows.
```

## Limitations
- **Unicode Watermarks**: Detects and removes known invisible Unicode characters (e.g., U+200B, U+202F) but may miss undocumented ones.
- **Statistical Watermarks**: The tool's entropy-based AI likelihood check is a basic heuristic. It cannot reliably detect ChatGPT's statistical token-based watermarks, which require advanced machine learning models.
- **Short Texts**: AI detection is less accurate for short or heavily edited texts.
- **Ethical Use**: Removing watermarks may enable misuse (e.g., passing AI text as human-written). Use responsibly for legitimate purposes like data cleaning or analysis.

## Future Improvements
- **Batch Processing**: Process multiple files in a folder.
- **Advanced AI Detection**: Integrate with Hugging Face `transformers` for robust statistical watermark detection.
- **Export Reports**: Save detailed stats as CSV or PDF.
- **Cloud Integration**: Support for loading/saving from cloud storage (e.g., Google Drive).
- **Live Preview**: Show cleaning results in real-time as options are selected.

## Contribution Policy

Feedback, bug reports, and suggestions are welcome.

You may submit:

- Issues
- Design feedback
- Pull requests for review

However:

- Contributions do not grant any license or ownership rights
- The author retains full discretion over acceptance and future use
- Contributors receive no rights to reuse, redistribute, or derive from this code

---

## License
This project is not open-source.

It is licensed under a private evaluation-only license.
See LICENSE.txt for full terms.