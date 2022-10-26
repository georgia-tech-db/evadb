import subprocess
import tempfile
import wave
import json
from vosk import Model, KaldiRecognizer, SetLogLevel
from contextlib import contextmanager


def transcribe_file_with_word_time_offsets(rich_video_file, sample_rate=16000):
    SetLogLevel(-1)
    print("Running Vosk")
    model = Model(lang="en-us")
    rec = KaldiRecognizer(model, sample_rate)

    with get_audio(rich_video_file) as wf:

        rec.SetWords(True)
        rec.SetPartialWords(True)

        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                part_result = json.loads(rec.Result())
                if 'result' in part_result:
                    results += (part_result['result'])

        part_result = json.loads(rec.FinalResult())
        if 'result' in part_result:
            results += (part_result['result'])
        results.append(part_result)

        return results


@contextmanager
def get_audio(file_name):
    outfile = tempfile.NamedTemporaryFile(prefix="temp_extract_audio", suffix=".wav", mode="w+b")
    # TODO: don't use a binary
    subprocess.call(['ffmpeg', '-y', '-i', file_name, outfile.name], stdout="/dev/null")
    try:
        yield wave.open(outfile.name, "rb")
    finally:
        outfile.close()
