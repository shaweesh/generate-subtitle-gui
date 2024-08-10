import argparse
import ffmpeg
import os

def merge_srt_with_mp4(video_file, srt_file, output_file):
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
        .output(output_file, vf='subtitles={}:force_style=\'FontName=Tahoma,PrimaryColour=&H0000FFFF,SecondaryColour=&H00000000,OutlineColour=&H00000000,BackColour=&H00000000,BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginL=10,MarginR=10,MarginV=50\''.format(temp_srt_file))
        .run(overwrite_output=True)
    )

    # Remove temporary SRT file
    if os.path.exists(temp_srt_file):
        os.remove(temp_srt_file)
        print(f'Removed {temp_srt_file}')

def main():
    parser = argparse.ArgumentParser(description='Merge SRT file with MP4 video.')
    parser.add_argument('--video', type=str, required=True, help='Path to input MP4 video file')
    parser.add_argument('--srt', type=str, required=True, help='Path to input SRT subtitle file')
    parser.add_argument('--output', type=str, required=True, help='Path to output MP4 file with embedded subtitles')
    args = parser.parse_args()

    merge_srt_with_mp4(args.video, args.srt, args.output)
    print(f'Successfully merged {args.srt} with {args.video} into {args.output}')

if __name__ == "__main__":
    main()
