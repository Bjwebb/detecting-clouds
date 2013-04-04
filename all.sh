python generate_symlinks.py www.mrao.cam.ac.uk sym
cd sym/2011
rm -r 01 02 03/{01,03,04,05,06,07,08}
cd ../../


python process.py -l process.log -mv --log-images -c

python generate_symlinks.py -sid out/fits_filtered/sym sid
python process.py -mv -i sid --no-filter --no-output --total

python manage.py syncdb
python manage.py migrate
python init_db.py
python catsid.py
python catmatch.py

python process.py --sum-db --no-filter -i out/fits_filtered/sym -m

python perline.py
python db_filter.py
python perline.py -g 2
python perimage.py multi
