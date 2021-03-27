import sys
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import random
from Bio.SeqIO.QualityIO import FastqGeneralIterator
from difflib import SequenceMatcher, Differ
from pprint import pprint as _pprint

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_ch = logging.FileHandler("deepview.log",mode='w')
_ch.setFormatter(_formatter)
logger.addHandler(_ch)

from dnastorage.system.formats import *
from dnastorage.system.header import *
from dnastorage.primer.primer_util import *

def reverse_complement(seq):
    if len(seq)==0:
        return seq
    #print (seq)
    complement = {'T':'A', 'G':'C', 'C':'G', 'A':'T'}
    r = [complement[x] for x in seq]
    r.reverse()
    return "".join(r)


def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    #ax.set_xticks(np.arange(data.shape[1]))
    #ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    #ax.set_xticklabels(col_labels)
    #ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    #ax.tick_params(top=True, bottom=False,
    #               labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in list(ax.spines.items()):
        spine.set_visible(False)

    #ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    #ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    #ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    #ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts


def get_strands(in_fd):
    strands = []
    while True:
        s = in_fd.readline()        
        if len(s) == 0:
            break
        s = s.strip()
        if s.startswith('%'):
            continue
        strands.append(s)
    return strands


def decode_segments_header(other_data,primer5,primer3):
    val = other_data
    numSeg = val[0]
    if numSeg==0:
        return
    pos = 1
    allSegs = []
    for i in range(numSeg):
        # get format of this segment
        seg = [convertBytesToInt(val[pos:pos+2])]
        pos+=2
        
        # get size in bytes
        v,p = decode_size_and_value(val,pos)
        pos += p
        seg += [v]
    
        # get begin index
        v,p = decode_size_and_value(val,pos)
        pos += p
        seg += [v]
    
        p5,p = decode_primer_diff(val[pos:], primer5)
    
        pos += p
        p3,p = decode_primer_diff(val[pos:], primer3)

        pos += p
        seg.append(p5)
        seg.append(p3)
        allSegs.append(seg)

    return allSegs

import argparse

parser = argparse.ArgumentParser(description="Fastq analysis for preview project.")
parser.add_argument('--primer3',dest="primer3",action="store",default="CGTGGCAATATGACTACGGA", help="Decoding end primer.")
parser.add_argument('--primer5',dest="primer5",action="store",default="CAGGTACGCAGTTAGCACTC", help="Decoding begin primer.")
parser.add_argument('--o',nargs='?', dest="output",action="store", default="filtered.dna", help="Output file.")

parser.add_argument('--sample',dest="sample",required=False,type=float,action="store",default=1.00,help='Downsample file, randomly, to specified percentage. So, if input=.25, only 25% of file will be used.')

parser.add_argument('--original',dest="original",required=False,action="store_true",default=False,help='use original primers from encoding as opposed to coming from PCR.')

parser.add_argument('--keep-one',dest="keep_one",required=False,action="store_true",default=False,help='only emit one copy of each decoded strand.')

parser.add_argument('--read-cnt',dest="read_cnt",required=False,type=int,action="store",default=-1,help='only emit one copy of each decoded strand.')

parser.add_argument('input_file', nargs="?", type=str, default="", help='input file name')

args = parser.parse_args()

count = 0
total_len = 0

strands = []

if len(sys.argv) > 2:
    original = args.original
else:
    original = False

input_file = args.input_file
    
if input_file.find('.fastq') != -1: 
    with open(input_file) as fin:
        for title, seq, qual in FastqGeneralIterator(fin):
            count += 1
            total_len += len(seq)            
            strands.append(seq.replace("N","A"))
else:
    with open(input_file) as fin:
        strands = get_strands(fin)
    count = len(strands)
    total_len = "?"

print((count, total_len))

orig_strand_cnt = len(strands)

from datetime import datetime
random.seed(0)
if args.read_cnt > 0:
    strands = random.sample(strands,int(args.read_cnt))
elif args.sample < 1:
    strands = random.sample(strands,int(len(strands)*args.sample))

print(("sample={}% read_cnt={} new count = {}".format(args.sample*100,args.read_cnt,len(strands))))

primer5 = args.primer5
primer3 = args.primer3

fout = open(args.output,"w")

h = decode_file_header(strands,primer5,primer3,fsmd_abbrev='FSMD-1')

header_strands,other_strands = pick_header_strands(strands,primer5)
#other_strands = pick_nonheader_strands(strands,"CAGGTACGCAGTTAGCACTC")

print(("other strands = ",len(other_strands)))

for s in header_strands:
    fout.write(s+"\n")

segs = decode_segments_header(h['other_data'],primer5,primer3)

tracker = {}

print(segs)

decoders = []

