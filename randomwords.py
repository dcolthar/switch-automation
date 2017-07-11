# Generate a random word passphrase

from __future__ import print_function
from getinput import getInput as getinput
from random_words import RandomWords
import random
import sys

class RandomWordsClass():

    def __init__(self):
        self.rw = RandomWords()

    def randomWordsPrint(self, count=5):
        # Blank string to get it started
        fullPassword = ""
        # to count loop iterations
        loopCounter = 0

        # Create a list of random words
        wordList = self.rw.random_words(count=int(count))
        # Iterate through the list and append to each other
        for i in wordList:
            loopCounter += 1
            if loopCounter < len(wordList):
                fullPassword += (i + str(random.randint(1,10)) + '-')
            else:
                fullPassword += i.upper() + str(random.randint(1,100))
        print(fullPassword)


rand = RandomWordsClass()
if len(sys.argv) > 1:
    rand.randomWordsPrint(count=sys.argv[1])
else:
    rand.randomWordsPrint(count=3)
