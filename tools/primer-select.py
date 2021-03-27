#from dnastorage.arch.builder import *
from dnastorage.system.formats import *
from dnastorage.system.dnafile import *
from dnastorage.util.file_support import *
from dnapreview.jpeg.encode import *
from dnapreview.jpeg.jpeg import *
from io import BytesIO


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Preview support for jpeg files.")
    parser.add_argument('--o',nargs='?', dest="output", type=argparse.FileType('w'), default=sys.stdout, help="Output file.")

    parser.add_argument('--preview-primer',dest="preview_primers",action="append",default=[], help="Beginning primer.")

    #parser.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='file to be converted')
    parser.add_argument('input_file', nargs="?", type=argparse.FileType('r'), help='input file name')
    
    args = parser.parse_args()

    in_fd = args.input_file
    out_fd = args.output
    
    while True:
        l = in_fd.readline()
        if len(l)==0:
            break
        if l.startswith('%'):
            out_fd.write(l)
        else:
            found = False
            for p in args.preview_primers:
                if l.find(p)!=-1:
                    out_fd.write(l)
                    found = True
                    break
                
                
    if args.output != sys.stdout:
        out_fd.close()
