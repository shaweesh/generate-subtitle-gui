import os
import ffmpeg

# Allow multiple OpenMP runtimes (temporary workaround)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class SRTMerger:
    def merge_srt_with_mp4(self, video_file, srt_file, output_file):
        # Ensure the SRT file is read with UTF-8 encoding
        with open(srt_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()

        # Write the content back to a new SRT file to ensure encoding is correct
        temp_srt_file = 'temp_subtitles.srt'
        with open(temp_srt_file, 'w', encoding='utf-8') as f:
            f.write(srt_content)

        # Use FFmpeg to merge the video and subtitles with additional options
        (
            ffmpeg
            .input(video_file)
            .output(
                output_file,
                vf='subtitles={}:force_style=\'FontName=Tahoma,Bold=1,PrimaryColour=&H0000FFFF,SecondaryColour=&H00000000,OutlineColour=&H00000000,BackColour=&H000000FF,BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginL=10,MarginR=10,MarginV=50,Box=1,BoxColor=&HFF000000,BoxBorderStyle=1\''.format(temp_srt_file)
            )
            .run(overwrite_output=True)
        )

        # Remove temporary SRT file
        if os.path.exists(temp_srt_file):
            os.remove(temp_srt_file)
            print(f'Removed {temp_srt_file}')
