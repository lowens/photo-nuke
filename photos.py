import pyexiv2
import os
import sys
# not sure I actually need sys...
# Extraineous 'print' lines are rudimentary de-bugging... they give me warm-fuzzies.


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
            print 'IM A VIDEO'


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
                        print f, ' has already been placed in the library.'
                    else:
                        print 'Moving ', f, 'to ', os.path.join(outdir,yeardir,monthdir,newname)
                        os.renames(f,os.path.join(outdir,yeardir,monthdir,newname))
                else:
                    video_move(indir,outdir)

            except KeyError as keyerr:
                print outdir
                print 'Key error: Exif.Photo.DateTimeOriginal' + str(keyerr) + ' for ' + f
                print 'Trying to process ', f, ' with Exif.Image.DateTime'
# This next bit is a complete mess. Looks like I need to define another function
                try:
                   dateTag = exifdata['Exif.Image.DateTime']
                   newname = dateTag.value.strftime('%Y%m%d_%H%M%S') + suffix        
                   newname = dateTag.value.strftime('%Y%m%d_%H%M%S') + suffix
                   yeardir = dateTag.value.strftime('%Y')
                   monthdir = dateTag.value.strftime('%m')
                   if os.path.isfile(os.path.join(outdir,yeardir,monthdir,newname)):
                       os.remove(f)
                       print f, ' has already been placed in the library.'
                   else:
                       print 'Moving ', f, 'to ', os.path.join(outdir,yeardir,monthdir,newname)
                       os.renames(f,os.path.join(outdir,yeardir,monthdir,newname))
                except KeyError as anothererr:
                    print outdir, str(anothererr)
                    os.renames(f,os.path.join(outdir,'nodate',f))


# Begin crude error handling...
    except IOError as ioerr:
        print('File error: ' + str(ioerr))
        pass
#    except OSError as oserr:
#        print('OS error: ' + str(oserr))


def main():
    rootdir = os.getcwd()
    for dirpath, dirnames, filenames in os.walk(rootdir, topdown=False):
    #    indir = os.getcwd() #raw_input('Source Directory (full path): ')
        indir = dirpath
        print 'PROCESSING ', indir
        outdir = '/mnt/MediaStorage/SubaquaticPhotos'
        print 'Placing processed files in ', outdir
        meta_move(indir, outdir)


if __name__ == "__main__":
    main()
