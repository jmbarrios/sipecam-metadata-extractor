from setuptools import setup, find_packages

setup(name="simex", version=0.1,
      description=u"Simplify extraction of metadata for SiPeCaM files",
      author="CONABIO",
      packages=['simex'],
      install_requires = [
                          "guano",
                          "pillow",
                          "hachoir",
                          ],
      entry_points = {
          'console_scripts': [
                              "list_of_files_and_subdirectories_to_extract_metadata = simex.list_of_files_and_subdirectories_to_extract_metadata:main",
                              "extract_metadata_and_ingest_it = simex.extract_metadata_and_ingest_it:main"
                              ]
                     }
      )
