from re import template
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, List
import tempfile
from PIL.Image import Image as pImage
import os

MARGINS = 20
MAX_QR_HEIGHT = 40 * mm

#We will just create some fonts and set some fixed styles which will be used for the report. No dynamic styles at this stage

FONT = 'calibri.ttf'
FONT_B = 'calibrib.ttf'

pdfmetrics.registerFont(TTFont('regular_font', FONT))
pdfmetrics.registerFont(TTFont('bold_font', FONT_B))

REG_STYLE = ParagraphStyle('regularText',
                            fontName='regular_font',
                            fontSize=20,
                            leading=20)
BOLD_STYLE = ParagraphStyle('boldText',
                            fontName='bold_font',
                            fontSize=20,
                            leading=20)

def build_pdf_report(data_struct : Dict, path : str, repeat_headings : bool = False):
    """
        Builds and saves a PDF document including QR codes and headings

        Arguments:
            data_structure: data structure in Dict formatted by qe_generator import
            path: path to save pdf document at
            repeat_headings: Determines whether to repeat headings on every line or once per doc
    """


    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin = MARGINS, leftMargin = MARGINS,
        topMargin = MARGINS, bottomMargin = MARGINS)



    temp_files = []
    data = build_data_table(data_struct, temp_files, repeat_headings)
    col_count = len(data[0])
    page_width = A4[0]
    avail_width = page_width - (MARGINS * 2)
    col_width = avail_width/col_count
    for row in data:
        for item in row:
            if isinstance(item, Image):
                item._restrictSize(col_width, MAX_QR_HEIGHT)
    elements = []
    table = Table(data, [col_width] * col_count)
    table.setStyle(
        TableStyle(
            [
                #('FONTSIZE', (0,0), (-1,-1), 24),
                ('VALIGN', (0,0), (-1,-1),'TOP'),
                # ('BOX', (0,0), (-1,-1), 0.125, colors.black),
                # ('LINEABOVE', (0,0), (-1,-1), 0.125, colors.black),
                # ('LINEBELOW', (0,0), (-1,-1), 0.125, colors.black),
                #('FONTNAME', (0,0), (0,-1),'bold_font'),
                #('FONTNAME', (1,0), (1,-1),'regular_font')
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    return temp_files
        

def build_data_table(data_struct : Dict, temp_files : List, pass_headings : bool = False,
        table : List = [], indent_count : int = 0, passed_headings : List = []) -> List[List[object]]:
    """
    Builds a table out of the provided data structure. Does not yet add in images, but will later.

    Arguments:
        data_struct: Data structure from qr_generator code
        temp_files: List of temp files which will be passed out to host process for clean up
        pass_headings: bool to indicate whether headings are to be repeated for each line
        table: table to be passed down for recursive operations
        indent_count: indent count to be passed through for recursive operations
        headings: previous headings for inclusion if required

    Result:
        table of data in List of Lists
    """
    for key in data_struct:
        # If configured to pass headings down the line then we will use these as the start of the row
        # otherwise blank strings
        if pass_headings:
            row = passed_headings[:]
        else:
            row = [ '' for _ in range(indent_count)]
        
        style = REG_STYLE
        if len(row) == 0:
            style = BOLD_STYLE

        # Add next text as paragraph to allow for word wrap
        row.append(Paragraph(key, style=style))

        # If there is an image add it to the row
        if data_struct[key][1]:
            # Has image
            image : pImage = data_struct[key][1]
            tf = tempfile.NamedTemporaryFile('wb', suffix='.png', delete=False)
            temp_files.append(tf)
            image.save(tf, bitmap_format='png')
            tf.close()
            row.append(Image(tf.name))
        else:
            row.append('')
        
        # Add row to the table
        table.append(row)

        # Recurse if there is more data
        if data_struct[key][0]:
            # Has nested data
            table = build_data_table(data_struct[key][0], temp_files, pass_headings,
                table, indent_count + 1, row[:-1])
        
        #Resize table to make uniform rows by inserting blanks to keep QR at the end
        max_cols = max([len(x) for x in table])
        for row in table:
            while len(row) < max_cols:
                row.insert(-1, '')
    return table
