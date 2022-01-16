import pypiano.keyboard
import pyttsx3
import os
import logging
from pypiano import Piano
from pypiano.keyboard import PianoKeyboard, PianoKey
from moviepy.editor import AudioFileClip, ImageClip
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont

# Initialize module logger
LOGGER_NAME = "note_generator"
logger = logging.getLogger(LOGGER_NAME)
logger.addHandler(logging.NullHandler())

RESULT_BASE_DIR = "./results"
PIANO_SOUND_DIR = "key_sounds"
PIANO_KEY_SPEECH_DIR = "key_speech"
PIANO_KEY_IMAGES_DIR = "key_images"
FINAL_SOUNDS_DIR = "key_full_sounds"
FINAL_FILE_DIR = "final"

VOICE_ID = 0
VOLUME = 1

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
TEXT_SIZE = 100
BACKGROUND_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

def map_key_to_speakable_string(key: pypiano.keyboard.PianoKey) -> str:
    return key.full_note_string.replace("#", " Sharp ").replace("b", " Flat ").replace("-", "").replace("/", " ")


def remove_file_if_exists(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)


def generate_piano_key_sound_file(key: PianoKey) -> None:
    print(f"Generating piano key sound for: {key}")
    piano = Piano()
    key_id = key.key_index
    note_path_wav = f"{RESULT_BASE_DIR}/{PIANO_SOUND_DIR}/{key_id}.wav"
    remove_file_if_exists(note_path_wav)
    note_to_play = key.get_as_note()
    piano.play(note_to_play, recording_file=note_path_wav, record_seconds=2)
    note_wav = AudioSegment.from_wav(note_path_wav)
    note_path_mp3 = note_path_wav.replace(".wav", ".mp3")
    note_wav.export(note_path_mp3, format="mp3")
    remove_file_if_exists(note_path_wav)
    print(f"DONE Generating piano key sound for: {key}")


def generate_piano_key_speech_sound_file(key: PianoKey) -> None:
    print(f"Generating piano key speech for: {key}")
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('rate', VOLUME)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[VOICE_ID].id)
    key_id = key.key_index
    speech_path_wav = f"{RESULT_BASE_DIR}/{PIANO_KEY_SPEECH_DIR}/{key_id}.wav"
    remove_file_if_exists(speech_path_wav)
    speakable_text = map_key_to_speakable_string(key)
    engine.save_to_file(speakable_text, speech_path_wav)
    engine.runAndWait()
    note_speech_wav = AudioSegment.from_file(speech_path_wav)
    note_speech_path_mp3 = speech_path_wav.replace(".wav", ".mp3")
    note_speech_wav.export(note_speech_path_mp3, format="mp3")
    remove_file_if_exists(speech_path_wav)
    print(f"DONE Generating piano key speech for: {key}")


def generate_piano_key_text_image_file(key: PianoKey) -> None:
    key_id = key.key_index
    image_path = f"{RESULT_BASE_DIR}/{PIANO_KEY_IMAGES_DIR}/{key_id}.png"
    remove_file_if_exists(image_path)
    img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Arial.ttf", TEXT_SIZE)
    draw.text((IMAGE_WIDTH / 2, IMAGE_HEIGHT / 2), key.full_note_string, fill=(255, 255, 255), font=font)
    img.save(image_path)


def merge_mp3_files(key: PianoKey, pause: int) -> None:
    key_id = key.key_index
    final_path = f"{RESULT_BASE_DIR}/{FINAL_SOUNDS_DIR}/{key_id}.mp3"
    note_path_mp3 = f"{RESULT_BASE_DIR}/{PIANO_SOUND_DIR}/{key_id}.mp3"
    speech_path_mp3 = f"{RESULT_BASE_DIR}/{PIANO_KEY_SPEECH_DIR}/{key_id}.mp3"
    note_sound = AudioSegment.from_file(note_path_mp3)
    note_speech = AudioSegment.from_file(speech_path_mp3)
    pause_sound = AudioSegment.silent(duration=pause)
    sound_with_gap = note_sound + pause_sound + note_speech
    sound_with_gap.export(final_path, format="mp3")


def generate_video_file_from_image_and_audio(key: PianoKey) -> None:
    key_id = key.key_index
    image_path = f"{RESULT_BASE_DIR}/{PIANO_KEY_IMAGES_DIR}/{key_id}.png"
    audio_path = f"{RESULT_BASE_DIR}/{FINAL_SOUNDS_DIR}/{key_id}.mp3"
    final_path = f"{RESULT_BASE_DIR}/{FINAL_FILE_DIR}/{key_id}.mp4"
    remove_file_if_exists(final_path)
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path)
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.duration = audio_clip.duration
    video_clip.fps = 1
    video_clip.write_videofile(final_path, audio_codec="aac")


def main() -> None:
    piano_keyboard = PianoKeyboard()
    for idx, key in enumerate(piano_keyboard):
        generate_piano_key_sound_file(key)
        generate_piano_key_speech_sound_file(key)
        merge_mp3_files(key, pause=1)
        generate_piano_key_text_image_file(key)
        generate_video_file_from_image_and_audio(key)


if __name__ == "__main__":
    main()


