import requests
import json
def get_animal_question_mc(asked_questions):
    '''
    Gets a multiple choice question from the API.
    '''
    while True:
        fullq = requests.get("https://opentdb.com/api.php?amount=1&category=27&type=multiple").text
        if not json.loads(fullq)['results'][0]['question'] in asked_questions:
            fullq = requests.get("https://opentdb.com/api.php?amount=1&category=27&type=multiple").text
            break

    return fullq