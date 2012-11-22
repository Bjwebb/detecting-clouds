#sextractor -c test.sex test.fits #www.mrao.cam.ac.uk/\~dfb/allsky/2011/06/20110601/201106010356.fits
#cp check.fits check-test.fits
#sextractor -c test.sex diff.fits
#cp check.fits check-diff.fits

for f in filtered/*; do
    sextractor -c test.sex $f;
    cp check.fits extracted/$f
done


