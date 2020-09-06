import requests
import re
import os
import json
import sys

# ex python3 scripts/refresh_original_files.py thetis_2019

THETIS_FILENAME_REGEX = r"%s\-(v\d+)\-(\d{2})(\d{2})(\d{4})\-.*"
DIRNAME = os.path.dirname(__file__)
# like "2018-v226-05092020-EU MRV Publication of information.xlsx"

# from https://www.codementor.io/@aviaryan/downloading-files-from-urls-in-python-77q3bs0un
def get_filename_from_content_disposition_header(cdh):
    if not cdh:
        return None
    match = re.match(r".*filename=\"?(.+)\"?.*", cdh)
    if match is None:
        return None
    return match.groups()[0]

class Refresher():
    def __init__(self, data_source):
        if not re.match(r"thetis_(\d{4})", data_source):
            raise "unsupported options"

        self.data_source = data_source
        self.metadata = {}

    def fetch_thetis_file(self, report_year):
        print(f"fetching THETIS file for year {report_year}...")
        url = f"https://mrv.emsa.europa.eu/api/public-emission-report/reporting-period-document/binary/{report_year}"
        res = requests.get(url, allow_redirects=True)
        raw_filename = get_filename_from_content_disposition_header(res.headers.get('Content-Disposition'))
        version, date, month, year = re.match(THETIS_FILENAME_REGEX % report_year, raw_filename).groups()
        filekey = f"thetis.export_{report_year}"
        filename = f"original.{filekey}.xlsx"
        filepath = os.path.join(DIRNAME, "..", "files_original", filename)
        self.metadata[filekey] = {
            "date": f"{year}-{month}-{date}",
            "filename": filename,
            "version": version
        }
        open(filepath, 'wb').write(res.content)
        print(f"√ wrote {filepath}")

    def write_metadata(self):
        print("outputting metadata...")
        filepath = os.path.join(DIRNAME, "..", "files_original", "metadata.json")
        metadata = json.loads(open(filepath).read())
        metadata.update(self.metadata)
        json_metadata = json.dumps(metadata, indent=2, sort_keys=True)
        open(filepath, 'w').write(json_metadata)
        print(f"√ updated {filepath}")

    def run(self):
        match = re.match(r"thetis_(\d{4})", self.data_source)
        if match:
            self.fetch_thetis_file(match.groups()[0])
        self.write_metadata()
        print("done!")

if __name__ == "__main__":
    Refresher(sys.argv[1]).run()