from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import os
import sys, getopt

ABR_PDF_FILE = 'eScholarship UC item 0xj4d6bm.pdf'

#converts pdf, returns its text content as a string
def convert(in_f, out_f, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)
    infile = file(in_f, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    outfile = file(out_f, 'wb')
    outfile.write(text)
    outfile.close()

if __name__ == '__main__':
    convert(ABR_PDF_FILE, 'A.txt', pages=range(11,33))
    convert(ABR_PDF_FILE, 'B.txt', pages=range(33,38))
    convert(ABR_PDF_FILE, 'C.txt', pages=range(38,101))
    convert(ABR_PDF_FILE, 'D.txt', pages=range(101,114))
    convert(ABR_PDF_FILE, 'E.txt', pages=range(116,133))
    convert(ABR_PDF_FILE, 'F.txt', pages=range(133,138))
    convert(ABR_PDF_FILE, 'G.txt', pages=range(138,152))
    convert(ABR_PDF_FILE, 'H.txt', pages=range(152,158))
    convert(ABR_PDF_FILE, 'I.txt', pages=range(158,164))
