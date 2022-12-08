#!/usr/bin/env python

'''
    Wrapper around OpenAI's chat GPT
    Author: Omar Busto Santos 
    Date created: 12/08/2022
'''

from os import environ
import http.client
import sys, argparse
import logging
import requests
import json
import uuid

OPENAI_TOKEN = environ.get('OPENAI_TOKEN')
API_CONVERSATION = "https://chat.openai.com/backend-api/conversation"
STREAM_PREFIX = "data: "

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
    'origin': 'https://chat.openai.com',
    'referer': 'https://chat.openai.com/chat',
    'content-type': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'authority': "chat.openai.com",
    'accept': 'text/event-stream',
    'authorization': OPENAI_TOKEN
}

def create_post_payload(prompt):
    """ Creates a payload for OpenAI chat api given a prompt """
    return {
        'action': 'next',
        'model': 'text-davinci-002-render',
        'parent_message_id': str(uuid.uuid4()),
        'messages': [ 
            {
                'id': str(uuid.uuid4()),
                'role': 'user',
                'content': {
                    'content_type': 'text',
                    'parts': [ 
                        prompt
                    ]
                }
            } 
        ]
    }

def extract_response(stream_data):
    """ Given a stream data as an iterator of lines, extract the final response """
    lines = [line.decode('utf-8').strip() for line in list(stream_data) if line]
    json_formatted = json.loads(lines[-2][len(STREAM_PREFIX):])
    print(json_formatted["message"]["content"]["parts"][0])

def main():
    parser = argparse.ArgumentParser(description='Send a prompt to OpenAI\'s chat API')
    parser.add_argument('-p', '--prompt', help='Prompt for the AI', type=str, required=True)
    parser.add_argument('-d', '--debug', help='Executes in debug mode with more logs', action='store_true', required=False)
    args = parser.parse_args()

    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    if args.debug:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.StreamHandler())
        http.client.HTTPConnection.debuglevel = 1

    r = requests.post(API_CONVERSATION, json=create_post_payload(args.prompt), stream=True, headers=headers)
    extract_response(r.iter_lines(delimiter=b'\n'))

if __name__ == "__main__":
    main()