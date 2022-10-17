# to-do App

## Features
- create a todo list
- update a todo list
- view todo lists
- archive a todo list
- delete a todo list

- add items to a todo list
- delete items from a todo list
- check items from a todo list

## How to run the app

### first time
1. Create a virtual environment and activate it:
	python3 -m venv venv
	source venv/bin/activate

2. Install the project dependacies from requirements.txt by running the following command in shell: 
	pip install -r requirements.txt 

3. Set-up the database by running:
	export FLASK_APP=flaskr 
	flask init-db

## Run following Commands in shell to run the app.
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
