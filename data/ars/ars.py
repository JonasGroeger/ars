import json
import os
import pathlib

import requests
import untangle


class ArsCodelistProvider(object):
    def __init__(self, out_dir):
        self.api = "https://www.xrepository.de/api"
        self.ars_urn = "urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs"

        self.all_urns = list(self._get_all_urns())
        self.latest_urn = self._get_latest_urn()

        g = requests.get(f"{self.api}/version_codeliste/{self.latest_urn}/genericode")

        ars_list = []
        xml = untangle.parse(g.text)
        version_uri = xml.gc_CodeList.Identification.CanonicalVersionUri.cdata
        entries = xml.gc_CodeList.SimpleCodeList.Row
        for entry in entries:
            ars = entry.Value[0].SimpleValue.cdata
            name = entry.Value[1].SimpleValue.cdata
            ars_list.append({
                "name": name,
                "ars": ars
            })

        with open(pathlib.Path(out_dir, version_uri + ".json"), 'w', encoding="UTF-8") as f:
            json.dump(ars_list, f, indent=2, ensure_ascii=False)

        with open(pathlib.Path(out_dir, "latest"), 'w', encoding="UTF-8") as f:
            f.write(version_uri)

    def _get_latest_urn(self):
        xml = untangle.parse(f"{self.api}/codeliste/{self.ars_urn}/gueltigeVersion")
        return xml.dat_VersionCodeliste.dat_kennung.cdata

    def _get_all_urns(self):
        xml = untangle.parse(f"{self.api}/xrepository/{self.ars_urn}")
        return map(lambda x: x.cdata, xml.dat_Codeliste.dat_versionCodeliste_kennung)


if __name__ == '__main__':
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    a = ArsCodelistProvider(out_dir=PROJECT_DIR + "/out")

    print(f"Found {len(a.all_urns)} ARS URNs. Latest: {a.latest_urn}")
