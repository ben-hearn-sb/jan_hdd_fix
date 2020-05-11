from PySide2 import QtWidgets
from process_dialog import Process_Dialog

import os
import ntpath
import time
import stat
import shutil
import traceback, sys


class HDD_FIX(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle('Jan HDD Fix')
        self.setMinimumWidth(700)
        self.setMinimumHeight(100)
        self.log = Process_Dialog( progressBar=True)
        self.num_of_files = 0

        #self.selected_root = '/Users/macbookpro/Documents/jan_test_data'
        self.selected_root = ''
        self.lbl_browser = QtWidgets.QLabel('Select Root Directory...')
        btn_browse = QtWidgets.QPushButton('...')
        btn_browse.setFixedWidth(50)
        btn_browse.clicked.connect(self.get_root)

        btn_run_cleanup  = QtWidgets.QPushButton('Run Cleanup')
        btn_run_cleanup.clicked.connect(self.run_cleanup)

        lyt_dir = QtWidgets.QHBoxLayout()
        lyt_dir.addWidget(self.lbl_browser)
        lyt_dir.addWidget(btn_browse)

        lyt_main = QtWidgets.QVBoxLayout()
        lyt_main.addLayout(lyt_dir)
        lyt_main.addWidget(btn_run_cleanup)
        lyt_main.addWidget(self.log)
        self.setLayout(lyt_main)


    def get_root(self):
        dir_path = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if not dir_path:
            return
        else:
            self.lbl_browser.setText(dir_path)
            self.selected_root = dir_path


    def run_cleanup(self):
        if not self.selected_root:
            self.log.updateLog('Tut Tut, feed me a root directory before running cleanup', warning=True)
            return

        extensions = ('.cr2', '.jpeg', '.jpg', '.mp4', '.dng', '.mov', '.mpeg', '.arw', '.nef', '.dsc', '.png')

        img_files = list()
        for root, folder, files in os.walk(self.selected_root):
            for f in files:
                if not f.lower().endswith(extensions):
                    continue

                path = os.path.join(root, f).replace('\\', '/')

                # Ignore it if its in the timestamped folder already
                if '_TIMESTAMPED' in path:
                    continue
                img_files.append(path)

        try:
            metadata = self.get_metadata(img_files)
        except:
            var = traceback.format_exc()
            self.log.updateLog('ERROR, show this to Ben...', error=True)
            self.log.updateLog(var, error=True)
            return

        try:
            self.move_files(metadata)
        except:
            var = traceback.format_exc()
            self.log.updateLog('ERROR, show this to Ben...', error=True)
            self.log.updateLog(var, error=True)
            return
        self.log.dialogProgressBar.reset()
        self.log.updateLog('Process complete!', success=True)


    def move_files(self, metadata):
        new_dir = os.path.join(self.selected_root, '_TIMESTAMPED')
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)

        self.log.dialogProgressBar.setMax(self.num_of_files)
        self.log.dialogProgressBar.setLabelTitle('Process image files, please wait...')
        index = 0
        # Iterate years
        for f_year in metadata:
            year_dir = os.path.join(new_dir, f_year)
            if not os.path.isdir(year_dir):
                os.mkdir(year_dir)

            # Iterate months
            for f_month in metadata[f_year]:
                month_dir = os.path.join(year_dir, f_month)
                if not os.path.isdir(month_dir):
                    os.mkdir(month_dir)

                # Iterate days
                for f_day in metadata[f_year][f_month]:
                    day_dir = os.path.join(month_dir, f_day)
                    if not os.path.isdir(day_dir):
                        os.mkdir(day_dir)

                    # Iterate our files in our given month
                    for f_path in sorted(metadata[f_year][f_month][f_day].keys()):
                        n, ext = ntpath.splitext(f_path)

                        #f_day = metadata[f_year][f_month][f_path]['day']
                        f_time = metadata[f_year][f_month][f_day][f_path]['time']

                        # Make a new day and timestamped name for the file
                        new_name = '({0}){1}'.format(f_time, ext)
                        new_path = os.path.join(day_dir, new_name)

                        if not os.path.exists(new_path):
                            index += 1
                            self.move_file(f_path, new_path, index)
                        else:
                            new_path = self.check_timestamp_match(new_path)
                            index += 1
                            self.move_file(f_path, new_path, index)


    def move_file(self, orig_path, new_path, index):
        self.log.updateLog('Processing file: {0}'.format(orig_path))
        self.log.dialogProgressBar.setValue(index)
        shutil.move(orig_path, new_path)

        # Need to make sure that the dirs are cleaned up if they are empty
        self.cleanup_dir(orig_path)


    def check_timestamp_match(self, file_path, stamp=1):
        self.log.updateLog('Identical timestamp found, renaming & moving: {0}'.format(file_path))
        dirpath = os.path.dirname(file_path)
        fname = ntpath.basename(file_path)

        name, ext = ntpath.splitext(fname)

        if stamp > 1:
            name = name[:-3]
        newname = name + '_{0}_'.format(stamp) + ext

        new_path = os.path.join(dirpath, newname)

        if os.path.exists(new_path):
            new_path = self.check_timestamp_match(new_path, stamp+1)
        return new_path


    def cleanup_dir(self, f_path):
        # Remove the directory if its empty
        f_dir = os.path.dirname(f_path)
        if not len(os.listdir(f_dir)):
            os.rmdir(f_dir)


    def get_metadata(self, files):
        metadata = {}
        month_map = {'jan':'01', 'feb':'02', 'mar':'03', 'apr':'04', 'may':'05', 'jun':'06', 'jul':'07', 'aug':'08',
                     'sep':'09', 'oct':'10', 'nov':'11', 'dec':'12'}

        for f_path in files:
            self.num_of_files += 1
            fstat = os.stat(f_path)
            timestamp = time.ctime (fstat[stat.ST_MTIME]) # Modified timestamp
            split_time = timestamp.split()

            f_month = month_map[split_time[1].lower()] # Turn it into a month digit representation
            f_day   = "{:02d}".format(int(split_time[2]))
            f_time  = split_time[3].replace(':', '.')
            f_year  = split_time[4]

            # Add the year and month as containers
            if not f_year in metadata:
                metadata.update({f_year:{}})

            # Month is inner container
            if not f_month in metadata[f_year]:
                metadata[f_year].update({f_month:{}})

            # Day is inner inner container
            if not f_day in metadata[f_year][f_month]:
                metadata[f_year][f_month].update({f_day:{}})

            # Add each individual file path to the month container
            metadata[f_year][f_month][f_day].update({f_path:{'time':f_time}})

        return metadata