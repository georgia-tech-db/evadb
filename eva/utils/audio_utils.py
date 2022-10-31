import subprocess
import tempfile
import wave
import json
from vosk import Model, KaldiRecognizer, SetLogLevel
from contextlib import contextmanager
from pydub import AudioSegment


def transcribe_file_with_word_time_offsets(rich_video_file):
    SetLogLevel(-1)
    print("Running Vosk")
    model = Model(lang="en-us")

    with get_audio(rich_video_file) as wf:
        rec = KaldiRecognizer(model, wf.getframerate())
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

        # sometimes there are bugs in recognition, and
        # the library returns an empty dictionary {'text': ''}
        return [result for result in results if len(result) == 4]


@contextmanager
def get_audio(file_name):
    outfile_stereo = tempfile.NamedTemporaryFile(prefix="temp_extract_audio_stereo", suffix=".wav", mode="w+b")
    outfile = tempfile.NamedTemporaryFile(prefix="temp_extract_audio", suffix=".wav", mode="w+b")
    # TODO: don't use a binary
    subprocess.call(['ffmpeg', '-y', '-i', file_name, outfile_stereo.name], stdout=None)
    mono_audio = AudioSegment.from_wav(outfile_stereo.name)
    mono_audio = mono_audio.set_channels(1)
    mono_audio.export(outfile, format="wav")
    try:
        yield wave.open(outfile.name, "rb")
    finally:
        outfile.close()
