import sys
#!pip install bibtexparser
import bibtexparser
import pandas as pd

def copy_file(source_file, destination_file):
    try:
        ## Papers
        with open(source_file) as bibtex_file:
            bibtex_str = bibtex_file.read()

        bib_database = bibtexparser.loads(bibtex_str)
        #print(bib_database.entries)

        products_df = pd.DataFrame(columns=['type', 'title', 'author', 'year', 'journal', 'volume', 'pages',\
                                             'doi', 'url', 'note', 'issn', 'if', 'quartile', 'link', 'month_reported'])

        for entry in bib_database.entries:

            try:
                if entry['ENTRYTYPE'] == 'article':
                    if entry['note'] == 'jcr':
                        products_row = {'type': entry['ENTRYTYPE'],\
                            'title': entry['title'],\
                            'author': entry['author'],\
                            'year': entry['year'],\
                            'month': entry['month'],\
                            'journal': entry['journal'],\
                            'volume': entry['volume'],\
                            'pages': entry['pages'],\
                            'doi': entry['doi'],\
                            'url': entry['url'],\
                            'note': entry['note'],\
                            'issn': entry['issn'],\
                            'if': entry['if'],\
                            'quartile': entry['quartile'],\
                            'link': entry['link'],\
                            'month_reported': entry['month_reported']}
                        products_df = pd.concat([products_df, pd.DataFrame([products_row])], ignore_index=True)

                    elif entry['note'] == 'conacyt':
                        pass
                    elif entry['note'] == 'divulgacion':
                        pass
                    else:
                        pass
            except KeyError as e:
                print("KeyError: ", e)
                print(entry)
                
            if entry['ENTRYTYPE'] == 'inproceedings':
                pass
                
            if entry['ENTRYTYPE'] == 'mastersthesis':
                pass

            if entry['ENTRYTYPE'] == 'phdthesis':
                pass
                
            if entry['ENTRYTYPE'] == 'unpublished':
                pass

        products_df.to_csv(destination_file, index=False)

        print("File copied successfully!")
    except FileNotFoundError:
        print("One or both files not found.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bib2dataframe.py <source_file.bib> <destination_file.csv>")
    else:
        source_file = sys.argv[1]
        destination_file = sys.argv[2]
        copy_file(source_file, destination_file)

