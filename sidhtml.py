#!/usr/bin/env python
import os, sys, json
from urllib import quote
outdir = sys.argv[1]
#outdir = os.path.join('out','png','sid')

f_in = open('head.html', 'r') 
f_out = open(os.path.join(outdir, 'ani.html'), 'w')

f_out.writelines(f_in)
f_in.close()

for hour in range(0,24):
    for minute in range(0,60):
        f = os.path.join(str(hour).zfill(2),str(minute).zfill(2),'total.png')
        if os.path.exists(os.path.join(outdir,f)):
            i = hour*60 + minute
            f_out.write('<a href="{1}"><img id="pic"{0}" src="{1}" /></a>\n'.format(i,quote(f)))

f_out.write('</head></body>')
f_out.close()
