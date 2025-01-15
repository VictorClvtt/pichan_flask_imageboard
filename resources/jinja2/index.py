import requests
from flask import render_template
from flask_smorest import Blueprint
from models.board_group import BoardGroupModel

blp = Blueprint('Index', __name__, description='Index Homepage')

@blp.route('/')
def home():
    # Fetch data from the API
    api_url = 'http://127.0.0.1:5000/board_group'
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        board_groups = response.json()  # Parse the JSON data from the API
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        board_groups = []  # Fallback to empty list in case of error
    
    # Render the template and pass the board_groups data
    return render_template('index.html', board_groups=board_groups)