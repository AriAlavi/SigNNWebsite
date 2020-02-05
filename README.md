# SigNNWebsite

### After each pull request:
git pull&nbsp;
pip install -r requirements.txt&nbsp;

### After each modification to a models.py file:
python manage.py makemigrations&nbsp;
python manage.py migrate&nbsp;

### After each modification to a static folder(js files, css files, images):
python manage.py collectstatic

### To run server:
python manage.py runserver&nbsp;
open browser, go to url "localhost:8000"&nbsp;

#### Further Documentation: https://docs.djangoproject.com/en/3.0/
