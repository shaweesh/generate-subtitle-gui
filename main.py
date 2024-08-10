import argparse
import ffmpeg
from faster_whisper import WhisperModel
import os

# Function to extract audio from video
def extract_audio(input_video, output_audio="audio.wav"):
    ffmpeg.input(input_video).output(output_audio, format='wav').run(overwrite_output=True)
    return output_audio

# Function to transcribe audio to subtitles
def transcribe_audio(audio_file, language='he'):
    model = WhisperModel("large", device="cpu")  # Use a smaller model and run on CPU
    segments, _ = model.transcribe(audio_file, language=language)  # Correct language code
    return segments

# Function to generate SRT file from transcription
def generate_srt(segments, output_file='subtitles.srt', min_display_duration=1.0):
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments):
            start_time = segment.start
            end_time = segment.end
            text = segment.text.strip()

            # Calculate the adjusted end time based on the minimum display duration
            adjusted_end_time = start_time + max(end_time - start_time, min_display_duration)

            # Format time in SRT format
            start_time_str = f"{int(start_time // 3600):02}:{int((start_time % 3600) // 60):02}:{int(start_time % 60):02},{int((start_time % 1) * 1000):03}"
            end_time_str = f"{int(adjusted_end_time // 3600):02}:{int((adjusted_end_time % 3600) // 60):02}:{int(adjusted_end_time % 60):02},{int((adjusted_end_time % 1) * 1000):03}"

            # Write to SRT file
            f.write(f"{i + 1}\n{start_time_str} --> {end_time_str}\n{text}\n\n")

def process_video(input_video, output_srt, language='he', min_display_duration=1.0):
    audio_file = extract_audio(input_video)
    segments = transcribe_audio(audio_file, language)
    generate_srt(segments, output_srt, min_display_duration)

    # Clean up the audio file
    if os.path.exists(audio_file):
        os.remove(audio_file)
        print(f'Removed {audio_file}')

def main():
    parser = argparse.ArgumentParser(description='Generate SRT file from video.')
    parser.add_argument('--input', type=str, required=True, help='Path to input video file')
    parser.add_argument('--output', type=str, required=True, help='Path to output SRT file')
    parser.add_argument('--language', type=str, default='he', help='Language code for transcription')
    parser.add_argument('--min_display_duration', type=float, default=1.0, help='Minimum display duration for subtitles in seconds')
    args = parser.parse_args()

    process_video(args.input, args.output, args.language, args.min_display_duration)

if __name__ == "__main__":
    main()
