#!/usr/bin/env python3

import subprocess
import sys
import wave
import json

from vosk import Model, KaldiRecognizer, SetLogLevel

SAMPLE_RATE = 16000

SetLogLevel(0)

model = Model(lang="en-us")
rec = KaldiRecognizer(model, SAMPLE_RATE)

bashCommand = "ffmpeg -y -i {} output_audio.wav".format(sys.argv[1])
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

wf = wave.open("output_audio.wav", "rb")
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
print(json.dumps(results, indent=1))

# with subprocess.Popen(["ffmpeg", "-loglevel", "quiet", "-i",
#                             sys.argv[1],
#                             "-ar", str(SAMPLE_RATE) , "-ac", "1", "-f", "s16le", "-"],
#                             stdout=subprocess.PIPE) as process:

#     while True:
#         data = process.stdout.read(4000)
#         if len(data) == 0:
#             break
#         if rec.AcceptWaveform(data):
#             print(rec.Result())
#         else:
#             print(rec.PartialResult())

#     print(rec.FinalResult())
