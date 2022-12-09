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
    'authorization': f'Bearer {OPENAI_TOKEN}'
}

def create_answer_json_response(answer, error, cause):
    """ Creates the json response for the conversation answer """
    return {
        "error": error,
        "cause": cause,
        "answer": answer
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
    return json_formatted["message"]["content"]["parts"][0]

def request_answer_as_json(prompt):
    """ Given a prompt, requests the OpenAI api for an answer and returns it as a json object """
    try:
        r = requests.post(API_CONVERSATION, json=create_post_payload(prompt), stream=True, headers=headers)
        r.raise_for_status()
        answer = extract_response(r.iter_lines(delimiter=b'\n'))
        return json.dumps(create_answer_json_response(answer, False, ""))
    except (requests.exceptions.HTTPError, IndexError) as e:
        return json.dumps(create_answer_json_response("Error", True, str(e)))
    except KeyError as e:
        return json.dumps(create_answer_json_response("Error", True, f"Key: {str(e)} not found."))

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

    answer = request_answer_as_json(args.prompt)
    print("\n")
    print(answer if args.debug else json.loads(answer)['answer'])
    print("\n")

if __name__ == "__main__":
    main()