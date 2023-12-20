from modules import datesorterv2 as datesorter
import PySimpleGUI as sg
#import os
#import uuid
#import pprint


##CONFIG
ftype = ['.jpg', '.jpeg', '.png', '.gif', '.raw', '.tiff', '.cr2', '.arw', '.dng', '.webp', '.avif', '.bmp', '.psd', '.ai', '.svg']

config = {
    'title':'ImageryToolkit',
    'default_w':1450,
    'default_h':600,
    'minsize_w':1450,
    'minsize_h':600,
    'location':'',
    'destination':'',
    'filetypes':ftype.copy(),
    'checkbox_filetypes':ftype.copy(),
    'delimiter':'',
    'sortmode':'',
    'sortmodeOptions':['Date Best Guess', 'EXIF Date Photo Taken', 'EXIF Date Photo Changed', 'EXIF Image Sensor', 'EXIF Camera Model'],
    'dirnodes':[]
    
}

config['sortmode'] = config['sortmodeOptions'][0]

## GUI - FILE LIST
file_list_column = [
    [
        sg.Text('SOURCE'),
        sg.In(size=(25, 1), enable_events=True, key="-SOURCE_FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Text('DESTINATION'),
        sg.In(size=(25, 1), enable_events=True, key="-DEST_FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(30, 15), key="-FILE LIST-"
        )
    ],
]

## GUI - EVENT LOG DISPLAY
output_log_column = [
    [sg.Text('EVENT LOG')],
    [
        #sg.HSeparator(),
        sg.Output(size=(75,15), key="-EVENT_LOG-"),
    ],
    [sg.Text('SORT ERROR LOG')],
    [
        #sg.HSeparator(),
        sg.Output(size=(75,15), key="-SORTFAIL_LOG-")
    ],
]


## GUI - SORT MODE SELECTION
sort_mode_column = [[sg.Text("SORT MODE")]]
for sortmodeOption in config['sortmodeOptions']:
    if config['sortmodeOptions'].index(sortmodeOption) == 0:
        sort_mode_column.append([sg.Radio(sortmodeOption, 'sortmodeoption', key=sortmodeOption, enable_events=True, default=True)])
    else:
        sort_mode_column.append([sg.Radio(sortmodeOption, 'sortmodeoption', key=sortmodeOption, enable_events=True)])

## GUI - FILE FORMAT SELECTION
file_format_column = [[sg.Text("FILE FORMATS")]]
for fileformatOption in config['checkbox_filetypes']:
    file_format_column.append([sg.Checkbox(fileformatOption, 'fileformatoption', key=fileformatOption, enable_events=True)])


## GUI - FILESTRUCTURE PREVIEW
structure_preview_column = [
            [sg.Text('FILE STRUCTURE PREVIEW')],[
                sg.Tree(
                data=sg.TreeData(),
                headings=['', ],
                auto_size_columns=False,
                select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                num_rows=15,
                col0_width=3,
                col_widths = [10,],
                key='-TREE-',
                show_expanded=False,
                enable_events=True,
                expand_x=True,
                expand_y=True,
            ),],
            [sg.Text('PROCESSING PROGRESS')],
            [sg.ProgressBar(100, orientation='h', expand_x=True, size=(20, 20),  key='-PBAR-'),],
            ]

## GUI - BUTTONS
control_buttons = [sg.Button("PREVIEW"), sg.Button("EXECUTE")]

## GUI - LAYOUT BUILD
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(sort_mode_column),
        sg.VSeperator(),
        sg.Column(file_format_column),
        sg.VSeperator(),
        sg.Column(structure_preview_column, key='PREVIEW_TREE_COLUMN'),
        control_buttons,
        sg.VSeparator(),
        sg.Column(output_log_column)
        #sg.Column(image_viewer_column),
    ]
]


