from jinja2 import Template
import os
from os import walk
import sys

# PreConditions #
# MUST BE IN ROOT DIRECTORY
if not os.getcwd().endswith("/eva"):
    print("Must be ran in the root directory! (i.e .../eva)")
    print("Exiting script")
    sys.exit()


# Generate folder names and file names #

folders = []
for (dirpath, dirnames, filenames) in walk('src'):
    folders.extend(dirnames)
    break

if "__pycache__" in folders:
    folders.remove("__pycache__")

"""
# print(folders) -> ["catalog", "configuration", "executor", ...]

Generate Folder -> File mapping
-only directories with sub-directories are 'catalog', 'models',
 and 'optimizer'
-'parser' does have a sub-directory but ignoring for now
-any files not stored under any sub-directory will be placed
under a psuedo-sub-directory called "root"

{
    "catalog": [
        "models": [
            "base_model.py,"
            "df_column.py",
            ...
        ],
        "services": [
            "catalog_manager.py",
            "column_type.py",
            ...
        ]
    ],
    "configuration": [
        "root": [
            "configuration_manager.py",
            "dictionary.py",
            ...
        ]
    ],
    ...
}

"""
files_per_folder = {}
for folder in folders:

    files_per_folder[folder] = {}

    subfolders = []
    for (dirpath, dirnames, filenames) in walk('src/' + folder):
        # files.extend(filenames)
        subfolders.extend(dirnames)
        break

    if "__pycache__" in subfolders:
        subfolders.remove("__pycache__")

    subfolders.append("root")

    for subfolder in subfolders:
        subfolder_path = ''
        if subfolder == "root":
            subfolder_path = 'src/' + folder
        else:
            subfolder_path = 'src/' + folder + '/' + subfolder

        files = []

        for (dirpath, dirnames, filenames) in walk(subfolder_path):
            files.extend(filenames)

            # Remove ReadME's and __init__.py
            removeFiles = ["__init__.py"]
            files = [x.split(".py")[0]
                     for x in files if x not in removeFiles and
                     x.endswith(".py")]
            files.sort()
            break

        files_per_folder[folder][subfolder] = files

# print(files_per_folder)


# Create RST files #

rst_template_data = '''
{{title_name}}
===============
< {{folder}} description here >

{% if subpackages %}
Subpackages
-----------

.. toctree::

{% for subpackage in subpackages %}
   {{folder}}.{{subpackage}}
{% endfor %}

{% endif %}

Submodules
----------

{% for file in files %}
{{folder}}.{{file}} module
--------------------------

.. automodule:: {{folder}}.{{file}}
   :members:
   :undoc-members:
   :show-inheritance:
{% endfor %}

'''


# if not os.path.exists('api-docs/documentation_test'):
#     os.makedirs('api-docs/documentation_test')
for folder, sub_folders in files_per_folder.items():
    main_template = Template(rst_template_data)

    createDocsSubFolder = False
    subpackages = []
    if len(sub_folders) > 1:
        subpackages = [x for x in sub_folders.keys() if x != "root"]
        createDocsSubFolder = True

    if folder == "parser":
        createDocsSubFolder = False
        subpackages = []

    # title_name converts "catalog" to "Catalog"
    rendered_main_rst_template = main_template.render(
        title_name=folder[0].upper() + folder[1:],
        folder=folder,
        files=sub_folders['root'],
        subpackages=subpackages)

    if createDocsSubFolder:
        folder_dir = os.getcwd() + '/api-docs/documentation/' + folder
        if not os.path.exists(folder_dir):
            os.makedirs(folder_dir)
            print("Creating folder:", folder, "at:", folder_dir)

        main_rst_path = folder_dir + '/' + folder + ".rst"
        print("Writing documentation main rst file for",
              folder, "at:", main_rst_path)
        with open(main_rst_path, "w") as fh:
            fh.write(rendered_main_rst_template)

        for sub_folder_name in subpackages:
            files = sub_folders[sub_folder_name]
            sub_folder_template = Template(rst_template_data)
            rendered_sub_folder_rst_template = sub_folder_template.render(
                title_name=folder + "." + sub_folder_name + " package",
                folder=folder + "." + sub_folder_name,
                files=files
            )
            sub_rst_path = folder_dir + '/' + folder + "." \
                + sub_folder_name + ".rst"
            print("Writing documentation sub rst file for",
                  folder + "." + sub_folder_name,
                  "at:", sub_rst_path)
            with open(sub_rst_path, "w") as fh:
                fh.write(rendered_sub_folder_rst_template)
    else:
        path = os.getcwd() + "/api-docs/documentation/" + folder + ".rst"
        print("Writing documentation rst file for", folder, "at:", path)
        with open(path, "w") as fh:
            fh.write(rendered_main_rst_template)
