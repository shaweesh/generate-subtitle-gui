import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import threading
from main import SubtitleGenerator
from merge_srt import SRTMerger

# Allow multiple OpenMP runtimes (temporary workaround)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# List of Whisper supported languages
SUPPORTED_LANGUAGES = [
    'af', 'ar', 'bg', 'bn', 'ca', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fi',
    'fr', 'gu', 'he', 'hi', 'hr', 'hu', 'id', 'it', 'ja', 'kn', 'ko', 'la', 'lv',
    'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'nl', 'pl', 'pt', 'ro', 'ru', 'si', 'sk',
    'sl', 'sq', 'sr', 'su', 'sv', 'sw', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'vi',
    'xh', 'yi', 'zu'
]

# List of Whisper models
WHISPER_MODELS = [
    'tiny',
    'base',
    'small',
    'medium',
    'large'
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
        json.dump(config, f, indent=4)

def browse_file():
    filename = filedialog.askopenfilename(
        filetypes=[("Video files", "*.mp4;*.mkv;*.avi;*.mov;*.flv"),
                   ("Audio files", "*.mp3;*.wav")]
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
        config = load_config()
        model_name = config.get('model', 'large')  # Default to 'large' model if not set

        # Validate model name
        if model_name not in WHISPER_MODELS:
            raise ValueError(f"Invalid model size '{model_name}', expected one of: {', '.join(WHISPER_MODELS)}")

        generator = SubtitleGenerator(model=model_name)

        file_extension = os.path.splitext(input_file.get())[1].lower()
        if file_extension in ['.mp4', '.mkv', '.avi', '.mov', '.flv']:
            generator.process_video(
                input_video=input_file.get(),
                output_srt="prepared.srt",
                language=language_menu.get(),
                min_display_duration=1.0
            )
        elif file_extension in ['.mp3', '.wav']:
            generator.process_audio(
                input_audio=input_file.get(),
                output_srt="prepared.srt",
                language=language_menu.get(),
                min_display_duration=1.0
            )
        else:
            raise ValueError("Unsupported file format.")

        root.after(0, lambda: show_message("Success", "SRT file prepared. You can now edit 'prepared.srt'."))
    except Exception as e:
        root.after(0, lambda: show_message("Error", f"Failed to prepare SRT file: {str(e)}"))
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

    status_var.set("Merging SRT with video...")
    progress.start()
    root.update_idletasks()

    # Run the long-running task in a separate thread
    thread = threading.Thread(target=run_complete_srt, args=(output_file,))
    thread.start()

def run_complete_srt(output_file):
    try:
        video_file = input_file.get()
        srt_file = "prepared.srt"
        merger = SRTMerger()
        merger.merge_srt_with_mp4(video_file, srt_file, output_file)
        root.after(0, lambda: show_message("Success", f"Successfully merged SRT with video into {output_file}"))
    except Exception as e:
        root.after(0, lambda: show_message("Error", f"Failed to merge SRT with video: {str(e)}"))
    finally:
        root.after(0, reset_status)

def show_message(title, message):
    messagebox.showinfo(title, message)

def reset_status():
    status_var.set("Ready")
    progress.stop()
    set_buttons_state("normal")

def set_buttons_state(state):
    for widget in [prepare_button, edit_button, complete_button]:
        widget.config(state=state)

def update_languages():
    language_menu['values'] = SUPPORTED_LANGUAGES
    config = load_config()
    # Set the default language based on the config or to 'en'
    language_menu.set(config.get('language', 'en'))

def update_models():
    model_menu['values'] = WHISPER_MODELS
    config = load_config()
    model_menu.set(config.get('model', 'large'))

def save_config_on_change(*args):
    config = {
        'model': model_menu.get(),
        'language': language_menu.get()
    }
    save_config(config)

# Create and configure the main window
root = tk.Tk()
root.title("Subtitle Preparation App")

input_file = tk.StringVar()
status_var = tk.StringVar(value="Ready")

# Create and place widgets
tk.Label(root, text="Input File:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=input_file, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=10, pady=10)

prepare_button = tk.Button(root, text="Prepare", command=prepare_srt)
prepare_button.grid(row=1, column=0, padx=10, pady=10)
edit_button = tk.Button(root, text="Edit SRT", command=open_srt_editor)
edit_button.grid(row=1, column=1, padx=10, pady=10)
complete_button = tk.Button(root, text="Complete", command=complete_srt)
complete_button.grid(row=1, column=2, padx=10, pady=10)

tk.Label(root, text="Select Language:").grid(row=2, column=0, padx=10, pady=10)
language_menu = ttk.Combobox(root, state="readonly")
language_menu.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Select Model:").grid(row=3, column=0, padx=10, pady=10)
model_menu = ttk.Combobox(root, state="readonly")
model_menu.grid(row=3, column=1, padx=10, pady=10)

update_languages()
update_models()

# Bind changes in the Comboboxes to save configuration
model_menu.bind("<<ComboboxSelected>>", save_config_on_change)
language_menu.bind("<<ComboboxSelected>>", save_config_on_change)

# Status label and progress bar
tk.Label(root, textvariable=status_var).grid(row=5, column=0, columnspan=3, padx=10, pady=10)
progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='indeterminate')
progress.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
