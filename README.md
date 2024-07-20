# Clean Members Script
This directory contains a script, `clean_members.py` that is used to automatically clean the membership data for the University of Toronto Mississauga Physics Club. The script will read in all the data from the first sheet of the `members_list` google sheet and then output a cleaned version of the data to the second sheet of the same google sheet.

## Usage
I have set up a server to automatically run this script every day at 12:00 AM EST. It can also be run manually by running the following command in a terminal:
```bash
python clean_members.py
```

### Credentials
The script requires a `key_secret.json` file to authenticate with the google sheet. This file should be placed in the same directory as the script. You will need to set up your own google project and create a credentials file. This can be done from the google cloud console by following the instructions [here](https://www.youtube.com/watch?v=w533wJuilao).

### Dependencies
Create a virtual environment and run the following command to install the required dependencies:
```bash
pip freeze > requirements.txt
```
Note that I used Python version 3.10.2 for this project, but the script should work with any version of Python 3 (I have not tested it with Python 2).

If you are not familiar with virtual environments, you can follow a quick guide online or learn more from my article here: [Python Virtual Environments](https://medium.com/towardsdev/managing-virtual-environments-with-different-python-interpreters-b997b7bb7254).

## Files

`clean_members.py` : The script which does the cleanings.

`key_secret.json` : The credentials file for the google sheet. This file should be placed in the same directory as the script.