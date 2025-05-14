import sys
#!pip install bibtexparser
import bibtexparser
import pandas as pd

def copy_file(source_file, destination_file, entrytype):
    try:
        ## Papers
        with open(source_file) as bibtex_file:
            bibtex_str = bibtex_file.read()

        bib_database = bibtexparser.loads(bibtex_str)

        matching_entries = [entry for entry in bib_database.entries if entry['ENTRYTYPE'] == entrytype]
        
        unique_keys = set([key for entry in matching_entries for key in entry.keys()])
        print("Unique keys in matching entries:", unique_keys)
        
        products_df = pd.DataFrame(columns=list(unique_keys))

        for entry in matching_entries:
            try:
                products_row = {key:entry[key] for key in entry.keys()}
                #print("products_row: ", products_row)
                products_df = pd.concat([products_df, pd.DataFrame([products_row])], ignore_index=True)

            except KeyError as e:
                print("KeyError: ", e)
                print(entry)
                
        products_df.to_csv(destination_file, index=False)

        print("File copied successfully!")
    except FileNotFoundError:
        print("One or both files not found.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python bib2dataframe.py <source_file.bib> <destination_file.csv> <entrytype>")
        print("Example: python bib2dataframe.py bibtex.bib bibtex.csv article")
    else:
        source_file = sys.argv[1]
        destination_file = sys.argv[2]
        entrytype = sys.argv[3]
        copy_file(source_file, destination_file, entrytype)

