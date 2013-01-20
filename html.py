#!/usr/bin/env python
import os, sys, json
from urllib import quote
from process import subdir
outdir = sys.argv[1]

f_in = open('head.html', 'r') 
f_out = open(os.path.join(outdir, 'ani.html'), 'w')

f_out.writelines(f_in)
f_in.close()

meta = json.load(open(os.path.join('out','meta',subdir(outdir), 'sum.json'), 'r'))

for i, f in enumerate(sorted(os.listdir(outdir))):
    if f.endswith('.png') and not f.endswith('total.png'):
        f_out.write('<a href="{1}"><img id="pic"{0}" src="{1}" /></a> {2}<br/>\n'.format(i,quote(f), str(float(meta[f[:-4]])/(10**9))+' *10^9' ))

f_out.write('</head></body>')
f_out.close()
