import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5 import uic, QtWidgets
from PyQt5 import QtSql
import sqlite3
import re
import shutil

#________________gui file of main window_______________#
Ui_gui, QtBaseClass = uic.loadUiType("gui.ui")

#_______________gui file of creating a new job Dialog_________________#
Ui_New_Job, LandingPageBase = uic.loadUiType("NewJob.ui")

#______________gui file of creating new group Dialog_____________#
Ui_New_Group, LandingPageBas = uic.loadUiType("NewGroup.ui")

#______________gui file of the option Dialog_____________#
Options, QWidget = uic.loadUiType("Options.ui")


#____________class of main window_____________#
class Main(QMainWindow, Ui_gui):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_gui.__init__(self)
        self.setupUi(self)
        self.actionNew_Job.triggered.connect(self.open_New_Job)          #button of creating new job
        self.actionNew_Group.triggered.connect(self.open_New_Group)     #button of creating new group
        self.actionAutoRun.triggered.connect(self.Auto_Run_switch)     #button of AutoRun
        self.left.clicked.connect(self.Open_FileL)                    #button of opening left file
        self.right.clicked.connect(self.Open_FileR)                  #button of opening right file
        self.actionOPtions.triggered.connect(self.Open_Options)     #Option button
        self.actionAnalyze.triggered.connect(self.start_analyze)   #Analyze button
        self.action_Analyze.triggered.connect(self.start_analyze) #Analyze button of menu bar
        self.rightPu.clicked.connect(self.copy_right)
        self.leftPu.clicked.connect(self.copy_left)
        self.actionSync.triggered.connect(self.Sync_ko)
        self.toolBar_3.setVisible(False)
        self.toolBar_4.setVisible(False)
        self.fileModel = QFileSystemModel()
        self.fileModel.setFilter(QDir.NoFilter | QDir.AllEntries)  #opening all file models of the directory
        self.Stacked.setCurrentWidget(self.alljobs)               #set the current page in to AllJobs
        self.treeViewL.setModel(self.fileModel)
        self.treeViewR.setModel(self.fileModel)
        self.l1 = QTreeWidgetItem(["All jobs"])                 #creating one new job in the left toolbar
        self.treeWidget.addTopLevelItem(self.l1)
        self.toolBar_3.addWidget(self.openf)                   #adding the openFile buttons in to top toolbar
        self.lft = 0                                          #left folder flag
        self.rgt = 0                                         #right folder flag
        self.i =0                                           #number of jobs
        self.name_array = [" "]                            #array of jobs name
        self.Lpath_array = ["c:"]                         #array of left paths
        self.Rpath_array = ["c:"]                        #array of right paths
        self.conn = sqlite3.connect('FILE_Sync.db')     #declare database
        self.cur = self.conn.cursor()
        self.cur.execute('DROP TABLE IF EXISTS Sync')   #creating table
        self.cur.execute('''CREATE TABLE Sync (file_or_folder text, name text, path text,i real, Ldate text,
                                              Lsize real, Rdate text, Rsize real, flag real, copied real)''')

        #________set column preporties for tree widget_______#
        self.treeWidgetR.setColumnCount(8)
        self.treeWidgetR.setHeaderLabels(["Name", "L Date", "L Size","","L", "R", "R Date", "R Size"])
        self.treeWidgetR.header().setDefaultAlignment(Qt.AlignCenter)
        self.treeWidgetR.setColumnWidth(0, 250)
        self.treeWidgetR.setColumnWidth(1, 150)
        self.treeWidgetR.setColumnWidth(2, 200)
        self.treeWidgetR.setColumnWidth(3, 8)
        self.treeWidgetR.setColumnWidth(4, 50)
        self.treeWidgetR.setColumnWidth(5, 50)
        self.treeWidgetR.setColumnWidth(6, 150)
        self.treeWidgetR.setColumnWidth(7, 200)


    #____________function of handling AutoRun button____________#
    def Auto_Run_switch(self):
        if self.actionAutoRun.text() == "AutoRun on":
            self.actionAutoRun.setText("AutoRun off")
        elif self.actionAutoRun.text() == "AutoRun off":
            self.actionAutoRun.setText("AutoRun on")

    #___________function of opening left file____________#
    def Open_FileL(self):
        global dirL                                                             #left folder path
        dirL = str(QFileDialog.getExistingDirectory(self, "Select Directory")) #gettin the left folder path
        self.Lpath_array.append(dirL)
        stri = self.checklen(dirL)
        if stri == 'splited':                                   #check the lenght of path to show it based on size
            self.left.setText(data[0] + "/\n" + data[1])
        else:
            self.left.setText(dirL)
        self.left.setIcon(QIcon('images/filesys-1.png'))
        self.lft = 1
        self.checkpath()

    #____________function of opening right file________#
    def Open_FileR(self):
        global dirR                                                             #right folder path
        dirR = str(QFileDialog.getExistingDirectory(self, "Select Directory")) #getting the right folder path
        self.Rpath_array.append(dirR)
        self.right.setIcon(QIcon("images/filesys-1.png"))
        stri = self.checklen(dirR)
        if stri == 'splited':                                   #check the lenght of path to show it based on size
            self.right.setText(data[0] + "/\n" + data[1])
        else:
            self.right.setText(dirR)
        self.rgt = 1
        self.checkpath()

    #__________function to check the size of path__________#
    def checklen(self, path):
        global data
        data  = path.split("/")
        if len(data) > 5:             #if the lenght of path is more than 5 directories
            n = 5
            data = '/'.join(data[:n]), '/'.join(data[n:])
            return 'splited'

    #___________function to check the flags__________#
    def checkpath(self):
        if self.lft == 1 and self.rgt == 1:               #if the both paths are chosed
            self.Stacked.setCurrentWidget(self.analyze)  #change the main page to Analyze page
            self.actionAnalyze.setEnabled(True)         #enable the Analyze button
            self.center.setEnabled(True)

    #_________function of Analyze button clicked________#
    def start_analyze(self):
        self.actionSync.setEnabled(True)
        if self.wjob.Task == "backup":
            self.actionSync.setText("BackUp")
        #enable the Sync button
        self.Stacked.setCurrentWidget(self.jobpage)                    #change the main page to Jobpage
        global max_iL        #left root depth
        global max_iR        #right root depth
        max_iL = 0
        max_iR = 0
        for root, dirs, files in os.walk(dirL):             #opening left path & extracting all files & folders & insert them in to table
            for name in dirs:
                temp_s = str(os.path.join(root, name))
                info1 = QFileInfo(temp_s)
                temp_s = re.sub(dirL, "", temp_s)
                temp_name = temp_s [temp_s.rfind('\\')+1 :]
                temp_s = temp_s[:temp_s.rfind(('\\')) + 1]
                temp_i = len(re.findall(r'\\', temp_s))
                if temp_i > max_iL:
                    max_iL = temp_i
                self.cur.execute("INSERT INTO Sync VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                                 ("Folder", temp_name, temp_s, temp_i, info1.lastModified().toString("yyyy-MM-dd hh:mm:ss"), "(folder)","not present", "", 0, 0))
            for name in files:
                temp_s = str(os.path.join(root, name))
                info2 = QFileInfo(temp_s)
                temp_s = re.sub(dirL, "", temp_s)
                temp_name = temp_s [temp_s.rfind('\\')+1 :]
                temp_s = temp_s[:temp_s.rfind(('\\')) + 1]
                temp_i = len(re.findall(r'\\', temp_s))
                self.cur.execute("INSERT INTO Sync VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                                 ("File", temp_name, temp_s, temp_i, info2.lastModified().toString("yyyy-MM-dd hh:mm:ss"), info2.size(),"not present", "", 0, 0))

        for root, dirs, files in os.walk(dirR):              #opening right path & extracting all files & folders & insert them in to table
            for name in dirs:
                temp_s = str(os.path.join(root, name))
                info3 = QFileInfo(temp_s)
                temp_name = temp_s [temp_s.rfind('\\')+1 :]
                temp_s = temp_s[:temp_s.rfind(('\\')) + 1]
                temp_s = re.sub(dirR ,"", temp_s)
                temp_i = len(re.findall(r'\\', temp_s))
                if temp_i > max_iR:
                    max_iR = temp_i
                self.cur.execute("INSERT INTO Sync VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?);",
                                 ('Folder', temp_name, temp_s, temp_i,  'not present', "",info3.lastModified().toString("yyyy-MM-dd hh:mm:ss"), "(folder)", 0, 0))

            for name in files:
                temp_s = str(os.path.join(root, name))
                info4 = QFileInfo(temp_s)
                temp_s = re.sub(dirR, "", temp_s)
                temp_name = temp_s [temp_s.rfind('\\')+1 :]
                temp_s = temp_s[:temp_s.rfind(('\\')) + 1]
                temp_i = len(re.findall(r'\\', temp_s))
                self.cur.execute("INSERT INTO Sync VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                                 ("File", temp_name, temp_s, temp_i, "not present", "", info4.lastModified().toString("yyyy-MM-dd hh:mm:ss") , info4.size(), 0, 0))


        for k in range(1, max_iL+1):  #modifing the table & checking the same files & folders in both roots
            self.cur.execute('SELECT name FROM Sync WHERE (Rdate, i, flag)=(?, ?, ?)', ('not present', k, 0))
            nameL = self.cur.fetchall()
            self.cur.execute('SELECT path FROM Sync WHERE (Rdate, i, flag)=(?, ?, ?)', ('not present', k, 0))
            pathL = self.cur.fetchall()
            self.cur.execute('SELECT name FROM Sync WHERE (Ldate, i, flag)=(?, ?, ?)', ('not present', k, 0))
            nameR = self.cur.fetchall()
            self.cur.execute('SELECT path FROM Sync WHERE (Ldate, i, flag)=(?, ?, ?)', ('not present', k, 0))
            pathR = self.cur.fetchall()


            for i in range(0, len(nameL)):
                flag = 1
                source_path = dirL + pathL[i][0]
                for j in range(0, len(nameR)):
                    if nameL[i][0] == nameR[j][0]:
                        flag = 0
                        self.cur.execute("DELETE FROM Sync WHERE (name,Ldate, i)=(?,?,?)",(nameL[i][0], 'not present', k))
                        self.cur.execute("UPDATE Sync SET Rdate=? WHERE (name,Rdate, i)=(?,?,?)", (" ", nameL[i][0],"not present", k ))
                if flag == 1:
                    destination_path = dirR + pathL[i][0]
                    self.cur.execute('UPDATE Sync SET flag=? WHERE path LIKE ?', (1, pathL[i][0] + nameL[i][0] + '%' ))
                    self.cur.execute('UPDATE Sync SET flag=? WHERE (path, name, Rdate)=(?, ? , ?)', (1, pathL[i][0] , nameL[i][0], 'not present'))

        ###_______show folders and files on tree widget_______###
        self.cur.execute('SELECT * FROM Sync') #import data from table
        all = self.cur.fetchall()
        sub_items_R = []
        sub_items_L = []
        path_L = []
        names_L = []
        path_R = []
        names_R = []
        #_____creating top items_______#
        for i,row in enumerate(all):

            if row[3] == 1.0:      #find top items
                item = (QTreeWidgetItem([str(row[1]), str(row[4]), str(row[5]),"", "", "", str(row[6]), str(row[7])]))
                self.treeWidgetR.addTopLevelItem(item)

                for i in range(1,8):
                    item.setTextAlignment(i, Qt.AlignCenter)

                pat_ = str(row[2])
                nam = str(row[1])

                __dir = str(row[1])
                font = QFont()
                font.setWeight(QFont.Bold)

                #____set view preporties of top items_____#
                if row[4] == 'not present':
                    __path = dirR
                    item.setIcon(5, QIcon('images/next.png'))
                    item.setIcon(4, QIcon('images/back.png'))


                elif row[6] == 'not present':
                    __path = dirL
                    item.setIcon(4, QIcon('images/previous.png'))
                    item.setIcon(5, QIcon('images/forward.png'))
                else:
                    __path = dirL
                    item.setIcon(4, QIcon('previous.png'))
                    item.setIcon(5, QIcon('next.png'))

                __path = __path.split("/")
                __path = '\\'.join(__path)
                item.setBackground(6,QBrush(QColor("#E5CCFF")))
                item.setBackground(7,QBrush(QColor("#E5CCFF")))
                item.setBackground(1,QBrush(QColor(204, 255, 204)))
                item.setBackground(2,QBrush(QColor(204, 255, 204)))
                fileInfo = QFileInfo(__path + pat_ + __dir)
                iconProvider = QFileIconProvider()
                icon = iconProvider.icon(fileInfo)
                item.setIcon(0,icon)

                #____if subitem is a folder_____#
                if row[0] == "Folder":
                    for row in all:
                        if (pat_ + nam + '\\' == str(row[2])):  #find childs of folder
                            if row[3] == 2.0:
                                #_sub item_#
                                sub_item = QTreeWidgetItem([str(row[1]), str(row[4]), str(row[5]),"", "", "", str(row[6]), str(row[7])])

                                for i in range(1,8):
                                    sub_item.setTextAlignment(i, Qt.AlignCenter)

                                _dir = str(row[1])

                                #____set view preporties of sub items_____#
                                if row[4] == 'not present':
                                    _path = dirR
                                    sub_items_R.append(sub_item)
                                    path_R.append(str(row[2]))
                                    names_R.append(str(row[1]))
                                    item.setIcon(5, QIcon('images/next.png'))
                                    item.setIcon(4, QIcon('images/back.png'))

                                else:
                                    _path = dirL
                                    sub_items_L.append(sub_item)
                                    path_L.append(str(row[2]))
                                    names_L.append(str(row[1]))
                                    item.setIcon(4, QIcon('images/previous.png'))
                                    item.setIcon(5, QIcon('images/forward.png'))


                                _path = _path.split("/")
                                _path = '\\'.join(_path)
                                sub_item.setBackground(6,QBrush(QColor("#E5CCFF")))
                                sub_item.setBackground(7,QBrush(QColor("#E5CCFF")))
                                sub_item.setBackground(1,QBrush(QColor(204, 255, 204)))
                                sub_item.setBackground(2,QBrush(QColor(204, 255, 204)))
                                fileInfo = QFileInfo(_path +  str(row[2]) + _dir)
                                iconProvider = QFileIconProvider()
                                icon = iconProvider.icon(fileInfo)
                                sub_item.setIcon(0,icon)
                                item.addChild(sub_item)

        #_______search for all subfolders and subfiles in right directory________#
        for i in range(3, max_iR + 2):
            for row in all:
                if row[4] == "not present":
                    if row[3] == i:
                        for j, nam in enumerate(names_R):
                            if (path_R[j] + nam + '\\' == str(row[2])):
                                sub_item = QTreeWidgetItem([str(row[1]), str(row[4]), str(row[5]),"", "", "", str(row[6]), str(row[7])])
                                sub_items_R[j].addChild(sub_item)
                                if row[0] == "Folder":
                                    sub_items_R.append(sub_item)
                                    names_R.append(str(row[1]))
                                    path_R.append(str(row[2]))

                                sub_item.setTextAlignment(1, Qt.AlignCenter)
                                sub_item.setTextAlignment(2, Qt.AlignCenter)
                                sub_item.setTextAlignment(6, Qt.AlignCenter)
                                sub_item.setTextAlignment(7, Qt.AlignCenter)
                                sub_item.setBackground(6,QBrush(QColor("#E5CCFF")))
                                sub_item.setBackground(7,QBrush(QColor("#E5CCFF")))
                                sub_item.setBackground(1,QBrush(QColor(204, 255, 204)))
                                sub_item.setBackground(2,QBrush(QColor(204, 255, 204)))
                                sub_item.setIcon(5, QIcon('images/next.png'))
                                sub_item.setIcon(4, QIcon('images/back.png'))
                                _dir = str(row[1])
                                _path = dirR
                                _path = _path.split("/")
                                _path = '\\'.join(_path)
                                fileInfo = QFileInfo(_path +  str(row[2]) + _dir)
                                iconProvider = QFileIconProvider()
                                icon = iconProvider.icon(fileInfo)
                                sub_item.setIcon(0,icon)


        #_______search for all subfolders and subfiles in left directory________#
        for i in range(3, max_iL + 2):
            for row in all:
                if row[4] != "not present":
                    if row[3] == i:
                        for j, nam in enumerate(names_L):
                            if (path_L[j] + nam + '\\' == str(row[2])):
                                sub_item = QTreeWidgetItem([str(row[1]), str(row[4]), str(row[5]),"", "", "", str(row[6]), str(row[7])])
                                sub_items_L[j].addChild(sub_item)
                                if row[0] == "Folder":
                                    sub_items_L.append(sub_item)
                                    names_L.append(str(row[1]))
                                    path_L.append(str(row[2]))
                                sub_item.setTextAlignment(1, Qt.AlignCenter)
                                sub_item.setTextAlignment(2, Qt.AlignCenter)
                                sub_item.setTextAlignment(6, Qt.AlignCenter)
                                sub_item.setTextAlignment(7, Qt.AlignCenter)
                                sub_item.setBackground(6,QBrush(QColor("#E5CCFF")))
                                sub_item.setBackground(7,QBrush(QColor("#E5CCFF")))
                                sub_item.setBackground(1,QBrush(QColor(204, 255, 204)))
                                sub_item.setBackground(2,QBrush(QColor(204, 255, 204)))
                                sub_item.setIcon(4, QIcon('images/previous.png'))
                                sub_item.setIcon(5, QIcon('images/forward.png'))
                                _dir = str(row[1])
                                _path = dirL
                                _path = _path.split("/")
                                _path = '\\'.join(_path)
                                fileInfo = QFileInfo(_path +  str(row[2]) + _dir)
                                iconProvider = QFileIconProvider()
                                icon = iconProvider.icon(fileInfo)
                                sub_item.setIcon(0,icon)

        self.conn.commit()

    #___________function that copy the right file or folders to left path___________#
    def copy_right(self):
        for k in range(1, max_iR + 2):
            self.cur.execute('SELECT name FROM Sync WHERE (file_or_folder, Ldate, i, copied)=(?, ?, ?, ?)', ('File', 'not present', k, 0))
            nameFile = self.cur.fetchall()
            self.cur.execute('SELECT path FROM Sync WHERE (file_or_folder, Ldate, i, copied)=(?, ?, ?, ?)', ('File', 'not present', k, 0))
            pathFile = self.cur.fetchall()
            self.conn.commit()
            for j in range(0, len(nameFile)):
                self.cur.execute('UPDATE Sync SET copied=? WHERE path LIKE ?', (1, pathFile[j][0] + nameFile[j][0] + '%'))
                self.cur.execute('UPDATE Sync SET copied=? WHERE (name, Ldate, i)=(? ,?, ?)', (1, nameFile[j][0], 'not present', k))
                self.conn.commit()
                shutil.copy(dirR + pathFile[j][0] + nameFile[j][0], dirL + pathFile[j][0] + nameFile[j][0])

            self.cur.execute('SELECT name FROM Sync WHERE (file_or_folder, Ldate, i, copied)=(?, ?, ?, ?)', ('Folder', 'not present', k, 0))
            nameFolder = self.cur.fetchall()
            self.cur.execute('SELECT path FROM Sync WHERE (file_or_folder, Ldate, i, copied)=(?, ?, ?, ?)', ('Folder', 'not present', k, 0))
            pathFolder = self.cur.fetchall()
            self.conn.commit()
            for j in range(0, len(nameFolder)):
                self.cur.execute('UPDATE Sync SET copied=? WHERE path LIKE ? AND i=?', (1, pathFolder[j][0] + nameFolder[j][0] + '%', k))
                self.cur.execute('UPDATE Sync SET copied=? WHERE (name, Ldate, i)=(? ,?, ?)', (1, nameFolder[j][0], 'not present', k))
                self.conn.commit()
                shutil.copytree(dirR + pathFolder[j][0] + nameFolder[j][0], dirL + pathFolder[j][0] + nameFolder[j][0])
        self.Stacked.setCurrentWidget(self.copypage)                    #change the main page to Jobpage
        self.treeViewL.setRootIndex(self.fileModel.setRootPath(dirL))  #desplaying the path in Jobpage
        self.treeViewR.setRootIndex(self.fileModel.setRootPath(dirR))

    #___________function that copy the left file or folders to right path___________#
    def copy_left(self):
        for k in range(1, max_iL + 2):
            self.cur.execute('SELECT name FROM Sync WHERE (file_or_folder, Rdate, i, copied)=(?, ?, ?, ?)', ('File', 'not present', k, 0))
            nameFile = self.cur.fetchall()
            self.cur.execute('SELECT path FROM Sync WHERE (file_or_folder, Rdate, i, copied)=(?, ?, ?, ?)', ('File', 'not present', k, 0))
            pathFile = self.cur.fetchall()
            self.conn.commit()
            for j in range(0, len(nameFile)):
                self.cur.execute('UPDATE Sync SET copied=? WHERE path LIKE ?', (1, pathFile[j][0] + nameFile[j][0] + '%'))
                self.cur.execute('UPDATE Sync SET copied=? WHERE (name, Rdate, i)=(? ,?, ?)', (1, nameFile[j][0], 'not present', k))
                self.conn.commit()
                shutil.copy(dirL + pathFile[j][0] + nameFile[j][0], dirR + pathFile[j][0] + nameFile[j][0])

            self.cur.execute('SELECT name FROM Sync WHERE (file_or_folder, Rdate, i, copied)=(?, ?, ?, ?)', ('Folder', 'not present', k, 0))
            nameFolder = self.cur.fetchall()
            self.cur.execute('SELECT path FROM Sync WHERE (file_or_folder, Rdate, i, copied)=(?, ?, ?, ?)', ('Folder', 'not present', k, 0))
            pathFolder = self.cur.fetchall()
            self.conn.commit()
            for j in range(0, len(nameFolder)):
                self.cur.execute('UPDATE Sync SET copied=? WHERE path LIKE ? AND i=?', (1, pathFolder[j][0] + nameFolder[j][0] + '%', k))
                self.cur.execute('UPDATE Sync SET copied=? WHERE (name, Rdate, i)=(? ,?, ?)', (1, nameFolder[j][0], 'not present', k))
                self.conn.commit()
                shutil.copytree(dirL + pathFolder[j][0] + nameFolder[j][0], dirR + pathFolder[j][0] + nameFolder[j][0])
        self.Stacked.setCurrentWidget(self.copypage)                    #change the main page to Jobpage
        self.treeViewL.setRootIndex(self.fileModel.setRootPath(dirL))  #desplaying the path in Jobpage
        self.treeViewR.setRootIndex(self.fileModel.setRootPath(dirR))


    #___________function that copy both right & left files or folders to each other___________#
    def Sync_ko(self):

        #_____________copy the right files & folders in to left folders_____________#
        for k in range(1, max_iR + 2):
            self.cur.execute('SELECT name FROM Sync WHERE (file_or_folder, Ldate, i, copied)=(?, ?, ?, ?)', ('File', 'not present', k, 0))
            nameFile = self.cur.fetchall()
            self.cur.execute('SELECT path FROM Sync WHERE (file_or_folder, Ldate, i, copied)=(?, ?, ?, ?)', ('File', 'not present', k, 0))
            pathFile = self.cur.fetchall()
            self.conn.commit()
            for j in range(0, len(nameFile)):
                self.cur.execute('UPDATE Sync SET copied=? WHERE path LIKE ?', (1, pathFile[j][0] + nameFile[j][0] + '%'))
                self.cur.execute('UPDATE Sync SET copied=? WHERE (name, Ldate, i)=(? ,?, ?)', (1, nameFile[j][0], 'not present', k))
                self.conn.commit()
                shutil.copy(dirR + pathFile[j][0] + nameFile[j][0], dirL + pathFile[j][0] + nameFile[j][0])

            self.cur.execute('SELECT name FROM Sync WHERE (file_or_folder, Ldate, i, copied)=(?, ?, ?, ?)', ('Folder', 'not present', k, 0))
            nameFolder = self.cur.fetchall()
            self.cur.execute('SELECT path FROM Sync WHERE (file_or_folder, Ldate, i, copied)=(?, ?, ?, ?)', ('Folder', 'not present', k, 0))
            pathFolder = self.cur.fetchall()
            self.conn.commit()
            for j in range(0, len(nameFolder)):
                self.cur.execute('UPDATE Sync SET copied=? WHERE path LIKE ? AND i=?', (1, pathFolder[j][0] + nameFolder[j][0] + '%', k))
                self.cur.execute('UPDATE Sync SET copied=? WHERE (name, Ldate, i)=(? ,?, ?)', (1, nameFolder[j][0], 'not present', k))
                self.conn.commit()
                shutil.copytree(dirR + pathFolder[j][0] + nameFolder[j][0], dirL + pathFolder[j][0] + nameFolder[j][0])

        #_____________copy the left files & folders in to right folders_____________#
        if self.wjob.Task == "Sync":
            for k in range(1, max_iL + 2):
                self.cur.execute('SELECT name FROM Sync WHERE (file_or_folder, Rdate, i, copied)=(?, ?, ?, ?)', ('File', 'not present', k, 0))
                nameFile = self.cur.fetchall()
                self.cur.execute('SELECT path FROM Sync WHERE (file_or_folder, Rdate, i, copied)=(?, ?, ?, ?)', ('File', 'not present', k, 0))
                pathFile = self.cur.fetchall()
                self.conn.commit()
                for j in range(0, len(nameFile)):
                    self.cur.execute('UPDATE Sync SET copied=? WHERE path LIKE ?', (1, pathFile[j][0] + nameFile[j][0] + '%'))
                    self.cur.execute('UPDATE Sync SET copied=? WHERE (name, Rdate, i)=(? ,?, ?)', (1, nameFile[j][0], 'not present', k))
                    self.conn.commit()
                    shutil.copy(dirL + pathFile[j][0] + nameFile[j][0], dirR + pathFile[j][0] + nameFile[j][0])

                self.cur.execute('SELECT name FROM Sync WHERE (file_or_folder, Rdate, i, copied)=(?, ?, ?, ?)', ('Folder', 'not present', k, 0))
                nameFolder = self.cur.fetchall()
                self.cur.execute('SELECT path FROM Sync WHERE (file_or_folder, Rdate, i, copied)=(?, ?, ?, ?)', ('Folder', 'not present', k, 0))
                pathFolder = self.cur.fetchall()
                self.conn.commit()
                for j in range(0, len(nameFolder)):
                    self.cur.execute('UPDATE Sync SET copied=? WHERE path LIKE ? AND i=?', (1, pathFolder[j][0] + nameFolder[j][0] + '%', k))
                    self.cur.execute('UPDATE Sync SET copied=? WHERE (name, Rdate, i)=(? ,?, ?)', (1, nameFolder[j][0], 'not present', k))
                    self.conn.commit()
                    shutil.copytree(dirL + pathFolder[j][0] + nameFolder[j][0], dirR + pathFolder[j][0] + nameFolder[j][0])
        self.Stacked.setCurrentWidget(self.copypage)                    #change the main page to Jobpage
        self.treeViewL.setRootIndex(self.fileModel.setRootPath(dirL))  #desplaying the path in Jobpage
        self.treeViewR.setRootIndex(self.fileModel.setRootPath(dirR))


    #_____________function to handle the OPtion button____________#
    def Open_Options(self):
        self.w_opt = Opt(self)
        self.w_opt.show()

    #_____________function to handle the Newjob button
    def open_New_Job(self):
        self.i += 1
        self.wjob = New_Job(self)
        self.wjob.show()
        self.wjob.OKB.clicked.connect(self.newjob_added)

    #______________function to handle the Newgroup button__________#
    def open_New_Group(self):
        self.w_New_Group = New_Group(self)
        self.w_New_Group.setFixedSize(450, 220)
        self.w_New_Group.lineEdit.setText('')
        self.w_New_Group.show()

    #_____________when new job addded_____________#
    def newjob_added(self, NewJobText):
        self.toolBar_3.setVisible(True)
        self.toolBar_4.setVisible(True)
        self.Stacked.setCurrentWidget(self.nopath)                #change the main window to Nopath page

        self.left.setText('Please click here to select folder')
        self.left.setIcon(QIcon('images/select-folder.ico'))
        self.right.setText('Please click here to select folder')
        self.right.setIcon(QIcon('images/select-folder.ico'))

        self.center.setEnabled(False)
        self.actionAnalyze.setEnabled(False)
        self.actionSync.setEnabled(False)

        self.l1_child = QTreeWidgetItem([self.wjob.NewJobText])
        self.l1.addChild(self.l1_child)
        self.treeWidget.addTopLevelItem(self.l1)                #add a sub item to the left toolbar

        if self.wjob.Task == "Sync":
            self.l1_child.setIcon(0, QIcon('images/sync3.png'))
            self.center.setIcon(QIcon('images/syncar'))
        elif self.wjob.Task == "backup":
            self.l1_child.setIcon(0, QIcon('images/backup4.png'))
            self.center.setIcon(QIcon('images/backupar'))

        self.rowPosition = self.tableWidget.rowCount()          #insert a row
        self.tableWidget.insertRow(self.rowPosition)
        self.name_array.append(self.wjob.NewJobText)

        self.treeWidget.itemSelectionChanged.connect(self.Creat_NewJob)



    #___________function to handle the selection change in left window___________#
    def Creat_NewJob(self):
        if len(self.Lpath_array) > self.i and len(self.Rpath_array) > self.i:  #if both paths are selected
            self.Stacked.setCurrentWidget(self.analyze)
        else:
            self.Stacked.setCurrentWidget(self.nopath)
        getSelected = self.treeWidget.selectedItems()

        #insert a row in tha table:
        self.tableWidget.setItem(self.rowPosition, 0, QTableWidgetItem(self.name_array[self.i]))
        self.tableWidget.setItem(self.rowPosition, 1, QTableWidgetItem("idle"))
        self.tableWidget.setItem(self.rowPosition, 5 , QTableWidgetItem(QtCore.QDateTime.currentDateTime().toString()))


        #if an item is clicked
        if getSelected:
            baseNode = getSelected[0]
            Job_name = baseNode.text(0)
            self.toolBar_3.setVisible(True)
            if len(self.Lpath_array) > self.i:    #if left path is entered
                self.tableWidget.setItem(self.rowPosition, 3, QTableWidgetItem(self.Lpath_array[self.i]))
            if len(self.Rpath_array) > self.i:   #if right path is entered
                self.tableWidget.setItem(self.rowPosition, 4, QTableWidgetItem(self.Rpath_array[self.i]))
            if Job_name == "All jobs":                         #if the selected item is Alljobs
                self.Stacked.setCurrentWidget(self.alljobs)
                self.toolBar_3.setVisible(False)


#___________NewJob dialog box__________#
class New_Job(Ui_New_Job, LandingPageBase):
    def __init__(self, parent=None):
        LandingPageBase.__init__(self, parent)
        self.setupUi(self)
        self.OKB.clicked.connect(self.getText)
        self.lineEdit.textChanged.connect(self.Ok_enable)
        if self.radioButton.isChecked:
            glob_synced = 1
        self.NewJobText = ""

    #_________Ok button is enabled if the jobname is entered__________#
    def Ok_enable(self):
        if len(self.lineEdit.text()) >= 1:
            self.OKB.setEnabled(True)
        elif len(self.lineEdit.text()) < 1:
            self.OKB.setEnabled(False)

    #__________get the name & model of the job_________#
    def getText(self):
        self.NewJobText = self.lineEdit.text()
        if self.radioButton.isChecked() == True:
            self.Task = "Sync"
        else:
            self.Task = "backup"



#________option dialog box__________#
class  Opt (Options, QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setupUi(self)

        self.setWindowTitle("Options")
        self.vStackedWidget.setCurrentIndex(0)
        self.list.setSpacing(15)
        self.list.itemClicked.connect(self.item_click)
        self.plus1.clicked.connect(self.additem_f)
        self.minus1.clicked.connect(self.delitem_f)
        self.plus2.clicked.connect(self.additem_t)
        self.minus2.clicked.connect(self.delitem_t)

    def item_click(self, item):
        if item.text() == "General":
            self.vStackedWidget.setCurrentWidget(self.Generalp)
            #QListWidget.listWidgetTimeSet.setSelected(true)
        elif item.text() == "Filters":
            self.vStackedWidget.setCurrentWidget(self.Filtersp)
        elif item.text() == "Auto":
            self.vStackedWidget.setCurrentWidget(self.Autop)

    def additem_f (self):
        self.listWidget1.addItem("hi")

    def delitem_f (self):
        self.listWidget1.addItem("none")

    def additem_t (self):
        self.listWidget2.addItem("hi")

    def delitem_t(self):
        self.listWidget2.addItem('none')

#___________New group Dialog box____________#
class New_Group(Ui_New_Group, LandingPageBas):
    def __init__(self, parent=None):
        LandingPageBas.__init__(self, parent)
        self.setupUi(self)
        self.OKB.clicked.connect(self.getText)
        self.lineEdit.textChanged.connect(self.Ok_enable)

    def Ok_enable(self):
        if len(self.lineEdit.text()) >= 1:
            self.OKB.setEnabled(True)
        elif len(self.lineEdit.text()) < 1:
            self.OKB.setEnabled(False)
    def getText(self):
        NewGroupText = self.lineEdit.text()
        print(NewGroupText)



if __name__ == "__main__":
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    window = Main()
    window.show()
    sys.exit(app.exec_())


