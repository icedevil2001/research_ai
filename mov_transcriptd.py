#!/usr/bin/env python3

import click
from rich.console import Console
from rich.progress import Progress
from loguru import logger
from pathlib import Path
from tempfile import TemporaryDirectory
import openai 

from moviepy.editor import VideoFileClip
from pydub import AudioSegment


def convert_mov_to_mp3(mov_file: str, mp3_file: str) -> str:
    clip = VideoFileClip(mov_file)
    clip.audio.write_audiofile(mp3_file)
    clip.close()
    logger.info(f"Converted {mov_file} to {mp3_file}")
    ## compress the mp3 file
    return mp3_file 


def convert_mp3_to_text(mp3_file: str, text_file: str) -> str:
    openai.api_key = "sk-1234"
    response = openai.File.create(file=open(mp3_file), purpose="transcription")
    with open(text_file, "w") as f:
        f.write(response.text)
    logger.info(f"Converted {mp3_file} to {text_file}")
    return text_file


def split_audio(mp3_file: str, split_file: str) -> str:


    if Path(mp3_file).stat().st_size > (25 * (1024**2)): ## larger than 25 Mb
        logger.info(f"Splitting {mp3_file} into {split_file}")
        # audio_file.export(split_file, format="mp3")

        return split_file
    
    
    audio_file = AudioSegment.from_file(mp3_file, format="mp3")
    duration = len(audio_file)  



    # # song = AudioSegment.from_mp3(mp3_file)
    # ten_minutes = 10 * 60 * 1000
    # first_10_minutes = song[:ten_minutes]
    # first_10_minutes.export(split_file, format="mp3")
    # logger.info(f"Split {mp3_file} into {split_file}")
    # return split_file
