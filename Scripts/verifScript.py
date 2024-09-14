# https://stackoverflow.com/questions/38996033/python-compare-two-csv-files-and-print-out-differences
with open('Reference datasets/lc_replicated.csv', 'r') as t1, open('Reference datasets/lc_2.csv', 'r') as t2:
    fileone = t1.readlines()
    filetwo = t2.readlines()

with open('Reference datasets/comparaison.csv', 'w') as outFile:
    for line in filetwo:
        if line not in fileone:
            outFile.write(line)
