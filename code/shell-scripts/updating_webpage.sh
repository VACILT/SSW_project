# Kopiere zunächst den gesamten Inhalt des Ordners _build/html in den Ordner /docs
cp -r /home/hochatmstud/bene/testbook/_build/html/. /home/hochatmstud/bene/docs/
# Wechsle zum Branch master, falls notwendig
git checkout master
# Aktualisiere nun den Ordner docs in das lokale git Repository
git add docs/
# Mache den Commit
git commit -m 'updating webpage contents to /docs'
# Und pushe nun den Branch master
git push