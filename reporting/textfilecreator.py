
from tabulate import tabulate
from pypdf import PdfMerger
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import pdfkit
from pyhtml2pdf import converter
import asyncio

PYPPETEER_CHROMIUM_REVISION = '1263111'

os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION
from pyppeteer import launch


def save_dict_to_file(dict, file):
    outputList = dict.items()
    table = outputList
    try:
        open(file, 'x')
    except FileExistsError:
        # print('File exists')
        pass
    outputfile = open(file, 'a')
    outputfile.write(tabulate(table, headers='firstrow'))
    outputfile.write('\n\n\n')


def getFile(file):
    path = ''
    try:
        open(path+file, 'x')
    except FileExistsError:
        # print('File exists')
        pass
    return open(path+file, 'a')


def save_figure_to_pdf(plt, file):
    figure_compilation = file
    temp_figure = 'data/temp/tempfigure.pdf'

    plt.savefig(temp_figure, format="pdf", dpi=1500)
    merger = PdfMerger()
    try:
        open(figure_compilation, 'x')
    except FileExistsError:
        # print('File exists')
        pass
    file_size = os.stat(figure_compilation).st_size
    if (file_size != 0):
        merger.append(figure_compilation)
    merger.append(temp_figure)
    merger.write(figure_compilation)
    merger.close()


async def generate_pdf(url, pdf_path):
    browser = await launch()
    page = await browser.newPage()
    
    await page.goto(url)
    
    await page.pdf({'path': pdf_path, 'format': 'A4'})
    
    await browser.close()


def save_map_to_pdf(map, file):
    final_file = file
    temp = 'data/temp/maptemp.pdf'
    getFile(temp)
    #print(map)
    #converter.convert(map, temp, print_options={"scale": 0.75})
    
    #loop = asyncio.new_event_loop()
    #asyncio.set_event_loop(loop)
    # asyncio.run(generate_pdf(map, temp))
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdfkit.from_string(map, temp, configuration=config)
    merger = PdfMerger()
    try:
        open(final_file, 'x')
    except FileExistsError:
        # print('File exists')
        
        pass
    file_size = os.stat(final_file).st_size
    if (file_size != 0):
        merger.append(final_file)
    merger.append(temp)
    merger.write(final_file)
    merger.close()


def toTable(data):
    t = Table(data)
    t.setStyle(TableStyle(
        [('SPAN', (0, 0), (-1, 0)),
         ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
    return t


def toComparasonTable(data):
    t = Table(data, [80, 80, 80, 80, 80, 80, 80])
    t.setStyle(TableStyle(
        [('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),]))
    return t
