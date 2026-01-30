"""
CLI entry point.
GUI will call processing.pipeline.run_pipeline directly.
"""

import json

from processing.pipeline import run_pipeline


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    input_video = "07.03.mkv"
    output_video = "07.03_output_cut_crf20_veryfast_2.mp4"

    config = load_config("config/config.json")

    run_pipeline(
        input_video=input_video,
        output_video=output_video,
        config=config
    )


if __name__ == "__main__":
    main()
