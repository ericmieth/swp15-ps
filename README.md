#Setup

* install python3
*  ├> Linux:	via Packagemanager
*  └> Windows:	https://www.python.org/ftp/python/3.4.3/python-3.4.3.msi
*
* install pip
*  ├> Linux:	via easy_install
*  └> Windows:	https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.python3
*
* pip install icalendar simplejson flask flask-wtf flask-sqlalchemy sparqlwrapper

* oder unter Ubuntu

* pip3 install --user icalendar simplejson flask flask-wtf flask-sqlalchemy sparqlwrapper

* um die Dependencies in ein lokales Nutzerverzeichnis unter
*  $HOME/.local/lib/python3.4/site-packages/ zu installieren

* Aber wie man das genau startet ist weder hier noch in der Doku beschrieben, geht aber so:

* python3 app.py
* startet auf localhost:5000 einen lokalen Webserver mit der Applikation.