class mainapp:
    def __init__(self, layout):
        self.layout = layout
        self.window = sg.Window(title=config['title'], layout=self.layout, resizable=True, finalize=True, size=(config['default_w'], config['default_h']))
        self.ds = datesorter.ds(date_delimiter='-', window=self.window)
        self.window.TKroot.minsize(config['minsize_w'], config['minsize_h'])
        self.ds.sort_filetypes = config['checkbox_filetypes']
        
    def event_loop(self):
        while True:
            event, values = self.window.read()
            if event != '':
                pass
                #print(event)
            # End program if user closes window or
            # presses the OK button
            if event == "OK" or event == sg.WIN_CLOSED:
                break
            
            ## EVENTLOOP - UPDATE FILETYPE SELECTION ON CHECKBOX INTERACTION
            if event in config['checkbox_filetypes']:
                #print(f'CHECKBOX EVENT: {event}')
                if event in self.ds.sort_filetypes:
                    #print(f'dropping {event} from {self.ds.sort_filetypes}')
                    self.ds.sort_filetypes.remove(event)
                else:
                    #print(f'adding {event} to {self.ds.sort_filetypes}')
                    self.ds.sort_filetypes.append(event)
                    
            ## EVENTLOOP - UPDATE FILE SOURCE FOLDER ON FOLDER SELECTION MENU INTERACTION
            if event == "-SOURCE_FOLDER-":
                folder = values["-SOURCE_FOLDER-"]
                self.ds.sort_filetypes = config['filetypes']
                config['location'] = folder
                self.ds.location = folder
                self.ds.preload_file_data()
                #filenames = list(self.ds.files)
                filenames = list([v['file'] for k, v in self.ds.files.items()])
                ##print(filenames)
                self.window["-FILE LIST-"].update(filenames)
            
            ## EVENTLOOP - UPDATE FILE DESTINATION FOLDER ON FOLDER SELECTION MENU INTERACTION
            if event == "-DEST_FOLDER-":
                folder = values["-DEST_FOLDER-"]
                config['destination'] = folder
                self.ds.destination = folder
            
            ## EVENTLOOP - PRELOAD DATA AND GENERATE FILESTRUCTURE PREVIEW
            if event == "PREVIEW":
                tree = self.window['-TREE-']
                self.ds.stage_sort(sort_by=config['sortmode'])
                treedata = sg.TreeData()
                fs = self.ds.sorted_file_structure
                #pprint.p#print(fs)
                used_years = []
                used_months = []
                used_days = []
                for dir, files in fs.items():
                    date_tree = {}
                    if 'date' in config['sortmode'].lower():
                        year, month, day = dir.split(self.ds.date_delimiter)
                        if year not in date_tree:
                            date_tree[year] = {}
                        if month not in date_tree[year]:
                            date_tree[year][month] = {}
                        if day not in date_tree[year][month]:
                            date_tree[year][month][day] = files
                        for year in date_tree.keys():
                            if year not in used_years:
                                used_years.append(year)
                                ##print(f'Inserting year {year}')
                                treedata.Insert('', year, '', values=[year])
                            for month in date_tree[year].keys():
                                if month not in used_months:
                                    ##print(f'Inserting month {month}')
                                    treedata.Insert(year, month, '', values=[month])
                                    used_months.append(month)
                                for day, files in date_tree[year][month].items():
                                    if day not in used_days:
                                        ##print(f'Inserting day {day}')
                                        treedata.Insert(month, day, '', values=[day])
                                        used_days.append(day)
                                    for file in files:
                                        ref_file = self.ds.files[file]
                                        treedata.Insert(day, file, '', values=[ref_file['file']])
                    else:
                                
                        treedata.Insert('', dir, '', values=[dir])    
                        for dir, files in fs.items():
                            for file in files:
                                treedata.Insert(dir, file, '', values=[file])
                tree.update(values=treedata)
                tree.expand(True, True)
            
            ## EVENTLOOP - PRELOAD DATA AND EXECUTE FILE SORT
            if event == "EXECUTE":
                tree = self.window['-TREE-']
                self.ds.stage_sort(sort_by=config['sortmode'])
                treedata = sg.TreeData()
                fs = self.ds.sorted_file_structure
                #pprint.p#print(fs)
                used_years = []
                used_months = []
                used_days = []
                for dir, files in fs.items():
                    date_tree = {}
                    if 'date' in config['sortmode'].lower():
                        year, month, day = dir.split(self.ds.date_delimiter)
                        if year not in date_tree:
                            date_tree[year] = {}
                        if month not in date_tree[year]:
                            date_tree[year][month] = {}
                        if day not in date_tree[year][month]:
                            date_tree[year][month][day] = files
                        for year in date_tree.keys():
                            if year not in used_years:
                                used_years.append(year)
                                ##print(f'Inserting year {year}')
                                treedata.Insert('', year, '', values=[year])
                            for month in date_tree[year].keys():
                                if month not in used_months:
                                    ##print(f'Inserting month {month}')
                                    treedata.Insert(year, month, '', values=[month])
                                    used_months.append(month)
                                for day, files in date_tree[year][month].items():
                                    if day not in used_days:
                                        ##print(f'Inserting day {day}')
                                        treedata.Insert(month, day, '', values=[day])
                                        used_days.append(day)
                                    for file in files:
                                        ref_file = self.ds.files[file]
                                        treedata.Insert(day, file, '', values=[ref_file['file']])
                    else:
                                
                        treedata.Insert('', dir, '', values=[dir])    
                        for dir, files in fs.items():
                            for file in files:
                                treedata.Insert(dir, file, '', values=[file])
                tree.update(values=treedata)
                tree.expand(True, True)
                self.ds.exec_sort(progbar=self.window['-PBAR-'])
            
            ## EVENTLOOP - UPDATE SORT MODE CONFIG ON SORT MODE OPTION INTERACTION
            if event in config['sortmodeOptions']:
                #print(f'SORTMODE SET TO: {event}')
                config['sortmode'] = event


app = mainapp(layout=layout)

app.event_loop()