import json
import time
import requests


class Parse5KaCatalog:

    headers = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
    }

    def __init__(self, parent_group_code, parent_group_name):
        self.result = {'parent_group_code': parent_group_code, 'parent_group_name': parent_group_name,
                       'producs': []}
        self.products_index = set()
        self.products_url = 'https://5ka.ru/api/v2/special_offers/'
        self.params = {
            'records_per_page': 100,
            'categories': parent_group_code
        }
        self.finished = False

    def launch_parsing(self):
        '''
        Запускает процесс чтения данных (парсинга) по координатам каталога. И выполняется до тех пор,
        пока все данные не будут прочитаны
        :return:
            ничего. Результат формируется в переменной self.result
        '''
        while not self.finished:
            self.parse()
            if not self.finished:
                time.sleep(1)

        if self.finished:
             self.save_result()

    def parse(self):
        prod_url = self.products_url
        params = self.params
        while prod_url:
            response: requests.Response = requests.get(prod_url, params=params, headers=self.headers)
            if response.status_code != 200:
                break

            data = response.json()

            for product in data.get('results', []):
                prod_id = product.get('id', '')

                # Добавление происходит только в том случае, если в индексе такого номера нет
                if prod_id not in self.products_index:
                    try:
                        self.result.get('producs').append(product)
                    except Exception:
                        pass
                    else:
                        # При удачном добавлении нового элемента в результат, добавляем id в индекс,
                        # чтобы в случае повторного чтения при сбое не добавить дубль.986\
                        self.products_index.add(prod_id)

            prod_url = data.get('next')
            if params:
                params = {}

        if not prod_url:
            self.finished = True

    def save_result(self):
        with open(f'data/products/catalog_{self.result.get("parent_group_code")}.json', 'w', encoding='UTF-8') as file:
            json.dump(self.result, file, ensure_ascii=False)

    def __str__(self):
        return str(self.result)



class Parse5Ka:

    headers = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
    }

    def __init__(self):
        self.catalog_index = set()
        self.cat_url = 'https://5ka.ru/api/v2/categories/'
        self.params = {
            'records_per_page': 100,
        }
        self.finished = False

    def launch_parsing(self):
        '''
        Выбирает все каталоги
        :return:
            ничего.
        '''
        while not self.finished:
            self.parse()
            if not self.finished:
                time.sleep(1)

    def parse(self):

        сat_url = self.cat_url
        response: requests.Response = requests.get(сat_url, headers=self.headers)

        if response.status_code != 200:
            return None

        data = response.json()
        try:
            for catalog in data:
                parser = Parse5KaCatalog(catalog.get('parent_group_code', ''), catalog.get('parent_group_name', ''))
                parser.launch_parsing()
        except Exception:
            pass
        else:
            self.finished = True

    def __str__(self):
        return str(self.result)


if __name__ == '__main__':
    site_parser = Parse5Ka()
    site_parser.launch_parsing()

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

### JetBrains template
# Covers JetBrains IDEs: IntelliJ, RubyMine, PhpStorm, AppCode, PyCharm, CLion, Android Studio, WebStorm and Rider
# Reference: https://intellij-support.jetbrains.com/hc/en-us/articles/206544839

# User-specific stuff
.idea/**/workspace.xml
.idea/**/tasks.xml
.idea/**/usage.statistics.xml
.idea/**/dictionaries
.idea/**/shelf

# Generated files
.idea/**/contentModel.xml

# Sensitive or high-churn files
.idea/**/dataSources/
.idea/**/dataSources.ids
.idea/**/dataSources.local.xml
.idea/**/sqlDataSources.xml
.idea/**/dynamic.xml
.idea/**/uiDesigner.xml
.idea/**/dbnavigator.xml

# Gradle
.idea/**/gradle.xml
.idea/**/libraries

# Gradle and Maven with auto-import
# When using Gradle or Maven with auto-import, you should exclude module files,
# since they will be recreated, and may cause churn.  Uncomment if using
# auto-import.
# .idea/artifacts
# .idea/compiler.xml
# .idea/jarRepositories.xml
# .idea/modules.xml
# .idea/*.iml
# .idea/modules
# *.iml
# *.ipr

# CMake
cmake-build-*/

# Mongo Explorer plugin
.idea/**/mongoSettings.xml

# File-based project format
*.iws

# IntelliJ
out/

# mpeltonen/sbt-idea plugin
.idea_modules/

# JIRA plugin
atlassian-ide-plugin.xml

# Cursive Clojure plugin
.idea/replstate.xml

# Crashlytics plugin (for Android Studio and IntelliJ)
com_crashlytics_export_strings.xml
crashlytics.properties
crashlytics-build.properties
fabric.properties

# Editor-based Rest Client
.idea/httpRequests

# Android studio 3.1+ serialized cache file
.idea/caches/build_file_checksums.ser

.gitignore