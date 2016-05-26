import argparse
import logging
import pyexiv2
import os

# Get a local logger for writing log messages instead of using extraineous 'print' lines
logger = logging.getLogger(__name__)


# Added this to start to deal with videos.
def video_move(indir,outdir):
    videotypes = '.mp4', '.mov', '.mts', '.avi', '.thm' ,'.mpg', '.m4v'
    outdir = os.path.join(outdir,'Videos')
    os.chdir(indir)
    for f in os.listdir(os.curdir):
#        f = os.path.join(dirpath,f)
        suffix = os.path.splitext(f.lower())[1]
        if suffix in videotypes:
            os.renames(f,os.path.join(outdir,f))
            logger.info('IM A VIDEO')


# read EXIF data for date of photo creation then rename the file with
# it's date/timeand move it to it's proper year/month directory
def meta_move(indir,outdir):
    phototypes = '.jpg', '.nef', '.tif', '.png', '.bmp'
    try:
        os.chdir(indir)
        for f in os.listdir(os.curdir):
#            f = os.path.join(dirpath,f)
            suffix = os.path.splitext(f.lower())[1]
# if suffix is jpg, nef, tif, etc...
            try:
                if suffix in phototypes:
                    exifdata = pyexiv2.metadata.ImageMetadata(f)
                    exifdata.read()
                    dateTag = exifdata['Exif.Photo.DateTimeOriginal']
                    newname = dateTag.value.strftime('%Y%m%d_%H%M%S') + suffix
                    yeardir = dateTag.value.strftime('%Y')
                    monthdir = dateTag.value.strftime('%m')
# Check for file existance here, then move.
                    if os.path.isfile(os.path.join(outdir,yeardir,monthdir,newname)):
                        os.remove(f)
                        logger.warn('{} has already been placed in the library.'.format(f))
                    else:
                        logger.info('Moving {} to {}'.format(f, os.path.join(outdir,yeardir,monthdir,newname)))
                        os.renames(f,os.path.join(outdir,yeardir,monthdir,newname))
                else:
                    video_move(indir,outdir)

            except KeyError as keyerr:
                logger.warn(outdir)
                logger.warn('Key error: Exif.Photo.DateTimeOriginal' + str(keyerr) + ' for ' + f)
                logger.warn('Trying to process {} with Exif.Image.DateTime'.format(f))
# This next bit is a complete mess. Looks like I need to define another function
                try:
                   dateTag = exifdata['Exif.Image.DateTime']
                   newname = dateTag.value.strftime('%Y%m%d_%H%M%S') + suffix
                   newname = dateTag.value.strftime('%Y%m%d_%H%M%S') + suffix
                   yeardir = dateTag.value.strftime('%Y')
                   monthdir = dateTag.value.strftime('%m')
                   if os.path.isfile(os.path.join(outdir,yeardir,monthdir,newname)):
                       os.remove(f)
                       logger.warn('{} has already been placed in the library.'.format(f))
                   else:
                       logger.info('Moving {} to {}'.format(f, os.path.join(outdir,yeardir,monthdir,newname)))
                       os.renames(f,os.path.join(outdir,yeardir,monthdir,newname))
                except KeyError as anothererr:
                    logger.warn(outdir +" " + str(anothererr))
                    os.renames(f,os.path.join(outdir,'nodate',f))


# Begin crude error handling...
    except IOError as ioerr:
        logger.warn('File error: ' + str(ioerr))
        pass
#    except OSError as oserr:
#        logger.warn('OS error: ' + str(oserr))


def main():
    # Set up global logging at the WARNING level, but the local logger to the DEBUG level
    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
            description="Utility for moving pictures into directories based on EXIF data.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
            "-s",
            "--source_path",
            default=os.getcwd(),
            help="Path to input directory")
    parser.add_argument(
            "-t",
            "--target_path",
            default='/mnt/MediaStorage/SubaquaticPhotos',
            help="Path to output directory")
    args = parser.parse_args()

    logger.info('Placing processed files in: {}'.format(args.target_path))

    for dirpath, dirnames, filenames in os.walk(args.source_path, topdown=False):
        indir = dirpath
        logger.info('PROCESSING {}'.format(indir))
        meta_move(indir, args.target_path)


if __name__ == "__main__":
    main()
