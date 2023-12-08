from modules import datesorter
import PySimpleGUI as sg
import os
import uuid
import pprint

ftype = ['.jpg', '.jpeg', '.png', '.gif', '.raw', '.tiff']

config = {
    'title':'ImageryToolkit',
    'default_w':1100,
    'default_h':400,
    'minsize_w':800,
    'minsize_h':400,
    'location':'',
    'destination':'',
    'filetypes':['.jpg', '.jpeg', '.png', '.gif', '.raw', '.tiff'],
    'checkbox_filetypes':['.jpg', '.jpeg', '.png', '.gif', '.raw', '.tiff'],
    'delimiter':'',
    'sortmode':'',
    'sortmodeOptions':['Date Best Guess', 'EXIF Date Photo Taken', 'EXIF Date Photo Changed', 'EXIF Image Sensor', 'EXIF Camera Model'],
    'dirnodes':[]
    
}

config['sortmode'] = config['sortmodeOptions'][0]

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

sort_mode_column = [[sg.Text("SORT MODE")]]
for sortmodeOption in config['sortmodeOptions']:
    if config['sortmodeOptions'].index(sortmodeOption) == 0:
        sort_mode_column.append([sg.Radio(sortmodeOption, 'sortmodeoption', key=sortmodeOption, enable_events=True, default=True)])
    else:
        sort_mode_column.append([sg.Radio(sortmodeOption, 'sortmodeoption', key=sortmodeOption, enable_events=True)])

file_format_column = [[sg.Text("FILE FORMATS")]]
for fileformatOption in config['checkbox_filetypes']:
    file_format_column.append([sg.Checkbox(fileformatOption, 'fileformatoption', key=fileformatOption, enable_events=True)])

structure_preview_column = [
            [sg.Text('FILE STRUCTURE PREVIEW')],[
                sg.Tree(
                data=sg.TreeData(),
                headings=['', ],
                auto_size_columns=False,
                select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                num_rows=15,
                col0_width=0,
                col_widths = [10,],
                key='-TREE-',
                show_expanded=True,
                enable_events=True,
                expand_x=True,
                expand_y=True,
            ),],
            [sg.Text('PROCESSING PROGRESS')],
            [sg.ProgressBar(100, orientation='h', expand_x=True, size=(20, 20),  key='-PBAR-'),],
            ]

control_buttons = [sg.Button("PREVIEW"), sg.Button("EXECUTE")]

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
        #sg.Column(image_viewer_column),
    ]
]
    
class mainapp:
    def __init__(self, layout):
        self.ds = datesorter.ds(date_delimiter='-')
        self.layout = layout
        self.window = sg.Window(title=config['title'], layout=self.layout, resizable=True, finalize=True, size=(config['default_w'], config['default_h']))
        self.window.TKroot.minsize(config['minsize_w'], config['minsize_h'])
        self.ds.sort_filetypes = config['checkbox_filetypes']
        
    def event_loop(self):
        while True:
            event, values = self.window.read()
            if event != '':
                print(event)
            # End program if user closes window or
            # presses the OK button
            if event == "OK" or event == sg.WIN_CLOSED:
                break
            if event in config['checkbox_filetypes']:
                print(f'CHECKBOX EVENT: {event}')
                if event in self.ds.sort_filetypes:
                    print(f'dropping {event} from {self.ds.sort_filetypes}')
                    self.ds.sort_filetypes.remove(event)
                else:
                    print(f'adding {event} to {self.ds.sort_filetypes}')
                    self.ds.sort_filetypes.append(event)
            if event == "-SOURCE_FOLDER-":
                folder = values["-SOURCE_FOLDER-"]
                self.ds.sort_filetypes = config['filetypes']
                config['location'] = folder
                self.ds.location = folder
                self.ds.preload_file_data()
                filenames = list(self.ds.files)
                #print(filenames)
                self.window["-FILE LIST-"].update(filenames)
            if event == "-DEST_FOLDER-":
                folder = values["-DEST_FOLDER-"]
                config['destination'] = folder
                self.ds.destination = folder
            if event == "PREVIEW":
                tree = self.window['-TREE-']
                self.ds.stage_sort(sort_by=config['sortmode'])
                treedata = sg.TreeData()
                fs = self.ds.file_structure
                #pprint.pprint(fs)
                for dir, files in fs.items():
                    treedata.Insert('', dir, '', values=[dir])
                for dir, files in fs.items():
                    for file in files:
                        treedata.Insert(dir, file, '', values=[file])
                tree.update(values=treedata)
                tree.expand(True, True)
            if event == "EXECUTE":
                tree = self.window['-TREE-']
                self.ds.stage_sort(sort_by=config['sortmode'])
                treedata = sg.TreeData()
                fs = self.ds.file_structure
                #pprint.pprint(fs)
                for dir, files in fs.items():
                    treedata.Insert('', dir, '', values=[dir])
                for dir, files in fs.items():
                    for file in files:
                        treedata.Insert(dir, file, '', values=[file])
                tree.update(values=treedata)
                tree.expand(True, True)
                self.ds.exec_sort(progbar=self.window['-PBAR-'])
            if event in config['sortmodeOptions']:
                print(f'SORTMODE SET TO: {event}')
                config['sortmode'] = event


app = mainapp(layout=layout)

app.event_loop()