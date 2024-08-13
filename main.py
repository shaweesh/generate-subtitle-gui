import os
import ffmpeg
from faster_whisper import WhisperModel

# Allow multiple OpenMP runtimes (temporary workaround)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class SubtitleGenerator:
    def __init__(self, model='large', translate_to=None):
        self.model = WhisperModel(f"{model}-v3", device="cpu")
        self.translate_to = translate_to

    def extract_audio(self, input_video, output_audio="audio.wav"):
        ffmpeg.input(input_video).output(output_audio, format='wav').run(overwrite_output=True)
        return output_audio

    def transcribe_audio(self, audio_file, language='he'):
        segments, _ = self.model.transcribe(audio_file, language=language)
        if self.translate_to and self.translate_to != language:
            # Perform translation (example)
            # You need to integrate a translation API or library here
            pass
        return segments

    def generate_srt(self, segments, output_file='subtitles.srt', min_display_duration=1.0):
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments):
                start_time = segment.start
                end_time = segment.end
                text = segment.text.strip()

                adjusted_end_time = start_time + max(end_time - start_time, min_display_duration)

                start_time_str = f"{int(start_time // 3600):02}:{int((start_time % 3600) // 60):02}:{int(start_time % 60):02},{int((start_time % 1) * 1000):03}"
                end_time_str = f"{int(adjusted_end_time // 3600):02}:{int((adjusted_end_time % 3600) // 60):02}:{int(adjusted_end_time % 60):02},{int((adjusted_end_time % 1) * 1000):03}"

                f.write(f"{i + 1}\n{start_time_str} --> {end_time_str}\n{text}\n\n")

    def process_video(self, input_video, output_srt, language='he', min_display_duration=1.0):
        audio_file = self.extract_audio(input_video)
        segments = self.transcribe_audio(audio_file, language)
        self.generate_srt(segments, output_srt, min_display_duration)

        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f'Removed {audio_file}')

    def process_audio(self, input_audio, output_srt, language='he', min_display_duration=1.0):
        segments = self.transcribe_audio(input_audio, language)
        self.generate_srt(segments, output_srt, min_display_duration)
