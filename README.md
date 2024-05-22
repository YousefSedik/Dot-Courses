# Dot Course

Dot Course is a E-Learning platform, you can buy course or request access to an instructor on Dot Course!  

- Easy To Use 

## Features

- You easily search for a course using it's name, content, description.
- You can add rates, get certificates upon finishing the course exams. 


## Tech

"Dot Course" uses a number of open source projects to work properly:

- [Bootstrap5] - HTML enhanced for web apps!
- [VS-Code] - main text editor
- [HTMX] - for sending AJAX requests
- [Django] - for backend sever side 
- [SQLITE3] as the main db 

And of course Dot Course" itself is open source with a [public repository](https://github.com/YousefSedik/Dot-Course/) on GitHub.

## Installation

Dot Course requires [Python](https://www.python.org/downloads/) v3+ a to run.

Create A Virtual Enviroment 
```sh
pip install venv 
python -m venv venv
```
Activate The Virtual Enviromnent 
```sh
\venv\Scripts\activate.bat
```
Create The .env file in the root dir
```
touch .env 
```
Setup this variables in the .env file 
```
SECRET_KEY=''
DEBUG=''
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
EMAIL_HOST=""
EMAIL_PORT=   
EMAIL_USE_TLS=''
```

Install the dependencies and devDependencies
```sh
pip install -r requirements.txt
py manage.py migrate 
```
Then You Can Run The Development Directly Using
```sh
py manage.py runserver  
```

