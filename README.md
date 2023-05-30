# Security_facial_authentication

python -m venv <env_name>

<env_name>\Scripts\activate

pip install cmake==3.25.0

download dlip wheel from this link with the approbriate version of your python
"https://drive.google.com/file/d/1HChwXxIolDl1KEMb9Iz9DD6V8aULhN5g/view"

pip install face_regognition

pip install -R requirements.txt

now to the django server setup :

# setup your postgres data base in the settings 
 DATABASES = {   
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '8000',
    }
}

python manage.py makemigrations

python manage.py migrate 

python manage.py runserver 

# in an another terminal we launch the web app server

make ur way to the \face-attendance-web-app-front using the cd commands

delete package-lock.json

pip install npm 

# you might need to follow some recomondation that you will find on your terminal and brute force 
# packages changes

npm start 

# You may need to adjust your browser to allow access to your webcam through an unsecure conection from the EC2 ip address. In chrome this setting is adjusted here chrome://flags/#unsafely-treat-insecure-origin-as-secure.
