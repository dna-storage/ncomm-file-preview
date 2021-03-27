from dnastorage.system.formats import *
from dnastorage.system.dnafile import *
from dnastorage.util.packetizedfile import *
from dnapreview.jpeg.encode import *
from dnapreview.jpeg.decoder import *
from dnapreview.jpeg.jpeg import *
from io import BytesIO
import csv
import os

import logging
plogger = logging.getLogger('dna.preview.tools.preview-viewer')
plogger.addHandler(logging.NullHandler())


def primer_select(input_file,output_file,primers):
    strands = []
    in_fd = open(input_file,"r")
    out_fd = open(output_file,"w")
    while True:
        l = in_fd.readline()
        if len(l)==0:
            break
        if l.startswith('%'):
            out_fd.write(l)
        else:
            found = False
            for p in primers:
                if l.find(p)!=-1:
                    out_fd.write(l)
                    break
    out_fd.close()


if __name__ == "__main__":
    from dnapreview.logger import logger
    import sys
    import argparse
    from dnastorage.util.stats import stats

    parser = argparse.ArgumentParser(description="Preview support for jpeg files.")
    parser.add_argument('--o',nargs='?', dest="output", default="", help="Base name of output files.")
    parser.add_argument('--preview-encoding-info',required=True,dest='preview_info',action="store",default="")    
    parser.add_argument('input_file', nargs="?", type=str, default="", help='input file name')
    parser.add_argument('--show',dest="show",required=False,action="store_true",default=False,help='upon successful decode show the resulting file')
    args = parser.parse_args()

    if args.input_file == "":
        print("No input file specified.")
        sys.exit(0)

    primer5 = []
    primer3 = []
    with open(args.preview_info) as csvfile:
        reader = csv.DictReader(csvfile)
        for i,pinfo in enumerate(reader):
            primer5.append(pinfo['primer5'])
            primer3.append(pinfo['primer3'])

    for i in range(len(primer5)):
        if len(args.output) > 0:
            outname_dna = "{}.{}.dna".format(args.output,i)
            outname_jpg = "{}.{}.jpg".format(args.output,i)
        else:
            base = os.path.basename(args.input_file)
            split = os.path.splitext(base)
            outname_dna = "viewer-{}.{}.dna".format(split[0],i,split[1])
            outname_jpg = "viewer-{}.{}.jpg".format(split[0],i,split[1])

        primer_select(args.input_file,outname_dna,primer5[0:i+1])
    
        dna_file = DNAFile.open(outname_dna,"r",\
                                primer5[0],primer3[0],\
                                fsmd_abbrev='FSMD-1',write_incomplete_file=True)

        out_fd = open(outname_jpg,"wb")
        while True:
            b = dna_file.read(1)
            if len(b)==0:
                break
            out_fd.write(b)

        #terminate file
        out_fd.write(bytes([0xFF,0xD9]))

        out_fd.close()

        if args.show:
            dec=JPEGDecoder()
            dec.decode(filename=outname_jpg)
            dec.jpeg.show()

    stats.persist()
