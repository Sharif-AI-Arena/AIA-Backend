# How to run project

```bash
# install and setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1 # for windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy .env.example .env

# init hooks
pre-commit install
pre-commit run --all-files

# run project
python manage.py migrate
python manage.py createsuperuser # optional
python manage.py runserver
```

## How to lint and format project?

```bash
pre-commit run --all-files
```
