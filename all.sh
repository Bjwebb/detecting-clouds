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

python perline.py -g 1
python perline.py -g 1 -f
python perline.py -g 2
python perline.py -g 2 -f
python perline.py -g 3
python perimage.py -m4 -o out 

