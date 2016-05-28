import argparse
import glob
import hashlib
import logging
import pyexiv2
import os
import sets

# Get a local logger for writing log messages instead of using extraineous 'print' lines
logger = logging.getLogger(__name__)

PHOTO_EXTENSIONS = sets.Set(['jpg', 'nef', 'tif', 'png', 'bmp'])
VIDEO_EXTENSIONS = sets.Set(['mp4', 'mov', 'mts', 'avi', 'thm' ,'mpg', 'm4v'])
EXTENSIONS = PHOTO_EXTENSIONS.union(VIDEO_EXTENSIONS)

# Added this to start to deal with videos.
def process_video_file(filename, target_path):
    target_filename = os.path.join(target_path, 'Videos', os.path.basename(filename))
    logger.info('Moving VIDEO file {} to {}'.format(filename, target_filename))
    os.renames(filename, target_filename)


# read EXIF data for date of photo creation then rename the file with
# it's date/timeand move it to it's proper year/month directory
def process_photo_file(filename, target_path):
    """
    Read EXIF data for date of photo creation then rename the file with
    it's date/time and move it to its proper year/month directory
    """
    try:
        exifdata = pyexiv2.metadata.ImageMetadata(filename)
        exifdata.read()

        # Set a default target_filename in case no EXIF data is found
        target_filename = os.path.join(target_path, 'nodate', os.path.basename(filename))
        try:
            dateTag = exifdata['Exif.Photo.DateTimeOriginal']
            newname = dateTag.value.strftime('%Y%m%d_%H%M%S') + os.path.splitext(filename)[-1]
            yeardir = dateTag.value.strftime('%Y')
            monthdir = dateTag.value.strftime('%m')
            target_filename = os.path.join(target_path, yeardir, monthdir, newname)
        except KeyError as keyerr:
            try:
                dateTag = exifdata['Exif.Image.DateTime']
                newname = dateTag.value.strftime('%Y%m%d_%H%M%S') + os.path.splitext(filename)[-1]
                yeardir = dateTag.value.strftime('%Y')
                monthdir = dateTag.value.strftime('%m')
                target_filename = os.path.join(target_path, yeardir, monthdir, newname)
            except KeyError as keyerr:
                logger.warn("No EXIF data found for {}".format(filename))

        # Check for file existance here, then move.
        if os.path.isfile(target_filename):
            os.remove(filename)
            logger.warn('{} has already been placed in the library.'.format(filename))
        else:
            logger.info('Moving {} to {}'.format(filename, target_filename))
            os.renames(filename, target_filename)

    # Begin crude error handling...
    except IOError as ioerr:
        logger.warn('File error: ' + str(ioerr))
    # except OSError as oserr:
    #     logger.warn('OS error: ' + str(oserr))


def process_file(filename, target_path):
    if lowercase_file_extension(filename) in PHOTO_EXTENSIONS:
        process_photo_file(filename, target_path)
    elif lowercase_file_extension(filename) in VIDEO_EXTENSIONS:
        process_video_file(filename, target_path)
    else:
        logger.warn("{} extension not in photo or video extension list")


def lowercase_file_extension(path):
    return path.split('.')[-1].lower()


def get_file_hash(path):
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        sha1.update(f.read())
    return sha1.hexdigest()


def get_hashed_file_list(path):
    hashed_file_list = {}
    for dirpath, dirnames, filenames in os.walk(path, topdown=False):
        filenames = glob.glob(os.path.join(dirpath, "*"))
        for filename in filenames:
            if lowercase_file_extension(filename) in EXTENSIONS:
                filehash = get_file_hash(filename)
                logger.debug("Found {} with hash {}".format(filename, filehash))
                if filehash in hashed_file_list:
                    logger.warn("{} matches hash for {}, assuming it is a duplicate".format(filename, hashed_file_list[filehash]))
                else:
                    hashed_file_list[filehash] = filename
            else:
                logger.debug("Skipping {}".format(filename))
    return hashed_file_list


def backup_photos(source_path, target_path):
    source_files = get_hashed_file_list(source_path)
    target_files = get_hashed_file_list(target_path)

    for filehash in source_files:
        if filehash in target_files:
            logger.warn("Source {} matches hash for target {}, assuming it is a duplicate".format(source_files[filehash], target_files[filehash]))
        else:
            logger.info("Processing source file: {}".format(source_files[filehash]))
            process_file(source_files[filehash], target_path)


def main():
    # Set up global logging at the WARNING level, but the local logger to the DEBUG level
    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(logging.WARNING)

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
    parser.add_argument(
            "-v",
            "--verbose",
            action='count',
            default=0,
            help="Increase logging verbosity, use multiple times if desired")
    args = parser.parse_args()

    if args.verbose > 1:
        logger.setlevel(logging.DEBUG)
    elif args.verbose > 0:
        logger.setLevel(logging.INFO)

    logger.info('Source path: {}'.format(args.source_path))
    logger.info('Target path: {}'.format(args.target_path))

    backup_photos(args.source_path, args.target_path)


if __name__ == "__main__":
    main()
