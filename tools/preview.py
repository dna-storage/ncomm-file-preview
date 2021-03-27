#from dnastorage.arch.builder import *
from dnastorage.system.formats import *
from dnastorage.system.dnafile import *
from dnastorage.util.packetizedfile import *
from dnapreview.jpeg.encode import *
from dnapreview.jpeg.decoder import *
from dnapreview.jpeg.jpeg import *
from io import BytesIO
import csv

plogger = logging.getLogger('dna.preview.tools.preview')

class JPEGPreview:
    def __init__(self, **kwargs):

        self.preview_primers = []
        self.primer3 = []
        self.preview_percents = []
        self.formats = []
        self.flanking5 = []
        self.flanking3 = []

        self.preview_info = []
        with open(kwargs['preview_info']) as csvfile:
            reader = csv.DictReader(csvfile)
            for i,pinfo in enumerate(reader):
                self.preview_primers.append(pinfo['primer5'])
                self.primer3.append(pinfo['primer3'])
                self.preview_percents.append(int(pinfo['percent']))
                self.formats.append(pinfo['format'])
                self.flanking5.append(pinfo['flanking5'])
                self.flanking3.append(pinfo['flanking3'])
                self.preview_info.append(pinfo)

                print("{}. {}% {}".format(i,pinfo['percent'],pinfo['format']))
                print("   p5 {} ({})".format(pinfo['primer5'],len(pinfo['primer5'])))
                print("   p3 {} ({})".format(pinfo['primer3'],len(pinfo['primer3'])))
                print("   f5 {} ({})".format(pinfo['flanking5'],len(pinfo['flanking5'])))
                print("   f3 {} ({})".format(pinfo['flanking3'],len(pinfo['flanking3'])))

        #print self.preview_info
                
        self.downsample = kwargs['downsample']
        self.input_file = kwargs['input_file']
        self.jpeg = JPEG(kwargs['input_file'],kwargs['downsample'])

        self.output = kwargs['output']        
        if 'spectral_group_size' in kwargs:
            self.spectral_group_size = kwargs['spectral_group_size']
        else:
            self.spectral_group_size = 5
            

    def create_preview_regions(self,scans,comments):
        sizes = [ len(s) for s in scans ]
        total = sum(sizes)
        dist = [ 100.0*float(s)/total for s in sizes]
        #print sizes
        #print total
        #print dist
        #print sum(dist)
        #print comments

        i = 0
        total = 0.0
        all_total = []
        regions = []
        all_comments = []
        s = b''
        comm = ""
        for size,scan,c in zip(dist,scans,comments):
            #print (len(scan))
            #print ( (["{:x}".format(_) for _ in scan[:120]]) )
            total += size
            s += scan
            comm += c
            if total >= self.preview_percents[i]:
                #print "size of region=",len(s)
                regions += [s]
                all_comments += [comm]
                all_total += [total]
                s = b''
                total = 0.0
                comm = ""                
                i+=1
                if i >= len(self.preview_percents):
                    break
        if len(s) > 0:
            regions += [s]
            all_comments += [comm]
            all_total += [total]
        #print [ len(r) for r in regions ]

        output_log = "{}.comments".format(self.output.name)
        flog = open(output_log,"w")
        
        for i,(s,c,t) in enumerate(zip(regions,all_comments,all_total)):
            plogger.info("{}% is from these scans: {}".format(t,c))
            flog.write("{}: {}% is from these scans: {}\n".format(i,t,c))
            
        return regions
        
    def create_preview(self):
        codec = JPEGProgressiveEncoder(self.jpeg)
        scans,comments = codec.get_progressive_scans(self.spectral_group_size,64,True)
        regions = self.create_preview_regions(scans,comments)

        #ofile = self.output                        
        #ofile.write("%{}\n".format(self.input_file))

        dna_file = SegmentedWriteDNAFile(primer5=self.preview_primers[0],\
                                         format_name=self.formats[0],
                                         primer3=self.primer3[0],\
                                         out_fd=self.output,\
                                         flanking_primer5=self.flanking5[0],\
                                         flanking_primer3=self.flanking3[0],\
                                         fsmd_abbrev='FSMD-1')

        dna_file.write( regions[0] )

        #print len(self.preview_primers[1:])
        #print len(self.formats[1:])
        #print len(self.primer3[1:])
        #print len(self.flanking3[1:])
        #print len(self.flanking5[1:])
        #print len(regions[1:])
        
        # each region is like a separate file, with its own unique primer and arch.
        for p5,f,r,p3,f5,f3 in zip(self.preview_primers[1:],self.formats[1:],regions[1:],self.primer3[1:],self.flanking5[1:],self.flanking3[1:]):
            #print "here!"
            dna_file.new_segment(f,p5,p3,flanking_primer5=f5,flanking_primer3=f3)
            dna_file.write(r)

        dna_file.close()

        
        
