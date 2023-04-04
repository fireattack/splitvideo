import json
from pathlib import Path
from subprocess import check_output, run


def get_chapter(f):
    cmd = ['ffprobe', '-i', f, '-print_format', 'json', '-show_chapters', '-loglevel', 'error']
    output = check_output(cmd, encoding='utf8')
    chapters = json.loads(output)
    return chapters['chapters']


def split_file(f, encode=False, simulate=True):
    f = Path(f)
    output_dir = f.parent / f.stem
    output_dir.mkdir(exist_ok=True)

    chapters = get_chapter(f)
    for idx, chap in enumerate(chapters, 1):
        idx_str = f"{idx:0{len(str(len(chapters)))}}" # padding it with enough zeroes
        start = chap['start_time']
        end = chap['end_time']
        title = chap['tags']['title']
        output_f = output_dir / f'{idx_str}. {title}{f.suffix}'

        print(f'Chapter {idx_str}, title is {title}, from {start} to {end}, output file: {output_f}')

        if simulate:
            continue

        command = ["ffmpeg", '-loglevel', 'error', '-stats', '-i', f, '-ss', start, '-to', end, '-map_chapters', '-1']
        if encode:
            command.extend(['-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-c:a', 'flac'])
        else:
            command.extend(['-c', 'copy'])
        command.append(output_f)
        run(command)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file")
    parser.add_argument("--encode", '-e', action='store_true', help='re-encode isntead of just copy')
    parser.add_argument("--simulate", '-s', action='store_true', help='simulate')

    args = parser.parse_args()
    split_file(args.input, encode=args.encode, simulate=args.simulate)
