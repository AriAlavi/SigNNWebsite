# SigNNWebsite

### After each pull request:
git pull
pip install -r requirements.txt

### After each modification to a models.py file:
python manage.py makemigrations
python manage.py migrate

### After each modification to a static folder(js files, css files, images):
python manage.py collectstatic

### To run server:
python manage.py runserver
open browser, go to url "localhost:8000"

#### Further Documentation: https://docs.djangoproject.com/en/3.0/
