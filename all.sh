python generate_symlinks.py www.mrao.cam.ac.uk sym
cd sym/2011
rm -r 01 02 03/{01,03,04,05,06,07,08,16,19,20,21,23,24}
cd ../../


python process.py -l process.log -mv --log-images

python generate_symlinks.py -sid out/fits_filtered/sym sid
python process.py -mv -i sid --no-filter --no-output --total

# echo "CREATE EXTENSION orafce;" | sudo -u postgres psql clouds2
python manage.py syncdb
python manage.py migrate
python init_db.py
python catsid.py
python catmatch.py

python process.py --sum-db --no-filter -i out/fits_filtered/sym -m

./timeper.sh > log/meta
python perimage.py -m4 -o out 
python perimage_todb.py
cd out
for f in perimage-*/; do cat $f/201* > `basename $f`-data; done
