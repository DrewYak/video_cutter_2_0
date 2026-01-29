# main.py

from processing.pipeline import run_pipeline


def main():
    input_video = "07.03.mkv"
    output_video = "07.03_output_2.mp4"

    run_pipeline(input_video, output_video)


if __name__ == "__main__":
    main()
