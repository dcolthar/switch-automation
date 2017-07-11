# This file exists only to provide a means to ensure a consistent
# input vs raw_input method across python2 and python3 platforms


def getInput(prompt="enter a value:"):

    value = None

    # Lets first see if we're dealing with python2 here, if not we'll get a NameError
    try:
        value = raw_input(prompt + "\n")
    except NameError:
        value = input(prompt + "\n")

    return value