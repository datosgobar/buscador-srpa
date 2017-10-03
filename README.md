# buscador-srpa
Pequeño servidor para clasificar o buscar textos similares para los informes mensuales del poder ejecutivo al congreso de la nación argentina. 

## Instalación del servidor

Instalación de dependencias
```
sudo apt-get install git-all python-pip python-dev build-essential sqlite3 libsqlite3-dev
pip install virtualenv
git clone https://github.com/datosgobar/text-classifier.git
cd text-classifier/
virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt

```

## Para desarrollo

### Crear la base de datos

```
. venv/bin/activate
python main.py create_db
```

### Crear usuarios

```
. venv/bin/activate
python main.py create_user
```
### Asignar un rol a un usuario

```
. venv/bin/activate
python main.py add_user_role
```

### Levantar el server:

Hay un script de bash de ejemplo para levantar el server llamado `runserver.sh.sample`.

### Compilar scss
Dentro de la carpeta `app/static/style` ejecutar `sass --watch app.scss:app.css`

### SMTP
Para levantar un servidor smtp para desarrollo, correr `sudo python -m smtpd -n -c DebuggingServer localhost:25`

### i18n

Cada vez que se agreguen, remuevan o modifiquen textos traducibles, ejecutar lo siguiente parado dentro de la carpeta `app` ejecutar:
```
pybabel extract -F translations/babel.cfg -o translations/messages.pot .
pybabel update -i translations/messages.pot -d translations
```

Esto actualiza los archivos `app/translations/messages.pot` y `app/translations/es/LC_MESSAGES/messages.po`.
Editar este ultimo con las traducciones pertinentes y ejecutar `pybabel compile -d translations` para compilar las traducciones.


### Documentaciones relevantes:
- [Flask Mail](https://pythonhosted.org/Flask-Mail/)
- [Flask User](https://pythonhosted.org/Flask-User/)
- [Flask SQLAlchemy](http://flask-sqlalchemy.pocoo.org/)
- [Flask Babel](https://pythonhosted.org/Flask-Babel/)
- [Flask WTF](http://flask.pocoo.org/docs/0.11/patterns/wtforms/)
- [Poncho](http://argob.github.io/poncho/)

## Contacto
Te invitamos a [crearnos un issue](https://github.com/datosgobar/text-classifier/issues/new?title=Encontre%20un%20bug) en caso de que encuentres algún bug o tengas comentarios sobre el proyecto o el cdigo del repositorio. Para todo lo demás, podés mandarnos tu comentario o consulta a [datos@modernizacion.gob.ar](mailto:datos@modernizacion.gob.ar).
