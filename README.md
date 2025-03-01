# *πchan - Anonymous imageboard implemented in Flask and SQLite3*

# 1. Running the app

The command lines on the setup proccess instructions where written assuming you're trying to run the app on a linux system and some commands might not work on Windows.

- ## 1.1. With Docker
    Assuming you already have Docker installed on your machine there are really very few steps to be followed to get the application running.

    - ### 1.1.1. Building the Docker image from the Dockerfile

        The first command you'll have to run will be the command that builds the image that runs the application from the [Dockerfile](Dockerfile).

        Before running it, make sure you're on the root of the application's folder, then you can run the following command: `docker build -t pichan .`

        After running it succesfully Docker will have built an image based on the [Dockerfile](Dockerfile).

    - ### 1.1.2. Creating a container with the Docker image

        With the image ready now we need to create a container with it, to do it you can simply run `docker run -dp 5000:5000 pichan` if you just intend to test the app, or you can also run `docker run -dp 5000:5000 -w /app -v "$(pwd):/app" pichan:latest` wich will use the local project's folder as a volume, making it easier to debug if you intend to change anything in the code.

    After that the project will be running on http://localhost:5000.

- ## 1.2. Without Docker
    Without Docker we will be manually doing what the docker image and conatiner do and that's why there will be a few more commands to run but it should still be simple.

    - ### 1.2.1. Creating the python virtual environment

        To create the venv simply run `python -m venv venv`, after the venv is created you should run `source ./venv/bin/activate` wich will activate the environment and allow you to modify the new environment's libraries.

    - ### 1.2.2. Installing the project's required libraries/frameworks
        
        With the activated environment, in order to install all dependencies the project needs to run you can run the command `pip install -r requirements.txt` wich will automatically install all libraries listed on the [requirements.txt](requirements.txt) file.

    - ### 1.2.3. Running the app

        After installing the dependencies all you'll have to do is run `flask run` in the activated environment.

    After that the project will be running on http://localhost:5000.


# 2. Overview of all page templates

- ## 2.1. Home

- ## 2.2. Board

- ## 2.3. Thread


# 3. Using the system as administrator

- ## 3.1. Logging to the system with and API key

- ## 3.2. Creating/Deleting board groups and boards from the home endpoint

- ## 3.3. Administrating boards, threads and replies


# 4. Using the system as a normal anonymous user

- ## 4.1. Accesing the home endpoint


# 5. Posting threads and/or replies


# 6. Submitting votes on threads and/or replies
