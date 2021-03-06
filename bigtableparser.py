import pandas as pd
import json
import sys
import merging

uniq = merging.uniq


def to_json(e):
	return json.dumps(e, indent=4, sort_keys=True, default=str)


def to_jsonfile(f, data):
	with open(f, "w") as outfile:
		outfile.write(to_json(data))
	return f


def from_jsonfile(f):
	with open(f) as infile:
		return json.load(infile)

def to_excel(fname, data, index=False):
	frame = pd.DataFrame(data)
	frame.to_excel(fname, index=index)
	return fname

def hash_bigtable(f=None):
	if not f: f = "raw/EpiAtlas_EpiRR_metadata_all.csv" # IHEC_metadata_summary.xlsx"
	frame = pd.read_csv(f) # read_excel(f, sheet_name="BigTable")
	data = frame.to_dict()
	columns = data.keys()
	n = uniq({len(data[column]) for column in columns})
	hashed = [{column: data[column][i] for column in columns} for i in range(n)]
	jsoned = to_json(hashed) # clean up any unknown types
	parsed = json.loads(jsoned)
	return to_jsonfile(f + ".json", parsed)



def merge_attributes(f=None):
    if not f: f = "config/merges.json"
    dbfile = 'raw/EpiAtlas_EpiRR_metadata_all.csv.json'
    cfg = from_jsonfile(f)
    records = from_jsonfile(dbfile)
    updated = list()
    minimal = list()
    for record in records:
        sm_record = dict()
        for rule in cfg:
            strategy = uniq(rule['strategy'])
            opts = rule.get("options")
            f = getattr(merging, strategy)
            term = rule['harmonized']
            record[term] = f(record, rule['strategy'][strategy], opts)
            sm_record[term] = record[term]
        updated.append(record)
        minimal.append(sm_record)

    print(to_jsonfile('merged/EpiAtlas_EpiRR_metadata_all.merged_sorted.json', updated))
    print(to_jsonfile('merged/EpiAtlas_EpiRR_metadata_all.merged_minimal_sorted.json', minimal))
    print(to_excel('merged/EpiAtlas_EpiRR_metadata_all.merged_sorted.xlsx', updated))
    print(to_excel('merged/EpiAtlas_EpiRR_metadata_all.merged_minimal_sorted.xlsx', minimal))
    return 'ok'

if __name__ == "__main__":
	cfg = sys.argv[1:]
	if '-hash' in cfg:
		print(hash_bigtable())
	elif '-merge' in cfg:
		print(merge_attributes())
	else:
		print('...')



