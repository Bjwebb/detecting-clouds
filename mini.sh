sudo -u postgres dropdb clouds4
sudo -u postgres createdb clouds4 -O clouds -E utf8
python manage.py syncdb
python manage.py migrate
python init_db_mini.py
python catsid.py -p 1
python catmatch.py

./timeper.sh
python perimage.py -m4 -o miniout
