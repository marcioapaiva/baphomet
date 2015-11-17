__author__ = 'ericmuxagata'

# example:
# $  PYTHONPATH=`pwd` python baphomet/image2term_cli.py http://fc00.deviantart.net/fs71/f/2011/310/5/a/giant_nyan_cat_by_daieny-d4fc8u1.png -t 100 -r 0.01

try:
    from PIL import Image
except:
    from sys import stderr
    stderr.write('[E] PIL not installed\n')
    exit(1)
from drawille.drawille import Canvas
from drawille.graphics_utils import get_terminal_size_in_pixels, COLOR_WHITE
from StringIO import StringIO
import urllib2


img_cache = {}


# Translates the image to its black/white representation and gives back a drawable frame.
def image2term(image, threshold=128, height=None, invert=False):
    if image not in img_cache:
        if image.startswith('http://') or image.startswith('https://'):
            i = Image.open(StringIO(urllib2.urlopen(image).read())).convert('L')
        else:
            i = Image.open(open(image)).convert('L')

        w, h = i.size
        if height:
            ratio = height/float(h)

            w = int(w * ratio)
            h = int(h * ratio)
            i = i.resize((w, h), Image.ANTIALIAS)
        else:
            tw,th = get_terminal_size_in_pixels()
            if tw < w:
                ratio = tw / float(w)
                w = tw
                h = int(h * ratio)
                if th < h:
                    h = th
            elif th < h:
                ratio = th / float(h)
                h = th
                w = int(w * ratio)
                if tw < w:
                    w = tw
            i = i.resize((w, h), Image.ANTIALIAS)
        img_cache[image] = i

    x = y = 0
    i = img_cache[image]
    w,h = i.size
    frame = []

    try:
         i_converted = i.tobytes()
    except AttributeError:
         i_converted = i.tostring()

    for pix in i_converted:
        if invert:
            if ord(pix) > threshold:
                frame.append((x,y,COLOR_WHITE))
        else:
            if ord(pix) < threshold:
                frame.append((x,y,COLOR_WHITE))
        x += 1
        if x >= w:
            y += 1
            x = 0
    return (w,h,frame)


def argparser():
    import argparse
    from sys import stdout
    argp = argparse.ArgumentParser(description='drawille - image to terminal example script')
    argp.add_argument('-o', '--output'
                     ,help      = 'Output file - default is STDOUT'
                     ,metavar   = 'FILE'
                     ,default   = stdout
                     ,type      = argparse.FileType('w')
                     )
    argp.add_argument('-r', '--ratio'
                     ,help      = 'Image resize ratio'
                     ,default   = None
                     ,action    = 'store'
                     ,type      = float
                     ,metavar   = 'N'
                     )
    argp.add_argument('-t', '--threshold'
                     ,help      = 'Color threshold'
                     ,default   = 128
                     ,action    = 'store'
                     ,type      = int
                     ,metavar   = 'N'
                     )
    argp.add_argument('-i', '--invert'
                     ,help      = 'Invert colors'
                     ,default   = False
                     ,action    = 'store_true'
                     )
    argp.add_argument('image'
                     ,metavar   = 'FILE'
                     ,help      = 'Image file path/url'
                     )
    return vars(argp.parse_args())


def __main__():
    args = argparser()
    canvas = Canvas()
    args['output'].write(image2term(args['image'], canvas, args['threshold'], args['ratio'], args['invert']).frame(0, 0))
    args['output'].write('\n')


if __name__ == '__main__':
    __main__()

