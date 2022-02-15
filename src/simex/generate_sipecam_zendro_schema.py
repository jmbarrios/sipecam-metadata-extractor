import os
import subprocess

from simex.utils import zendro

def call_sgqlc_introspection_and_codegen():

    dir_with_schema = os.path.join(os.path.expanduser('~'),
                                   "sipecam-metadata-extractor/src/simex")
    os.makedirs(dir_with_schema, exist_ok=True)

    filename_schema = os.path.join(dir_with_schema,
                                   "sipecam_zendro_schema")
    string = "".join(["\"Authorization: bearer ",
                      zendro.get_token(),
                      "\"",
                      " ",
                      zendro.get_zendro_url_for_gql(),
                      " "])
    cmd1 = "".join(["python3 -m sgqlc.introspection --exclude-deprecated --exclude-description -H ",
                    string,
                    filename_schema,
                    ".json"])
    cmd2 = "".join(["sgqlc-codegen schema ",
                    filename_schema,
                    ".json",
                    " ",
                    filename_schema,
                    ".py"])
    run_out_cmd1 = subprocess.run(cmd1,
                          shell=True,
                          capture_output=True)
    print("Standard Error sgqlc.introspection %s" % run_out_cmd1.stderr)
    print("Standard Output sgqlc.introspection %s" % run_out_cmd1.stdout)
    run_out_cmd2 = subprocess.run(cmd2,
                          shell=True,
                          capture_output=True)
    print("Standard Error sgqlc-codegen %s" % run_out_cmd2.stderr)
    print("Standard Output sgqlc-codegen %s" % run_out_cmd2.stdout)

def main():
    call_sgqlc_introspection_and_codegen()
