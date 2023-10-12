# LSC Backend

## Description
This project will be the backend for the internal logiscool application. It is a django rest framework application that serves as an endpoint for a future React app.

## Requirements
- python 3.8 or higher (3.10 recommended)
- visual studio code or pycharm
- git (2.34.1 or latest)

## Setup
- create a folder in your machine, and using the terminal (cmd) go to the folder location 

    ```cd C:/MY/LOCATION/PATH```
- clone the repository using the following command: 

  ``` git clone https://github.com/gabi-theo/lsc_backend.git ```
  
  provide credentials from github account if required

- go to your cloned repo (cd lsc_backend)
- create a python virtual environment, activate it and install needed python packages:

```
pip install virtualenv 

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

Python will read and install the needed packages from the requirements.txt file. A virtual environment is needed to be sure that we all use the same versions of libraries and not to mix with other python libraries that already exists into your system.

## Running django app
To run the local server for development and testing you need to follow these steps:

### Create the database

```
python manage.py makemigrations
python manage.py migrate
```

These commands will read the models from your app, create the migration files and then a local sqlite database. More about django migrations can be read here: https://docs.djangoproject.com/en/4.2/topics/migrations/
Also, it`s important to run these 2 commands everytime you make changes to your models.py file.


### Create a superuser
This is needed to acces the admin interface.

```
python manage.py createsuperuser
```
and fill the required fields

### Run the local server
In order to test the application locally, you can run the following command:

```
python manage.py runserver
```
Application can be accessed on http://127.0.0.1:8000
By going to http://127.0.0.1:8000/admin you will be able to login to the admin interface with the user and password you created on the previous step.

### Running and testing end-points
In order to test the end-points you have to options.
1. Use Postman and make request to http://127.0.0.1:8000/api/YOUR_ENDPOINT
2. You can directly access http://127.0.0.1:8000/api/YOUR_ENDPOINT in your browser, where django provides a nice UI for testing the end-points.


## Development and git
Everytime you want to work on a new task, follow the next steps:
1. Be sure you have the latest approved version of code by:
```
git checkout main
git pull
```
2. Checkout to a branch with a name related to your task. If you have a task called, for example "Implement a login end-point", you should:
```
git checkout -b feat/login_endpoint
```
and start work.
"git checkout -b BRANCH_NAME" is needed only when you create a new branch. If the branch already exists, you can "git checkout BRANCH_NAME" without using "-b"

3. After you are done with your task, you should:
- let git be aware of your changes with 
```
git add .
```
- check the status of you branch to be sure that you don`t add not needed files/scripts/passwords/etc in your remote branch, with:
```
git status
```
- create a commit with usefull information. A commit, will help everybody from the team to easily see what you did in your branch, if the commit has a good and short description. For example:
```
git commit -m "Added an endpoint for user loggin"
```
- finally, create a merge request so your code can be reviewed and merged to the main branch
```
git push origin/NAME_OF_YOUR_BRANCH
```

4. After that, when working on a new task, repeat the steps from this section
