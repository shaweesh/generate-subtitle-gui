import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import subprocess
import os
import threading
import json

# List of Whisper supported languages
SUPPORTED_LANGUAGES = [
    'af', 'ar', 'bg', 'bn', 'ca', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fi',
    'fr', 'gu', 'he', 'hi', 'hr', 'hu', 'id', 'it', 'ja', 'kn', 'ko', 'la', 'lv',
    'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'nl', 'pl', 'pt', 'ro', 'ru', 'si', 'sk',
    'sl', 'sq', 'sr', 'su', 'sv', 'sw', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'vi',
    'xh', 'yi', 'zu'
]

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def browse_file():
    filename = filedialog.askopenfilename(
        filetypes=[("Video files", "*.mp4;*.mkv;*.avi;*.mov;*.flv")]
    )
    if filename:
        input_file.set(filename)

def prepare_srt():
    if not input_file.get():
        messagebox.showerror("Error", "Please select an input file.")
        return

    # Disable all buttons except the Cancel button
    set_buttons_state("disabled")

    # Update the GUI to show progress
    status_var.set("Preparing SRT file...")
    progress.start()
    root.update_idletasks()

    # Run the long-running task in a separate thread
    thread = threading.Thread(target=run_prepare_srt)
    thread.start()

def run_prepare_srt():
    try:
        subprocess.run([
            "python", "main.py",
            "--input", input_file.get(),
            "--output", "prepared.srt",
            "--language", language_menu.get(),  # Get language from dropdown
            "--min_display_duration", "1.0"
        ], check=True)
        root.after(0, lambda: show_message("Success", "SRT file prepared. You can now edit 'prepared.srt'."))
    except subprocess.CalledProcessError:
        root.after(0, lambda: show_message("Error", "Failed to prepare SRT file."))
    finally:
        root.after(0, reset_status)

def open_srt_editor():
    if os.path.exists("prepared.srt"):
        editor_window = tk.Toplevel(root)
        editor_window.title("Edit SRT File")

        tk.Label(editor_window, text="Edit SRT File:").pack(padx=10, pady=5)
        srt_text = scrolledtext.ScrolledText(editor_window, wrap=tk.WORD, height=15, width=80)
        srt_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Load SRT content into the editor
        with open("prepared.srt", "r", encoding="utf-8") as file:
            srt_content = file.read()
        srt_text.insert(tk.END, srt_content)

        def save_srt():
            srt_content = srt_text.get(1.0, tk.END)
            with open("prepared.srt", "w", encoding="utf-8") as file:
                file.write(srt_content)
            messagebox.showinfo("Info", "SRT file saved successfully.")
            editor_window.destroy()  # Close the editor window after saving

        tk.Button(editor_window, text="Save SRT", command=save_srt).pack(padx=10, pady=5)

def complete_srt():
    if not os.path.exists("prepared.srt"):
        messagebox.showerror("Error", "Prepare the SRT file first.")
        return

    output_file = "completed.mp4"  # Specify the output video file with subtitles

    # Disable all buttons except the Cancel button
    set_buttons_state("disabled")

    status_var.set("Completing video...")
    progress.start()
    root.update_idletasks()

    # Run the long-running task in a separate thread
    thread = threading.Thread(target=run_complete_srt, args=(output_file,))
    thread.start()

def run_complete_srt(output_file):
    try:
        subprocess.run([
            "python", "merge_srt.py",
            "--video", input_file.get(),
            "--srt", "prepared.srt",
            "--output", output_file
        ], check=True)
        root.after(0, lambda: show_message("Success", f"Video with subtitles saved as {output_file}."))
    except subprocess.CalledProcessError:
        root.after(0, lambda: show_message("Error", "Failed to complete the SRT file."))
    finally:
        root.after(0, reset_status)

def show_message(title, message):
    messagebox.showinfo(title, message)

def reset_status():
    status_var.set("Ready")
    progress.stop()
    root.update_idletasks()
    set_buttons_state("normal")  # Re-enable buttons

def set_buttons_state(state):
    # Update the state of all buttons except the Cancel button
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button) and widget.cget("text") not in ["Cancel"]:
            widget.config(state=state)

def update_languages():
    language_menu['values'] = SUPPORTED_LANGUAGES
    if SUPPORTED_LANGUAGES:
        config = load_config()
        saved_language = config.get('language', SUPPORTED_LANGUAGES[0])
        language_menu.set(saved_language)

    language_menu.bind('<<ComboboxSelected>>', lambda e: save_config({'language': language_menu.get()}))

# Create the main window
root = tk.Tk()
root.title("Subtitle Generator")

input_file = tk.StringVar()
status_var = tk.StringVar(value="Ready")

# Create and place widgets
tk.Label(root, text="Input File:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=input_file, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=10)

tk.Button(root, text="Prepare", command=prepare_srt).grid(row=1, column=0, padx=10, pady=10)
tk.Button(root, text="Edit SRT", command=open_srt_editor).grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Complete", command=complete_srt).grid(row=1, column=2, padx=10, pady=10)

tk.Label(root, text="Select Language:").grid(row=2, column=0, padx=10, pady=10)
language_menu = ttk.Combobox(root, state="readonly")
language_menu.grid(row=2, column=1, padx=10, pady=10)

update_languages()

# Status label and progress bar
tk.Label(root, textvariable=status_var).grid(row=3, column=0, columnspan=3, padx=10, pady=10)
progress = ttk.Progressbar(root, mode='indeterminate')
progress.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

root.mainloop()
