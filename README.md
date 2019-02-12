# Cartelera Cine

Get the nearest movies in a Cinépolis Theatre, of any given position expressed in coordinates. 

## Objective

This is a little exercise to show some Python functionalities

## Architecture

The program was written in Pyton 2.7.

## Requirements

The requirements are saved in the requirements.txt file.
Also, chromedriver must be installed, check: http://chromedriver.chromium.org/.

Steps to run the script:

1. Create a virtual environment. 

```virtualenv venv```

2. Open the virtual environment and istall the requirements using pip.

```
source venv/bin/activate
pip install -r requirements.txt
```

3. Run the main file.

```
python main.py
```

## Operation range

The information of the movies is only available for the current date (today).

## Functional Diagram

- Step 1. Get the current location.
- Step 2. Get the theatres locations.
- Step 3. Get the nearest theatres locations.
- Step 4. Get the movies from Cinepolis.
- Step 5. Show the results to the user.

