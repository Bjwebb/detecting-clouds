mkdir log
time python -u perline.py $@ -fr > log/rf
time python perline.py $@ -fn > log/nf
time python perline.py $@ -g 1 > log/1
time python perline.py $@ -g 1 -f > log/1f
time python perline.py $@ -g 2 > log/2
time python perline.py $@ -g 2 -f > log/2f
time python perline.py $@ -g 3 > log/3
#time python perimage.py -m4 -o out > log/img

