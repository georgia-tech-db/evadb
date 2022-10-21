#!/usr/bin/env python3

import subprocess
import sys
import wave
import json
import io

# from vosk import Model, KaldiRecognizer, SetLogLevel

SAMPLE_RATE = 16000

# SetLogLevel(0)

# model = Model(lang="en-us")
# rec = KaldiRecognizer(model, SAMPLE_RATE)

bashCommand = "ffmpeg -y -i {} output_audio.wav".format(sys.argv[1])
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

def transcribe_file_with_word_time_offsets(speech_file):
    """Transcribe the given audio file synchronously and output the word time
    offsets."""
    from google.cloud import speech

    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_word_time_offsets=True,
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        alternative = result.alternatives[0]
        print("Transcript: {}".format(alternative.transcript))

        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time

            print(
                f"Word: {word}, start_time: {start_time.total_seconds()}, end_time: {end_time.total_seconds()}"
            )

transcribe_file_with_word_time_offsets("output_audio.wav")
