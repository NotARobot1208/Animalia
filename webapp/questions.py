import requests
#we might not be able to use this
# url = "https://animals-endangered-environmentalism.p.rapidapi.com/population/1"

# querystring = {"type":"equal"}

# headers = {
# 	"X-RapidAPI-Key": "8f6296b82emsh79c42e24801397cp1f82c4jsn98de5dc5175b",
# 	"X-RapidAPI-Host": "animals-endangered-environmentalism.p.rapidapi.com"
# }
# def get_endangered_question(): 
# 	response = requests.request("GET", url, headers=headers)
# 	print(response.text)	
# 	return response.text

def get_animal_question_mc():
    '''
    Gets a multiple choice question from the API.
    '''
    return requests.get("https://opentdb.com/api.php?amount=1&category=27&type=multiple").text

def get_animal_question_bool():
    '''
    Gets a true/false question from the API.
    '''
    return requests.get("https://opentdb.com/api.php?amount=1&type=boolean").text
  
