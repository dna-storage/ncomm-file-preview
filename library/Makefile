.PHONY: all file1 file2 file3 file4 count

all: file1 file2 file3 file4

count: 
	wc 2*dna 3*dna 4*dna 1*dna

file1:
	python ../tools/preview.py --downsample=6 --preview-encoding-info preview-file1.csv --o 1.wuflab.dna wuflab-noblock.jpg --encode
	python ../tools/preview-viewer.py --preview-encoding-info preview-file1.csv 1.wuflab.dna

file2:
	python ../tools/preview.py --downsample=5 --preview-encoding-info preview-file2.csv --o 2.1911_Wright_Glider.dna 1911_Wright_Glider.jpg --encode
	python ../tools/preview-viewer.py --preview-encoding-info preview-file2.csv 2.1911_Wright_Glider.dna


file3:
	python ../tools/preview.py --preview-encoding-info preview-file3.csv --o 3.first_flight.dna first_flight.jpg --encode
	python ../tools/preview-viewer.py --preview-encoding-info preview-file3.csv 3.first_flight.dna

file4:
	python ../tools/preview.py --downsample=10 --preview-encoding-info preview-file4.csv --o 4.earth.dna earth.jpg --encode
	python ../tools/preview-viewer.py --preview-encoding-info preview-file4.csv 4.earth.dna


clean:
	@rm -Rf *.dna viewer-*.jpg *~ *.comments *.log