if __name__ == "__main__":
    import sys
    import argparse
    from dnastorage.util.stats import stats

    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    _formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ch = logging.FileHandler("preview.log",mode='w')
    _ch.setFormatter(_formatter)
    logger.addHandler(_ch)

    
    plogger.info("Begin preview script.");
    plogger.info("Command: {}".format(" ".join(sys.argv)))
    
    
    parser = argparse.ArgumentParser(description="Preview support for jpeg files.")
    parser.add_argument('--o',nargs='?', dest="output", action="store", default="", help="Output file.")

    parser.add_argument('--encode',dest="encode",required=False,action="store_true",default=False,help='encode the image input file into JPEG preview format')

    parser.add_argument('--decode',dest="decode",required=False,action="store_true",default=False,help='decode the DNA strands into a JPEG file')

    parser.add_argument('--use-single-primer',dest="use_single_primer",required=False,action="store_true",default=False,help='If strands come from sequencing, use this setting to indicate a single primer.')

    parser.add_argument('--show',dest="show",required=False,action="store_true",default=False,help='upon successful decode show the resulting file')
        
    parser.add_argument('--downsample',dest="downsample",type=int,default=1,help="Downsample the file to make it smaller.")

    parser.add_argument('--primer3',dest="primer3",action="store",default="", help="Decoding end primer.")
    parser.add_argument('--primer5',dest="primer5",action="store",default="", help="Decoding begin primer.")

    parser.add_argument('--use-flanking-primer',dest="use_flanking_primer",required=False,action="store_true",default=False,help='If strands come from sequencing, use this setting to indicate a flanking primer.')

    parser.add_argument('--flanking-primer3',dest="flanking_primer3",action="store",default="", help="Decoding flanking end primer.")
    parser.add_argument('--flanking-primer5',dest="flanking_primer5",action="store",default="", help="Decoding flanking begin primer.")

    parser.add_argument('--preview-encoding-info',dest='preview_info',action="store",default="")
    
    parser.add_argument('input_file', nargs="?", type=str, default="", help='input file name')
    
    args = parser.parse_args()

    if args.input_file == "":
        print("No input file specified.")
        sys.exit(0)

    if args.encode:

        if len(args.preview_info)==0:
            print("Missing the csv file that describes how to encode the preview.")
            print("Pass using --preview-encoding-info.")
            sys.exit(0)

        if args.output == "":
            out_fd = sys.stdout
        else:
            out_fd = open(args.output,"wt")
            
        preview = JPEGPreview(preview_info = args.preview_info,\
                              filename = args.input_file,\
                              output = out_fd,\
                              downsample = args.downsample,\
                              input_file = args.input_file)

        preview.create_preview()

    elif args.decode:

        dna_file = DNAFile.open(args.input_file,"r",\
                                args.primer5,args.primer3,\
                                fsmd_abbrev='FSMD-1', \
                                write_incomplete_file=True,\
                                use_single_primer=args.use_single_primer,\
                                preview_mode=True, \
                                use_flanking_primer_for_decoding=args.use_flanking_primer,\
                                flanking_primer3=args.flanking_primer3,\
                                flanking_primer5=args.flanking_primer5,\
        )
        
        if args.output == "":
            print("Warning: output is in binary form. Don't send to stdout.")
            sys.exit(0)

        out_fd = open(args.output,"wb")
            
        
        while True:
            b = dna_file.read(1)
            if len(b)==0:
                break
            out_fd.write(b)

        logger.info("Wrote new jpeg file {}.".format(args.output))
        # write extra EOI just to make sure file terminates
        out_fd.write(bytes([0xFF,0xD9]))
        out_fd.close()
        #if args.show:
        #    dec=JPEGDecoder(tolerate_errors=True)
        #    dec.decode(filename=args.output)
        #    dec.jpeg.show()
        #    dec.jpeg.image.save(args.output+"2.jpg")
        #    #jpeg_name = args.output.name
        #    #j = JPEG(jpeg_name)
        #    #j.show()

    stats.persist()
    plogger.debug("Done!")
