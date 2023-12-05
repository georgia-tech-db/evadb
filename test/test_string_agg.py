import evadb
import pandas as pd
from pathlib import Path

cursor = evadb.connect().cursor()

print(cursor.query("LOAD PDF 'test/test_pdf.pdf' INTO MyPDFs;").df())
print(cursor.query("LOAD DOCUMENT 'test/sample1.txt' INTO MyTexts;").df())
print(cursor.query("LOAD DOCUMENT 'test/sample2.txt' INTO MyTexts;").df())
print(cursor.query("LOAD DOCUMENT 'test/sample3.txt' INTO MyTexts;").df())
print(cursor.query("SELECT STRING_AGG(paragraph || ' ' || name, '&') FROM MyPDFs GROUP BY '8 paragraphs';").df())
print(cursor.query("SELECT * FROM MyTexts GROUP BY '2 chunks';").df())
