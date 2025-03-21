## Local Development for TravelCompanion

### Clone this repo

### Setup
MacOS:
```shell
brew install pyenv, pipenv
cat Pipfile | grep python_version
pyenv versions
pyenv install 3.9.6
pyenv local 3.9.6
pipenv --python 3.9.6
pipenv shell
```

### Copy the environment file and install dependencies
```shell
cp .env
pipenv install --dev
python --version  # Должна быть версия из pyenv
pip list  # Должны быть установлены зависимости из Pipfile.lock`
```

### Run the uvicorn server
```shell
uvicorn main:app --reload
```