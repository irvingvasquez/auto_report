import bibtexparser
import datetime


def categorize_bibliography_entries(bib_database, date_inicio, date_fin):
    """
    Categorize bibliography entries by type and note.
    
    Returns a dictionary with counts and entries for each category.
    """
    categories = {
        'jcr': {'entries': [], 'count': 0},
        'cona': {'entries': [], 'count': 0},
        'divul': {'entries': [], 'count': 0},
        'otros': {'entries': [], 'count': 0},
        'proc': {'entries': [], 'count': 0},
        'mt': {'entries': [], 'count': 0},
        'phd': {'entries': [], 'count': 0},
        'preprint': {'entries': [], 'count': 0},
        'total': 0
    }
    
    for entry in bib_database.entries:
        entry_date = datetime.datetime(int(entry['year']), int(entry['month']), 1)
        
        if date_inicio <= entry_date and entry_date <= date_fin:
            categories['total'] += 1
            
            if entry['ENTRYTYPE'] == 'article':
                note = entry.get('note', '').lower()
                if note == 'jcr':
                    categories['jcr']['entries'].append(entry)
                    categories['jcr']['count'] += 1
                elif note == 'conacyt':
                    categories['cona']['entries'].append(entry)
                    categories['cona']['count'] += 1
                elif note == 'divulgacion':
                    categories['divul']['entries'].append(entry)
                    categories['divul']['count'] += 1
                else:
                    categories['otros']['entries'].append(entry)
                    categories['otros']['count'] += 1
            
            elif entry['ENTRYTYPE'] == 'inproceedings':
                categories['proc']['entries'].append(entry)
                categories['proc']['count'] += 1
            
            elif entry['ENTRYTYPE'] == 'mastersthesis':
                categories['mt']['entries'].append(entry)
                categories['mt']['count'] += 1
            
            elif entry['ENTRYTYPE'] == 'phdthesis':
                categories['phd']['entries'].append(entry)
                categories['phd']['count'] += 1
            
            elif entry['ENTRYTYPE'] == 'unpublished':
                categories['preprint']['entries'].append(entry)
                categories['preprint']['count'] += 1
    
    return categories

