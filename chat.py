#!/usr/bin/env python

'''
    Wrapper around OpenAI's chat GPT
    Author: Omar Busto Santos 
    Date created: 12/08/2022
'''

from os import environ
import logging

OPENAI_TOKEN = environ.get('OPENAI_TOKEN')

def main():
    print(f"Test {OPENAI_TOKEN}")

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    main()