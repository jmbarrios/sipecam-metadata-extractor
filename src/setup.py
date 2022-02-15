from setuptools import setup, find_packages

cli_list = "list_of_files_and_subdirectories_to_extract_metadata = simex.list_of_files_and_subdirectories_to_extract_metadata:main"
cli_extract_sn_dt = "extract_serial_numbers_datetimes_of_files = simex.extract_serial_numbers_datetimes_of_files:main"
cli_extract_met_and_ing = "extract_metadata_and_ingest_it = simex.extract_metadata_and_ingest_it:main"
cli_generate_sipecam_zendro_schema = "generate_sipecam_zendro_schema = simex.generate_sipecam_zendro_schema:main"
cli_copy_files_to_standard_directory = "copy_files_to_standard_directory = simex.copy_files_to_standard_directory:main"

setup(name="simex", version=0.1,
      description=u"Simplify extraction of metadata for SiPeCaM files",
      author="CONABIO",
      packages=find_packages(),
      install_requires = [
                          "guano",
                          "pillow",
                          "hachoir",
                          "python-dotenv",
                          "sgqlc"
                          ],
      entry_points = {
          'console_scripts': [
                              cli_list,
                              cli_extract_sn_dt,
                              cli_extract_met_and_ing,
                              cli_generate_sipecam_zendro_schema,
                              cli_copy_files_to_standard_directory
                              ]
                     }
      )
