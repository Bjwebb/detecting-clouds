import datetime
import subprocess
import re
from collections import defaultdict

# NOTE: this code ignores windspeed events since there are none in the data
"""
find | grep log | xargs -d'\n' cat | grep weather= | sort | uniq -c
  36525 finished weather Returned from weather_status, weather=0
   2905 finished weather Returned from weather_status, weather=2
   4851 finished weather Returned from weather_status, weather=4
    226 finished weather Returned from weather_status, weather=6
   2435 Returned from weather_status, weather=1
"""

d = datetime.date(2011,3,25)
c = 0
outcomes = defaultdict(int)
while d <= datetime.date(2012,11,30):
    logfile = d.strftime('www.mrao.cam.ac.uk/~dfb/allsky/%Y/%m/%Y%m%d/log _%Y_%m_%d.log')
    # Match both weather = and weather= since some early nights use the former
    output = subprocess.check_output('grep " weather \?=" "{0}" | sort | uniq -c'.format(logfile), stderr=subprocess.STDOUT, shell=True)
    c += 1
    if output.find('No such file') >= 0:
        outcomes['nodata'] += 1
        print logfile
    else:
        counts = re.findall(r' +(\d+).+weather ?= ?(\d+)', output)
        counts_dict = dict([(code,count) for count,code in counts])
        codes = [ code for count,code in counts]
        try:
            nfine = int(counts_dict['0'])
        except KeyError:
            nfine = 0

        if codes == ['0']:
            outcomes['fine'] += 1
        if not '4' in codes and not '6' in codes: 
            if nfine < 1:
                outcomes['norain,notincluded'] += 1
            else:
                outcomes['norain,included'] += 1
        elif codes == ['4'] or codes == ['4','6'] or codes == ['6']:
            outcomes['allrain'] += 1
        else:
            if nfine < 1:
                outcomes['rain,notincluded'] += 1
            else:
                outcomes['rain,included'] += 1

    d += datetime.timedelta(days=1)

print c
print outcomes
