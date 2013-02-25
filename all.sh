python generate_symlinks.py www.mrao.cam.ac.uk sym
cd sym/2011
rm -r 01 02 03/{01,03,04,05,06,07,08}
cd ../../
python generate_symlinks.py -sid sym sid
