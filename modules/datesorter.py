import os
import re
import PIL.Image
import datetime
import shutil
import uuid

class ds:
    def __init__(self, date_delimiter) -> None:
        self.location = ''
        self.destination = ''
        self.sort_filetypes = []
        self.date_delimiter = date_delimiter if date_delimiter in ['-','','_'] else '-'
        #self.date_delimiter = '-'
        self.files = {}
        self.file_structure = {}
        self.missed_files = []
        self.exif_supported_ftypes = ['.jpeg', '.jpg', '.png']
        
    def preload_file_data(self):
        self.files = {}
        dirlist = [x for x in os.walk(self.location)]
        #for f in os.listdir(self.location):
        for i in dirlist:
            directory = i[0]
            subfolders = i[1]
            files = i[2]
            for f in files:
                name, extension = os.path.splitext(f)
                if extension.lower() not in self.sort_filetypes:
                    print(f'SKIPPING IMAGE: {f} WITH EXTENSION: {extension.lower()}')
                    continue
                else:
                    #file_dirized = f'{self.location}/{f}'
                    file_dirized = f'{directory}/{f}'
                    self.files[f] = {
                        'location':file_dirized,
                        'name':name,
                        'extension':(extension.lower()).replace('.',''),
                        'EXIF Date Photo Taken': '',
                        'EXIF Date Photo Changed': '',
                        'EXIF Image Sensor': '',
                        'EXIF Camera Model': ''
                    }
                    
                    if extension.lower() in [ext.lower() for ext, ftype in PIL.Image.registered_extensions().items()]:
                        with PIL.Image.open(file_dirized) as pilimg:
                            exif = pilimg._getexif()
                            #extract EXIF into dict
                            self.files[f]['EXIF Date Photo Taken'] = exif[36867].split(' ')[0].replace(':', '/') if 36867 in exif.keys() and extension in self.exif_supported_ftypes else ''
                            self.files[f]['EXIF Date Photo Changed'] = exif[306].split(' ')[0].replace(':', '/') if 306 in exif.keys() and extension in self.exif_supported_ftypes else ''
                            self.files[f]['EXIF Image Sensor'] = exif[37399] if 37399 in exif.keys() and extension in self.exif_supported_ftypes else ''
                            self.files[f]['EXIF Camera Model'] = exif[50708] if 50708 in exif.keys() and extension in self.exif_supported_ftypes else ''
                            #extract best guess values
                            if 36867 in exif.keys():
                                self.files[f]['Date Best Guess'] = exif[36867].split(' ')[0].replace(':', '/')
                            elif 306 in exif.keys():
                                self.files[f]['Date Best Guess'] = exif[306].split(' ')[0].replace(':', '/')
                            elif os.path.getctime(file_dirized):
                                self.files[f]['Date Best Guess'] = datetime.datetime.fromtimestamp(os.path.getctime(file_dirized)).strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                self.files[f]['Date Best Guess'] = ''
                    else:
                        self.files[f]['Date Best Guess'] = datetime.datetime.fromtimestamp(os.path.getctime(file_dirized)).strftime('%Y-%m-%d %H:%M:%S')
            print('DATA LOADED.')
                    
                            
    def stage_sort(self, sort_by):
        sortby_options = ['Date Best Guess', 'EXIF Date Photo Taken', 'EXIF Date Photo Changed', 'EXIF Image Sensor', 'EXIF Camera Model']
        if sort_by not in sortby_options:
            print(f'NOT A SORTING OPTION [{sort_by}]. PLEASE SELECT A VALID SORTING OPTION.')
            return False
        file_structure = {}
        missed_files = []
        for f in self.files:
            d = self.files[f][sort_by]
            if d == '':
                missed_files.append(f)
            else:
                if any(ext in f.lower() for ext in self.sort_filetypes):
                    print(f'{f} has filetype in {self.sort_filetypes}')
                    if '/' in d:
                        d = d.replace('/',self.date_delimiter)
                    if ' ' in d:
                        d = d.split(' ')[0]
                    if d not in file_structure.keys():
                        file_structure[d] = []
                    else:
                        file_structure[d].append(f)
                else:
                    missed_files.append(f)
        self.file_structure = file_structure
        self.missed_files = missed_files
        print('STAGED SORT.')
        
    def exec_sort(self, progbar):
        destination_name = f'{self.destination}/sorted-{datetime.datetime.now().strftime("%m%d%Y%H%M%S")}'
        #print(f'copying data to: {destination_name}')
        try:  
            os.mkdir(destination_name)  
        except OSError as error:  
            print(error)
        curr = 0
        maxval = len(self.file_structure)
        progbar.update(current_count=curr, max=maxval)
        for dir, files in self.file_structure.items():
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
            for file in files:
                src = f'{self.location}/{file}'
                dst = f'{dirloc}/{file}'
                print(f'copying file: {src} to {dst}')
                try:
                    shutil.copy2(src, dst)
                except Exception as e:
                    print(f'ERROR WITH FILE {file}.\n EXCEPTION: {e}')
            progbar.update(current_count=curr, max=maxval)
        print('COPY COMPLETE.')