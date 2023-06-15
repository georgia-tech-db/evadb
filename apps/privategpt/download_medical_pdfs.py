from ftplib import FTP
from pathlib import Path

FTP_SERVER = 'ftp.ncbi.nlm.nih.gov'
DIR = 'pub/pmc/oa_pdf/00/'
OUT_DIR = 'medical_pdfs'
NUM_DIRS = 10

Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

ftp = FTP(FTP_SERVER)
ftp.login()
ftp.cwd(DIR)

subdirs = ftp.nlst()
done = 0
for subdir in subdirs:
    print('Downloading pdfs from {}'.format(DIR + subdir))
    ftp.cwd(subdir)
    files = ftp.nlst()
    for filename in files:
        print(' ' * 4 + filename)
        with open(Path(OUT_DIR) / filename, 'wb') as handle:
            ftp.retrbinary('RETR ' + filename, handle.write)
    done += 1
    if done == NUM_DIRS:
        break
    ftp.cwd('..')
ftp.quit()

