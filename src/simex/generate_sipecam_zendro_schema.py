import sys
import json
from pathlib import Path

from sgqlc.introspection import query, variables
from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.codegen.schema import CodeGen
from simex.utils import zendro


def call_sgqlc_introspection_and_codegen() -> None:

    dir_with_schema = Path.home() / "sipecam-metadata-extractor" / "src" / "simex"

    dir_with_schema.mkdir(parents=True, exist_ok=True)
    schema_name = "sipecam_zendro_schema"
    filename_schema = dir_with_schema / f"{schema_name}.json"
    outfile_schema = dir_with_schema / f"{schema_name}.py"

    headers = {"Authorization": f"bearer {zendro.get_token()}"}
    endpoint = HTTPEndpoint(zendro.get_zendro_url_for_gql(), headers)

    schema = endpoint(
        query, variables(include_description=False, include_deprecated=False)
    )

    json.dump(schema, filename_schema.open("w"), sort_keys=True, indent=2, default=str)

    if schema.get("errors"):
        sys.exit(1)

    with open(outfile_schema, "w") as outfile:
        gen = CodeGen(schema_name, schema['data']['__schema'], outfile.write, False)
        gen.write()

def main():
    call_sgqlc_introspection_and_codegen()
