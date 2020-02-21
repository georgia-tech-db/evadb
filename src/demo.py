# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from cmd import Cmd
import matplotlib
import random
import glob
from PIL import Image
from src.query_parser.eva_parser import EvaFrameQLParser

import sys
sys.path.append('.')
matplotlib.use('TkAgg')


class EVADemo(Cmd):

    def default(self, query):
        """Takes in SQL query and generates the output"""

        # Type exit to stop program
        if(query == "exit" or query == "EXIT"):
            raise SystemExit

        if len(query) == 0:
            print("Empty query")

        else:
            try:
                # Connect and Query from Eva
                parser = EvaFrameQLParser()
                eva_statement = parser.parse(query)
                select_stmt = eva_statement[0]
                print("Result from the parser:")
                print(select_stmt)
                print('\n')

                # Read Input Videos
                # Replace with Input Pipeline once finished
                input_video = []
                for filename in glob.glob('data/sample_video/*.jpg'):
                    im = Image.open(filename)
                    # to handle 'too many open files' error
                    im_copy = im.copy() 
                    input_video.append(im_copy)
                    im.close()

                # Write Output to final folder
                # Replace with output pipeline once finished
                ouput_frames = random.sample(input_video, 50)
                output_folder = "data/sample_output/"

                for i in range(len(ouput_frames)):
                    frame_name = output_folder + "output" + str(i) + ".jpg"
                    ouput_frames[i].save(frame_name)

                print("Refer pop-up for a sample of the output")
                ouput_frames[0].show()

            except TypeError:
                print("SQL Statement improperly formatted. Try again.")

    def do_quit(self, args):
        """Quits the program."""
        print("Quitting.")
        raise SystemExit


if __name__ == '__main__':
    prompt = EVADemo()
    prompt.prompt = '> '
    prompt.cmdloop('Starting EVA...')
