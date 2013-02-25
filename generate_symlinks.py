import os, sys, errno
import pyfits, dateutil.parser
from utils import join, get_sidereal_time

def new_path_from_datestamp(date_obs):
    return os.path.join(date_obs[0:4], date_obs[5:7], date_obs[8:10])

class Symlinker(object):
    force = False

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs) 

    def symlink(self, src, dst):
        try:
            os.symlink(src, dst)
        except OSError as e:
            if e.errno == errno.EEXIST:
                if self.force:
                    os.remove(dst)
                    os.symlink(src,dst)
                else:
                    print "The file {0} already exists, use -f to remove files automatically.".format(dst)
                    sys.exit(1)

    def generate_symlinks(self):
        for (path, subdirs, files) in os.walk(self.indir):
            subdirs.sort()
            files.sort()
            for name in files:
                if not name.endswith('.fits'):
                    continue
                fname = os.path.join(path, name)
                hdulist = pyfits.open(fname, do_not_scale_image_data=True)
                hdu = hdulist[0] 
                date_obs = hdu.header['DATE-OBS'] 
                self.symlink(os.path.abspath(fname),
                    join(self.outdir,
                        new_path_from_datestamp(date_obs),
                        date_obs+'.fits'))


class SidSymlinker(Symlinker):
    def generate_symlinks(self):
        for (path, subdirs, files) in os.walk(self.indir):
            subdirs.sort()
            files.sort()
            for fname in files:
                dt = dateutil.parser.parse(fname.split('.')[0])
                sidtime = get_sidereal_time(dt)
                self.symlink(
                    os.path.abspath(os.path.realpath(os.path.join(path,fname))),
                    join(self.outdir,
                        str(sidtime.seconds/3600).zfill(2),
                        str((sidtime.seconds/60)%60).zfill(2),
                        fname))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Generate symlinks grouped by date information taken from the DATE-OBS header.")
    parser.add_argument('indir', help="Input directory to generate symlinks to") 
    parser.add_argument('outdir', help="Output directory, where symlinks are places") 
    parser.add_argument('-sid', '--groupby_sidereal_time', dest='class', action='store_const',
        const=SidSymlinker,
        default=Symlinker,
        help="Group the symlinks based on sidereal times, and assume the filename contains the DATE-OBS information."
    ) 
    parser.add_argument('-f', '--force', action='store_true',
        help="Forcibly create symlinks by removing any files that may already exist."
    )
    kwargs = vars(parser.parse_args())
    symlinker = kwargs.pop('class')(**kwargs)
    symlinker.generate_symlinks()

