#Setup & Generierung der Dokumentation

Installation:
	pip install sphinx
	
Automatisches Hinzufügen von Modulen (Dateien):
	sphinx-apidoc -o <Output-Ordner> <Modul-Ordner>

Kompilieren der Dateien in HTML-Format:
	Für alle Plattformen:
		make html
	
	Zum Aufräumen:
		make clean

	Die kompilierten Dateien sind im _build Ordner (sofern nicht anders angegeben wurde).
	Die Datei html/index.html ist die Startseite des Projekts