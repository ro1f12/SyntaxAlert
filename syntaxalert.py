#!/usr/bin/python3
import keyboard
import argparse, os.path
from threading import Thread
from time import sleep
from utils.data_handlers import open_typo_file

from configparser import ConfigParser
import json

script_path = os.path.dirname(os.path.realpath(__file__))

config_parser = ConfigParser()
config_parser.read( os.path.join( script_path, 'filepath.ini' ))

LIST_OF_FILES = json.loads( config_parser.get( 'DEFAULT', 'words_file' ))
WORDS_FILE_DEFAULT_LOCATION = [ os.path.join( script_path, file_path ) for file_path in LIST_OF_FILES ]

# Load words
def loadWord(filename):
    with open(filename) as json_file:
        words = open_typo_file(json_file)
        return words

# Parse argument
parser = argparse.ArgumentParser(description='Scan your digited letter for wrong words and alert you!')
parser.add_argument('-words', dest='words_file', nargs='?', default=WORDS_FILE_DEFAULT_LOCATION[0], type=str)
parser.add_argument('-words2', dest='words_file2', nargs='?', default=WORDS_FILE_DEFAULT_LOCATION[1], type=str)
args = parser.parse_args()

# it holds the files name passed and the stat os file
files = {}


def loadJSON():
    # Check the file and load it
    if os.path.isfile(args.words_file) is False:
        print('ERR: Words file not exist!')
        exit()

    if args.words_file2 is not None:
        if os.path.isfile(args.words_file2) is not False:
            words = open_typo_file(args.words_file)
            words2 = open_typo_file(args.words_file2)
            words.update(words2)
            # register the status of file in these moment
            files[args.words_file] = os.stat(args.words_file)
            files[args.words_file2] = os.stat(args.words_file2)
    else:
        words = open_typo_file(args.words_file)
        # register the status of file in these moment
        files[args.words_file] = os.stat(args.words_file)

    print(str(len(words)) + " words loaded")
    for (correct, wrongs) in words.items():
        for wrong in wrongs:
            if wrong != '':
                print('Loaded ' + wrong + ' with as: ' + correct)
                keyboard.add_abbreviation(wrong, ' ' + correct + ' ')
    #keyboard.wait()


# Clean the abbreviations from previous JSON and reloads new JSON
def reload_JSON():
    print("Reloading modified JSON!")
    keyboard.unhook_all()
    loadJSON()


def JSON_modify_watcher():
    while True:
        sleep(3)
        for k in files:
            if files[k] != os.stat(k):
                reload_JSON()
                break


loadJSON()
t_watcher = Thread(target=JSON_modify_watcher)
t_watcher.start()
