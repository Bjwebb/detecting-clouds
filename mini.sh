sudo -u postgres dropdb clouds4
sudo -u postgres createdb clouds4 -O clouds -E utf8
python manage.py syncdb
python manage.py migrate
python init_db_mini.py
python catsid.py -p 1
python catmatch.py

python perline.py -g 1 
python perline.py -g 1 -ftn
python perline.py -g 2 
python perline.py -g 2 -ft
python perline.py -g 3 
python perline.py -g 3 -ft
python perline.py -g 4
python perimage.py -m4 -o miniout

