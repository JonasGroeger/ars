import json
import pathlib

import requests
import untangle


class ArsCodelistProvider(object):
    def __init__(self):
        self.api = "https://www.xrepository.de/api"
        self.ars_urn = "urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs"
        self.ars_list = []

        latest_xml = self._get_latest_xml()
        self.version_uri = (
            latest_xml.gc_CodeList.Identification.CanonicalVersionUri.cdata
        )
        for entry in latest_xml.gc_CodeList.SimpleCodeList.Row:
            ars = entry.Value[0].SimpleValue.cdata
            name = entry.Value[1].SimpleValue.cdata
            self.ars_list.append({"name": name, "ars": ars})

    def write(self, out_dir):
        out_file = out_dir.joinpath(self.version_uri + ".json")
        latest_file = out_dir.joinpath("latest.json")

        to_write = {
            "data": self.ars_list,
            "urn": self.ars_urn,
            "version_uri": self.version_uri,
            "version": self.version_uri.rsplit("_", 1)[-1],
        }

        with open(out_file, "w", encoding="UTF-8") as f:
            json.dump(to_write, f, indent=2, ensure_ascii=False)

        with open(latest_file, "w", encoding="UTF-8") as f:
            json.dump(to_write, f, indent=2, ensure_ascii=False)

    def _get_latest_urn(self):
        xml = untangle.parse(f"{self.api}/codeliste/{self.ars_urn}/gueltigeVersion")
        return xml.dat_VersionCodeliste.dat_kennung.cdata

    def _get_all_urns(self):
        xml = untangle.parse(f"{self.api}/xrepository/{self.ars_urn}")
        return map(lambda x: x.cdata, xml.dat_Codeliste.dat_versionCodeliste_kennung)

    def _get_latest_xml(self):
        latest_urn = self._get_latest_urn()
        latest = requests.get(f"{self.api}/version_codeliste/{latest_urn}/genericode")
        return untangle.parse(latest.text)


if __name__ == "__main__":
    PROJECT_DIR = pathlib.Path(__file__).parent

    acp = ArsCodelistProvider()
    acp.write(PROJECT_DIR.joinpath("data"))
