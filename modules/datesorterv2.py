import os
#import re
import PIL.Image
import datetime
import shutil
import uuid
#from tqdm import tqdm
#import pprint


class ds:
    def __init__(self, date_delimiter) -> None:
        self.location = ''
        self.destination = ''
        self.sort_filetypes = []
        self.date_delimiter = date_delimiter if date_delimiter in ['-','','_'] else '-'
        #self.date_delimiter = '-'
        self.files = {}
        self.file_structure = {}
        self.sorted_file_structure = {}
        self.missed_files = []
        self.exif_supported_ftypes = ['.jpeg', '.jpg', '.png']
        self.used_uuids = []
        
        
    def preload_file_data(self):
        self.files = {}
        dirlist = [x for x in os.walk(self.location)]
        #for f in os.listdir(self.location):
        #for i in tqdm(dirlist):
        for i in dirlist:
            directory = i[0]
            subfolders = i[1]
            files = i[2]
            #print(f'dir loaded: {directory}')
            for f in files:
                #print(f'loading file: {f}')
                #generate uuid for file
                uuid_is_unique = False
                while uuid_is_unique == False:
                    new_uuid = uuid.uuid4()
                    if new_uuid not in self.used_uuids:
                        self.used_uuids.append(new_uuid)
                        uuid_is_unique = True
                        self.files[new_uuid] = {}
                    else:
                        pass
                        #print(f'uuid is not unique: {new_uuid}')
                #print(f'uuid generated: {new_uuid}')
                #assign file and basic properties
                name, extension = os.path.splitext(f)
                self.files[new_uuid].update({
                    'parent_dir':directory,
                    'file_name':name,
                    'file_extension':(extension.lower()).replace('.',''),
                    'file':f,
                    'full_path':f'{directory}/{f}',
                    'EXIF Date Photo Taken': '',
                    'EXIF Date Photo Changed': '',
                    'EXIF Image Sensor': '',
                    'EXIF Camera Model': ''
                })
                #print(f'exif extracted for file: {f}')
                #identify support for PIL processing
                if extension.lower() in [ext.lower() for ext, ftype in PIL.Image.registered_extensions().items()]:
                    with PIL.Image.open(self.files[new_uuid]['full_path']) as pilimg:
                        exif = pilimg._getexif()
                        #extract EXIF into dict
                        self.files[new_uuid]['EXIF Date Photo Taken'] = exif[36867].split(' ')[0].replace(':', '/') if 36867 in exif.keys() and extension in self.exif_supported_ftypes else ''
                        self.files[new_uuid]['EXIF Date Photo Changed'] = exif[306].split(' ')[0].replace(':', '/') if 306 in exif.keys() and extension in self.exif_supported_ftypes else ''
                        self.files[new_uuid]['EXIF Image Sensor'] = exif[37399] if 37399 in exif.keys() and extension in self.exif_supported_ftypes else ''
                        self.files[new_uuid]['EXIF Camera Model'] = exif[50708] if 50708 in exif.keys() and extension in self.exif_supported_ftypes else ''
                        #extract best guess values
                        if 36867 in exif.keys():
                            self.files[new_uuid]['Date Best Guess'] = exif[36867].split(' ')[0].replace(':', '/')
                        elif 306 in exif.keys():
                            self.files[new_uuid]['Date Best Guess'] = exif[306].split(' ')[0].replace(':', '/')
                        elif os.path.getctime(self.files[new_uuid]['full_path']):
                            self.files[new_uuid]['Date Best Guess'] = datetime.datetime.fromtimestamp(os.path.getctime(self.files[new_uuid]['full_path'])).strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            self.files[new_uuid]['Date Best Guess'] = ''
                else:
                    self.files[new_uuid]['Date Best Guess'] = datetime.datetime.fromtimestamp(os.path.getctime(self.files[new_uuid]['full_path'])).strftime('%Y-%m-%d %H:%M:%S')
        
    def stage_sort(self, sort_by):
        sortby_options = ['Date Best Guess', 'EXIF Date Photo Taken', 'EXIF Date Photo Changed', 'EXIF Image Sensor', 'EXIF Camera Model']
        if sort_by not in sortby_options:
            #print(f'NOT A SORTING OPTION [{sort_by}]. PLEASE SELECT A VALID SORTING OPTION.')
            return False
        sorted_file_structure = {}
        missed_files = []
        for f_uuid in self.files:
            f_tosort = self.files[f_uuid]
            sortby_value = f_tosort[sort_by]
            if sortby_value == '':
                missed_files.append(f_tosort['file'])
            else:
                if any(ext in f_tosort['file'].lower() for ext in self.sort_filetypes):
                    #print(f"{f_tosort['file']} has filetype in {self.sort_filetypes}")
                    if '/' in sortby_value:
                        sortby_value = sortby_value.replace('/',self.date_delimiter)
                    if ' ' in sortby_value:
                        sortby_value = sortby_value.split(' ')[0]
                    if sortby_value not in sorted_file_structure.keys():
                        sorted_file_structure[sortby_value] = []
                    sorted_file_structure[sortby_value].append(f_uuid)
                else:
                    missed_files.append(f_tosort['file'])
        self.sorted_file_structure = sorted_file_structure
        self.missed_files = missed_files
        #print('STAGED SORT.')
            
    def exec_sort(self, progbar):
        destination_name = f'{self.destination}/sorted-{datetime.datetime.now().strftime("%m%d%Y%H%M%S")}'
        ##print(f'copying data to: {destination_name}')
        #pprint.pprint(self.file_structure)
        try:  
            os.mkdir(destination_name)  
        except OSError as error:
            pass
            #print(error)
        curr = 0
        maxval = len(self.file_structure)
        progbar.update(current_count=curr, max=maxval)
        for dir, f_uuids in self.sorted_file_structure.items():
            curr += 1
            dirloc = f'{destination_name}'
            if self.date_delimiter in dir:
                for sd in dir.split(self.date_delimiter):
                    dirloc += f'/{sd}'
            else:
                dirloc += f'/{dir}'
            builddir = ''
            for dirlvl in dirloc.split('/'):
                builddir += f'{dirlvl}/'  
                if os.path.isdir(builddir):
                    pass
                else:
                    os.mkdir(builddir)
            for f_uuid in f_uuids:
                ref_file = self.files[f_uuid]
                src = ref_file['full_path']
                dst = f'{dirloc}/{ref_file['file']}'
                #print(f'copying file: {src} to {dst}')
                try:
                    shutil.copy2(src, dst)
                except Exception as e:
                    pass
                    #print(f'ERROR WITH FILE {ref_file}.\n EXCEPTION: {e}')
            progbar.update(current_count=curr, max=maxval)
        progbar.update(current_count=0, max=maxval)
        #print('COPY COMPLETE.')