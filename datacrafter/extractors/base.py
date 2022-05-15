from ..common.collect import get_file, get_file_by_name, get_file_by_pattern
from apibackuper.cmds.project import ProjectBuilder
import logging
import shutil
import os
from runpy import run_path

FILEEXT_MAP = {'file-zip' : 'zip', 'file-xls' : 'xls', 'file-csv' : 'csv', 'file-xml' : 'xml', 'file-json' : 'json', 'file-jsonl' : 'jsonl'}

class DataCrafteronfigurationError(Exception):
    def __init(self, message):
        self.message = message
        super().__init__(self.message)

class BaseExtractor:
    """This is proof-of-concept extractor class. Should be plugin based in future. #TODO Make me pluginnable"""
    def __init__(self, project=None):
        self.project = project
        self.project_config = project.project
        self.mode = project.project['extractor']['mode']
        self.sourcetype = project.project['extractor']['type']
        self.method = project.project['extractor']['method']
        self.force = project.project['extractor']['force'] if 'force' in project.project['extractor'].keys() else True
        self.config = project.project['extractor']['config'] if 'config' in project.project['extractor'].keys() else {}


    def validate(self):
        """Number of validation rules to make sure that config is right"""
        if self.project is None:
            raise DataCrafteronfigurationError("Can't run extractor without project data. Please provide it")
        if self.method == 'url' and 'url' not in self.config.keys():
            raise DataCrafteronfigurationError("An 'url' should be defined in config section for url method")
        if self.method == 'urlbypattern':
            if not ('data_prefix' in self.config.keys() and 'prefix' in self.config.keys()):
                raise DataCrafteronfigurationError("A 'prefix' and 'data_prefix' should be defined in config section for urlbypattern method")
# Need to include type = 'api'
#        if self.sourcetype not in FILEEXT_MAP.keys() :
#            raise datacrafterConfigurationError("Source type in 'type' should be one of %s" % (','.join(FILEEXT_MAP.keys())))


    def run(self):
        """Run extractor process"""
        self.validate()
        self.results = []
        if self.mode == 'singlefile':
            file_ext = FILEEXT_MAP[self.sourcetype]
            fullpathname = os.path.join(self.project.current, 'data.%s' % (file_ext))
            result = None
            if self.method == 'url':
                logging.info('Extract single file %s' % (self.config['url']))
                result = get_file(self.config['url'], fullpathname)
            elif self.method == 'urlbypattern':
                logging.info('Extract file by url pattern %s' % (self.config['prefix']))
                result = get_file_by_pattern(self.project.current, self.project.temp, self.config['prefix'], self.config['data_prefix'], fullpathname, file_type=file_ext, force=True)
            if result:
                self.results = [{'filename': os.path.relpath(fullpathname), 'compressed': False, 'type': 'file'}]
        elif self.sourcetype == 'api':
            if self.method == 'apibackuper':
                original_config = os.path.join(self.project.storage, 'apibackuper.cfg')
                if os.path.exists(original_config):
                    for filename in ['apibackuper.cfg', 'params.json', 'url_params.json']:
                        original = os.path.join(self.project.storage, filename)
                        if os.path.exists(original):
                            shutil.copy(original, os.path.join(self.project.current, filename))
                    builder = ProjectBuilder(self.project.current)
                    if not os.path.exists(os.path.join(builder.storagedir, 'storage.zip')) or self.force:
                        builder.run(mode=self.mode)
                    fullfilename = os.path.join(self.project.current, 'data.jsonl')
                    builder.export(format='jsonl', filename=fullfilename)
                    self.results = [{'filename': os.path.relpath(fullfilename), 'compressed': False, 'type' : 'file'}]
                else:
                    logging.info('APIBackuper config file not found')
        elif self.sourcetype == 'code':
            self.script = self.config['script']
            script = run_path(self.script)
            self.__process_func = script['collect']
            self.results = self.__process_func(self.config)

        status = 'fail' if len(self.results) == 0 else 'success'
        self.project.state.add('extractor', status=status, results=self.results)