for snum,s in enumerate(segs):
    print (s)
    formatid = s[0]
    size = s[1]
    bindex = s[2]
    logger.info("bindex={} size={} p5={} p3={}".format(bindex,size,s[3],s[4]))
    if original:
        p5 = s[3]
        p3 = s[4]
        if snum > 0:
            p3 = reverse_complement(p3)
    else:
        p5 = primer5
        p3 = primer3
        
    dec_func = file_system_decoder(formatid)

    membuffer = BytesIO()
    pf = WritePacketizedFilestream(membuffer,size,file_system_format_packetsize(formatid),minKey=bindex)
    
    #dec = dec_func(pf,primer5,primer3,bindex)
    dec = dec_func(pf,p5,p3,bindex,policy=AllowAll())

    #print dec.blockSizeInBytes,dec.strandSizeInBytes,dec.blockSizeInBytes//dec.strandSizeInBytes

    last_block_size = size % dec.blockSizeInBytes
    last_block_index = size // dec.blockSizeInBytes + bindex
    last_strand_in_last_block = last_block_size//dec.strandSizeInBytes+1
    first_error_strand = dec.blockCodec._lengthMessage-dec.blockCodec._errorSymbols-2
    
    decoders.append(
        [dec, bindex, last_block_size, last_block_index, last_strand_in_last_block, first_error_strand, p5, p3] )

    
    #print "size=",size, "strands=",size/dec.strandSizeInBytes

    #print "last_block_size=",last_block_size
    #print "last_block_index=",last_block_index
    #print "last_strand_in_last_block=",last_strand_in_last_block    
    #print "error strands=",dec.blockCodec._errorSymbols
    #print dec.blockCodec._lengthMessage,dec.blockCodec._packetSize
    #print "first_error strands=",dec.blockCodec._lengthMessage-dec.blockCodec._errorSymbols-1
    #

#print (decoders)
    
def try_reverse(res, seq,dec):
    if -1 in res:
        rseq = reverse_complement(seq)
        res2 = dec.decode_from_phys_to_strand(rseq)
        if -1 not in res2:
            #print ("reversed!")
            return res2,rseq
        else:
            return res,seq
    else:
        return res,seq

goodCnt = 0
totStrands = 0
goodDecode = 0
for k,seq in enumerate(other_strands):
    #if original:
    #    if seq.find(p5) == -1:
    #        continue

    totStrands += 1
    if k % 1000 == 0 and k > 0:
        print(("Processed {} strands, {:3.1f}% decoded.".format(k,100.0*goodDecode/k)))
    
    seq_copy = seq
    possible_error = False
    for dnum,(dec,bindex,last_block_size,last_block_index,last_strand_in_last_block,first_error_strand,p5,p3) in enumerate(decoders):
        possible_error = False
        res = dec.decode_from_phys_to_strand(seq_copy)
        #print (dnum,res,)
        res,seq = try_reverse(res, seq_copy, dec)
        block_index = res[0]
        inner_idx = res[1]

        if seq.find('ATCGATGC') >= 0 and seq_copy.find('ATCGATGC') == -1:
            if -1 not in res:
                goodDecode += 1
            possible_error = True
            break
            print ("found header after reversing")
        
        if -1 not in res:
            if block_index==last_block_index and (inner_idx>last_strand_in_last_block and inner_idx<first_error_strand):
                possible_error = True
                goodDecode+=1
                break
            elif block_index < bindex or block_index > last_block_index:
                if dnum == len(decoders)-1:
                    possible_error = True
                    goodDecode+=1
                    break
                else:
                    # not correct decoder and still more chances, so don't flag error yet
                    continue
            else:
                break
                            
    if possible_error or -1 in res:
        #print ("didn't find decoding match for {}.".format(k))
        continue

    block_index = res[0]
    inner_idx = res[1]        
    #print (k, res)

    if block_index > 17:
        print((block_index, inner_idx))
    
    if -1 not in res:
        if not args.keep_one:
            fout.write(seq+"\n")
        goodCnt += 1
        goodDecode+=1
        if block_index != -1 and block_index not in tracker:
            tracker[block_index] = []
        if inner_idx != -1 and block_index != -1:
            if args.keep_one:
                if inner_idx not in tracker[block_index]:
                    fout.write(seq+"\n")
                    tracker[block_index].append(inner_idx)
            else:
                tracker[block_index].append(inner_idx)

    #if not original:
    #    break

items = list(tracker.items())
items.sort(key=lambda a:a[0])

array = {}
for k,v in items:
    v.sort()
    l = {}
    for a in v:
        l[a] = int(l.get(a,0) + 1)
    array[k] = l
    #l = l.keys()
    #l.sort()
    #print "{}:{}".format(k,l)


boolean = False
    
data = []
for i in range(256):
    row = []
    if i in array:
        for j in range(256):
            if j in array[i]:
                if boolean:
                    if array[i][j]:
                        row.append(1)
                    else:
                        row.append(0)
                else:
                    if array[i][j] > 100:
                        row.append(100)
                    else:
                        row.append(array[i][j])
            else:
                row.append(int(0))
    #else:
        #row = [ 0 for _ in range(256) ]
    if len(row)>0:
        data.append(row)    

data = np.array(data,dtype=int)

print((data.shape))

print(("max value = {}".format(np.max(data))))

fout.close()

fig, ax = plt.subplots()

#fig, (ax0, ax1) = plt.subplots(2, 1)

c = ax.pcolor(data)
ax.set_title('Color: Read Depth per Strand')

fig.tight_layout()
fig.colorbar(c, ax=ax)

#plt.show()


figname = os.path.splitext(args.output)[0] + "-dna-analysis.png"

plt.ylabel("Block Number")
plt.xlabel("Offset within Block")
plt.savefig(figname)

stats.persist()

otherout = os.path.splitext(args.output)[0] + "-stats.txt"
other = open(otherout, "w")
other.write("# " + " ".join(sys.argv) + "\n")
other.write("# Processed {} strands, {:3.1f}% ({}) decoded successfully.\n".format(totStrands,100.0*goodDecode/totStrands,goodCnt))
other.write("key,{}\n".format(os.path.basename(os.path.splitext(args.output)[0])))
other.write("strands,{}\n".format(orig_strand_cnt))
other.write("other_strands,{}\n".format(totStrands))
other.write("decoded,{}\n".format(goodDecode))
other.write("useful,{}\n".format(goodCnt))
other.close()


