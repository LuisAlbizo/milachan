'''
    Module to manipulate images, create thumbnails, convert, and add FX.
'''
import subprocess, re, hashlib, os, random

class ImageFileError(Exception):
    pass

# Compilers
ImageFormat = re.compile(r"identify: (no decode delegate for this image format).*")
NotFound = re.compile(r"identify: (unable to open image).*")
Info = re.compile(r"(?P<filename>[/A-Za-z0-9._-]+)(?P<frames>\[\d+\])? (?P<format>[A-Z]+) (?P<size>\d+x\d+).* (?P<filesize>[0-9.]+)([MK]i)?B.*")

def image_info(filename):
    out = subprocess.getoutput('identify '+filename)
    match = Info.match(out)
    if match:
        info = match.groupdict()
        info ['format'] = info['format'].lower()
        info ['size'] = tuple([int(x) for x in info['size'].split('x')])
        if info['frames']:
            info ['frames'] = int(info['frames'].strip('[]'))
        else:
            info.pop ('frames')
        try:
            info ['filesize'] = int(info['filesize'])
        except:
            info ['filesize'] = eval(info['filesize'])
            if match.group(6) == 'Ki':
                info ['filesize'] = int(info['filesize']*(2**10))
            elif match.group(6) == 'Mi':
                info ['filesize'] = int(info['filesize']*(2**20))
        return info
    else:
        for err in [ImageFormat,NotFound]:
            match = err.match(out)
            if match:
                raise ImageFileError(match.group(1))
        raise ImageFileError('Unknow error: `%s`' % out)

def make_thumbnail(original,filename,size):
    return not bool(os.system('convert %s -resize %ix%i %s' % (original,size,size,filename)))

def thumbnail_gif(gif,filename,size):
    return not bool(
            os.system('convert %s -coalesce -resize %ix%i -layers OptimizeFrame %s' % (gif,size,size,filename)))

def resize(original,filename,size):
    return not bool(os.system('convert %s -resize %ix%i! %s' % (original,size[0],size[1],filename)))

def monochrome(original, filename):
    return not bool(os.system('convert %s -colorspace gray -auto-level %s' % (original,filename)))

def checksum(filename,algorithm = 'md5',chunk_size=64*1024):
    Hash = hashlib.new(algorithm)
    with open(filename,'rb') as f:
        chunk = f.read(chunk_size)
        while chunk:
            Hash.update(chunk)
            chunk = f.read(chunk_size)
        f.close()
    return Hash

#Luis Albizo 23/03/18
