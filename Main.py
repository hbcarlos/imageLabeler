#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
App for image labeling
Author: Carlos Herrero
"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtWidgets import QListView, QMessageBox, QInputDialog, QFileDialog, QLabel
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap, QPen, QFont
from PyQt5.QtCore import Qt, QModelIndex, QRectF

import os
import re
import json

PERSON = 0
DORSAL = 1
NUMBER = 2

step = PERSON
person = None
graphic = None

fileLabels = None
directory = None

data = {}
pos = None
photos = []

listView = None
listLabels = None

class Photo(QGraphicsScene):
    """
    Class to manage the photos, select and draw the labels.
    This class heritage from QGraphicsScene which let us add the image, draw beyond
    and all the mouse events we need to select the pixels for the label.

    params:
        - name: photo name.
        - parent: GUI Widget where the Photo is placed. (QMainWindow)
    """

    def __init__(self, name, parent=None):
        super(Photo, self).__init__(parent)
        global step, person, graphic, listView, listLabels
        self.parent = parent
        self.name = name

        step = PERSON
        person = None
        graphic = None

        listLabels = QStandardItemModel()
        listView.setModel(listLabels)

        self.img = QPixmap(directory + "/" + self.name)
        self.addItem(QGraphicsPixmapItem(self.img))
        self.initPeople()

    def initPeople(self):
        """
        This function is for load and draws the labels of a photo when is initialized
        """
        people = data[self.name]
        for i in range(0, len(people)) :
            person = people[i]
            position = person['position']

            self.addRect(position[0], position[1], abs(position[0]-position[2]), abs(position[1]-position[3]), pen=QPen(Qt.red))
            txt = self.addText(str(i))
            txt.setPos(position[0], position[1])
            txt.setDefaultTextColor(Qt.red)

            if person.get('number', None) :
                number = person['number']['number']
                numberPosition = person['number']['position']

                listLabels.appendRow(QStandardItem(str(i) + ") " + str(number)))
                self.addRect(numberPosition[0], numberPosition[1], abs(numberPosition[0]-numberPosition[2]), abs(numberPosition[1]-numberPosition[3]), pen=QPen(Qt.yellow))
                txt = self.addText(str(number))
                txt.setPos(numberPosition[0], numberPosition[1])
                txt.setDefaultTextColor(Qt.yellow)
            
            else :
                listLabels.appendRow(QStandardItem(str(i) + ") No number"))

    def keyPressEvent(self, event):
        super(Photo, self).keyPressEvent(event)
        self.parent.keyPressEvent(event)

    def mousePressEvent(self, event):
        """
        Function to capture mouse press event and obtain the pixel.
        """
        super(Photo, self).mousePressEvent(event)
        global step, person, graphic
        
        x = event.scenePos().x()
        y = event.scenePos().y()

        x = x if x >= 0 else 0
        x = x if x < self.img.width() - 20 else self.img.width() - 20

        y = y if y >= 0 else 0
        y = y if y < self.img.height() - 20 else self.img.height() - 20

        if step == PERSON :
            person = { 'position': [x, y, 0, 0] }
            graphic = self.addRect(x, y, 0, 0, pen=QPen(Qt.gray))
        
        elif step == DORSAL :
            person['number'] = { 'position': [x, y, 0, 0] }
            graphic = self.addRect(x, y, 0, 0, pen=QPen(Qt.gray))

        self.update()

    def mouseMoveEvent(self, event):
        """
        Function to capture mouse movement event and obtain the pixel.
        """
        super(Photo, self).mouseMoveEvent(event)
        global step, person, graphic
        
        if graphic and person :
            x = event.scenePos().x()
            y = event.scenePos().y()

            x = x if x >= 0 else 0
            x = x if x < self.img.width() else self.img.width()

            y = y if y >= 0 else 0
            y = y if y < self.img.height() else self.img.height()

            if step == PERSON :
                iniX = person['position'][0]
                iniY = person['position'][1]
                
                x = x if x >= iniX else iniX
                y = y if y >= iniY else iniY

                graphic.setRect(QRectF(iniX, iniY, abs(iniX - x), abs(iniY - y)))
                graphic.update()
            
            elif person.get('number', None) and step == DORSAL :
                iniX = person['number']['position'][0]
                iniY = person['number']['position'][1]

                x = x if x >= iniX else iniX
                y = y if y >= iniY else iniY

                graphic.setRect(QRectF(iniX, iniY, abs(iniX - x), abs(iniY - y)))
                graphic.update()

        self.update()

    def mouseReleaseEvent(self, event):
        """
        Function to capture mouse release event and obtain the pixel.
        """
        super(Photo, self).mouseReleaseEvent(event)
        global data, step, person, graphic

        if graphic and person :
            x = event.scenePos().x()
            y = event.scenePos().y()

            x = x if x >= 0 else 0
            x = x if x < self.img.width() else self.img.width()

            y = y if y >= 0 else 0
            y = y if y < self.img.height() else self.img.height()

            if step == PERSON :
                iniX = person['position'][0]
                iniY = person['position'][1]

                x = x if x >= iniX else iniX
                y = y if y >= iniY else iniY

                graphic.setRect(QRectF(iniX, iniY, abs(iniX - x), abs(iniY - y)))
                graphic.setPen(QPen(Qt.red))
                graphic.update()

                txt = self.addText(str(len(data[self.name])))
                txt.setPos(iniX, iniY)
                txt.setDefaultTextColor(Qt.red)

                person['position'][2] = x
                person['position'][3] = y
                step = DORSAL
                graphic = None
            
            elif person.get('number', None) and step == DORSAL :
                number, ok = QInputDialog.getInt(self.parent, "Number", "")

                if ok :
                    iniX = person['number']['position'][0]
                    iniY = person['number']['position'][1]
                    
                    x = x if x >= iniX else iniX
                    y = y if y >= iniY else iniY

                    graphic.setRect(QRectF(iniX, iniY, abs(iniX - x), abs(iniY - y)))
                    graphic.setPen(QPen(Qt.yellow))
                    graphic.update()

                    txt = self.addText(str(number))
                    txt.setPos(iniX, iniY)
                    txt.setDefaultTextColor(Qt.yellow)

                    listLabels.appendRow(QStandardItem(str(len(data[self.name])) + ") " + str(number)))

                    person['number']['number'] = number
                    person['number']['position'][2] = x
                    person['number']['position'][3] = y
                    data[self.name].append(person)
                    
                    step = PERSON
                    person = None
                    graphic = None

                else :
                    self.removeItem(graphic)
                    del person['number']
                    step = DORSAL
                    graphic = None

        self.update()

class Main(QMainWindow):
    """
    Main widget of this app.
    """

    def __init__(self):
        super(Main, self).__init__()
        # Main windows config
        self.resize(1080, 800)
        self.setWindowTitle('Labeler')
        #self.setWindowIcon(QIcon('web.png'))
        self.statusBar().showMessage('Ready...')

        self.initToolbar()
        self.setCentralWidget(self.initLayoutPhoto())
        self.show()

    def initToolbar(self):
        """
        Funtion to inicialice the tool bar and his components
        """
        # Tool Bar
        self.toolbar = self.addToolBar('Menu')

        newFile = QAction('New file', self)
        newFile.triggered.connect(self.newFile)
        openFile = QAction('Open file', self)
        openFile.triggered.connect(self.openFile)

        loadData = QAction('Load data', self)
        loadData.triggered.connect(self.loadData)
        saveData = QAction('Save data', self)
        saveData.triggered.connect(self.saveData)
        noLabeled = QAction('No labeled', self)
        noLabeled.triggered.connect(self.noLabeled)
        allPhotos = QAction('All photos', self)
        allPhotos.triggered.connect(self.allPhotos)

        previusPhoto = QAction('Previus photo', self)
        previusPhoto.triggered.connect(self.previusPhoto)
        nextPhoto = QAction('Next photo', self)
        nextPhoto.triggered.connect(self.nextPhoto)

        newPerson = QAction('New person', self)
        newPerson.triggered.connect(self.newPerson)

        self.toolbar.addAction(newFile)
        self.toolbar.addAction(openFile)
        self.toolbar.insertSeparator(loadData)
        self.toolbar.addAction(loadData)
        self.toolbar.addAction(saveData)
        self.toolbar.addAction(noLabeled)
        self.toolbar.addAction(allPhotos)
        self.toolbar.insertSeparator(previusPhoto)
        self.toolbar.addAction(previusPhoto)
        self.toolbar.addAction(nextPhoto)
        self.toolbar.insertSeparator(newPerson)
        self.toolbar.addAction(newPerson)

    def initLayoutPhoto(self):
        """
        Function to create the main layout with all the widgets for show the images and labels.
        """
        global listView
        # Screen
        screen = QHBoxLayout()

        # Photo
        layoutPhotos = QVBoxLayout()
        self.viewPhoto = QGraphicsView()
        self.viewPhoto.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.viewPhoto.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layoutPhotos.addWidget(self.viewPhoto)
        screen.addLayout(layoutPhotos, 10)

        # Tools
        tools = QVBoxLayout()
        tools.setAlignment(Qt.AlignTop)
        labelPeople = QLabel("People:\n")
        labelPeople.setFont(QFont("Times", 20, QFont.Bold))
        tools.addWidget(labelPeople)

        listView = QListView()
        listView.clicked[QModelIndex].connect(self.onClicked)
        tools.addWidget(listView)
        screen.addLayout(tools, 1)
        
        widget = QWidget()
        widget.setLayout(screen)
        return widget

    def keyPressEvent(self, event):
        super(Main, self).keyPressEvent(event)
        
        if event.key() == Qt.Key_N :
            self.newFile()
        elif event.key() == Qt.Key_O :
            self.openFile()
        elif event.key() == Qt.Key_L :
            self.loadData()
        elif event.key() == Qt.Key_S :
            self.saveData()
        elif event.key() == Qt.Key_1 :
            self.noLabeled()
        elif event.key() == Qt.Key_2 :
            self.allPhotos()
        elif event.key() == Qt.Key_Left :
            self.previusPhoto()
        elif event.key() == Qt.Key_Right :
            self.nextPhoto()
        elif event.key() == Qt.Key_A :
            self.previusPhoto()
        elif event.key() == Qt.Key_D :
            self.nextPhoto()
        elif event.key() == Qt.Key_P :
            self.newPerson()

    def openFile(self):
        """
        Function to capture the Open file action.
        Allows us to open a folder with the lables' file and his photos to continue labelling.
        Open the file and load all the labels verifying what images are labeled.
        """
        global fileLabels, directory

        try:
            self.statusBar().showMessage("Opening file...")
            name, ok = QFileDialog.getOpenFileName(self, 'Select file')
            
            if ok :
                fileLabels = name
                directory = os.path.dirname(fileLabels)
                self.statusBar().showMessage("Ready...")
                self.loadData()
            else :
                fileLabels = None
                directory = None
                self.statusBar().showMessage("No file!")
        
        except FileNotFoundError:
            QMessageBox.question(self, 'Open file', "File " + fileLabels + " not found.", QMessageBox.Ok, QMessageBox.Ok)
        except TypeError:
            QMessageBox.question(self, 'Open file', "No file", QMessageBox.Ok, QMessageBox.Ok)

    def newFile(self):
        """
        Function to capture the New file action.
        Allows us to create a new file for a folder with images to start labelling.
        Create the file and load the images to start labelling.
        """
        global fileLabels, directory

        try:
            self.statusBar().showMessage("Creating file...")
            name, ok = QFileDialog.getSaveFileName(self, 'Create file')
        
            if ok :
                fileLabels = name
                directory = os.path.dirname(fileLabels)
                file = open(name, 'w')
                json.dump({}, file)
                file.close()
                self.statusBar().showMessage("Ready...")
                self.loadData()
            else :
                fileLabels = None
                directory = None
                self.statusBar().showMessage("No file!")
        
        except FileNotFoundError:
            QMessageBox.question(self, 'New file', "File " + fileLabels + " not found.", QMessageBox.Ok, QMessageBox.Ok)
        except TypeError:
            QMessageBox.question(self, 'New file', "No file", QMessageBox.Ok, QMessageBox.Ok)
    
    def loadData(self):
        """
        Function to capture the Load data action.
        Allows us to refresh the folder to verify if there are new images or we delete any image
        applying the changes to the labels in the opened file.
        """

        global fileLabels, directory, data, pos, photos

        print("fileLabels:" + fileLabels)
        print("directory:" + directory)
        print("data:" + str(data))
        print("pos:" + str(pos))
        print("photos:" + str(photos))

        try:
            self.statusBar().showMessage("Loading data...")

            if fileLabels and directory :
                file = open(fileLabels, 'r')
                data = json.load(file)
                
                images = set(data.keys())

                cont = 0
                first = True

                for file in os.listdir(directory):
                    if re.search('(.jpg|.jpeg|.png|.webp)$', file) :
                        label = data.get(file, None)

                        if label != None :
                            images.remove(file)
                            
                            if first and len(label) > 0 :
                                cont += 1
                            else :
                                first = False

                        else :
                            data[file] = []
                            first = False
                            
                
                for image in list(images) :
                    data.pop(image)

                photos = list(data.keys())
                pos = cont if cont < len(photos) else 0
                self.viewPhoto.setScene(Photo(photos[pos], parent=self))
                self.statusBar().showMessage("Photo: " + photos[pos] + " " + str(pos+1) + "/" + str(len(photos)))
            
            else :
                self.statusBar().showMessage("Ready...")

        except FileNotFoundError:
            QMessageBox.question(self, 'Load data', "File " + fileLabels + " not found.", QMessageBox.Ok, QMessageBox.Ok)
        except TypeError:
            QMessageBox.question(self, 'Load data', "No file", QMessageBox.Ok, QMessageBox.Ok)

    def saveData(self):
        """
        Function to capture the Save data action.
        Allows us to save the labels in the selected file.
        """

        global fileLabels, data, pos, photos, step, person, graphic

        try:
            self.statusBar().showMessage('Saving data...')

            if person :
                listLabels.appendRow(QStandardItem(str(len(data[photos[pos]])) + ") No number"))
                data[photos[pos]].append(person)
                step = PERSON
                person = None
                graphic = None

            file = open(fileLabels, 'w')
            json.dump(data, file)
            self.statusBar().showMessage("Photo: " + photos[pos] + " " + str(pos+1) + "/" + str(len(photos)))

        except FileNotFoundError:
            QMessageBox.question(self, 'Save data', "File " + fileLabels + " not found.", QMessageBox.Ok, QMessageBox.Ok)
        except TypeError:
            QMessageBox.question(self, 'Save data', "No file", QMessageBox.Ok, QMessageBox.Ok)
    
    def noLabeled(self):
        """
        Function to capture the No labeled action.
        Allows us to show only the no labeled images (does not modify the labels or file labels).
        """
        global data, photos, pos
        self.statusBar().showMessage('Serching photos...')
        self.saveData()
        
        aux = []
        for image in photos:
            if len(data[image]) == 0 :
                aux.append(image)

        if len(aux) == 0 :
            QMessageBox.question(self, 'No labeled', "All photos are labeled", QMessageBox.Ok, QMessageBox.Ok)
            self.statusBar().showMessage('Ready...')
        else :
            photos = aux
            pos = 0
            self.viewPhoto.setScene(Photo(photos[pos], parent=self))
            self.statusBar().showMessage("Photo: " + photos[pos] + " " + str(pos+1) + "/" + str(len(photos)))
    
    def allPhotos(self):
        """
        Function to capture the All photos action.
        Allows us to show all photos at the actual folder again.
        """
        global data, photos, pos
        self.statusBar().showMessage('Searching photos...')
        self.saveData()
        
        photos = list(data.keys())

        if len(photos) == 0 :
            QMessageBox.question(self, 'All photos', "No photos", QMessageBox.Ok, QMessageBox.Ok)
            self.statusBar().showMessage('Ready...')
        else :
            cont = 0
            for image in photos:
                if len(data[image]) == 0 :
                    pos = cont
                    break
                
                cont += 1
            
            pos = cont if cont < len(photos) else 0
            self.viewPhoto.setScene(Photo(photos[pos], parent=self))
            self.statusBar().showMessage("Photo: " + photos[pos] + " " + str(pos+1) + "/" + str(len(photos)))
        
    def previusPhoto(self):
        """
        Function to capture the previus photo action.
        Allows us to change the photo to label, saving the labels in the file.
        """
        global data, pos, photos, step, person, graphic
        
        try:
            if person :
                listLabels.appendRow(QStandardItem(str(len(data[photos[pos]])) + ") No number"))
                data[photos[pos]].append(person)
                step = PERSON
                person = None
                graphic = None

            self.saveData()

            pos = pos - 1 if pos > 0 else len(photos) - 1
            self.viewPhoto.setScene(Photo(photos[pos], parent=self))
            self.statusBar().showMessage("Photo: " + photos[pos] + " " + str(pos+1) + "/" + str(len(photos)))

        except TypeError:
            QMessageBox.question(self, 'Previus photo', "No photos", QMessageBox.Ok, QMessageBox.Ok)

    def nextPhoto(self):
        """
        Function to capture the next photo action.
        Allows us to change the photo to label, saving the labels in the file.
        """
        global data, pos, photos, step, person, graphic
        
        try:
            if person :
                listLabels.appendRow(QStandardItem(str(len(data[photos[pos]])) + ") No number"))
                data[photos[pos]].append(person)
                step = PERSON
                person = None
                graphic = None
            
            self.saveData()

            pos = pos + 1 if pos < len(photos) - 1 else 0
            self.viewPhoto.setScene(Photo(photos[pos], parent=self))
            self.statusBar().showMessage("Photo: " + photos[pos] + " " + str(pos+1) + "/" + str(len(photos)))

        except TypeError:
            QMessageBox.question(self, 'Next photo', "No photos", QMessageBox.Ok, QMessageBox.Ok)

    def newPerson(self):
        """
        Function to capture the New person action.
        Allows us add new label without number.
        """
        global data, pos, photos, step, person, graphic
        
        if person :
            listLabels.appendRow(QStandardItem(str(len(data[photos[pos]])) + ") No number"))
            data[photos[pos]].append(person)
            step = PERSON
            person = None
            graphic = None
    
    def onClicked(self, index):
        """
        Function to capture the click event in a label at the right panel.
        Allows us delete a label in a photo.
        """
        listLabels.removeRow(index.row())
        del data[photos[pos]][index.row()]
        self.viewPhoto.setScene(Photo(photos[pos], parent=self))
        self.statusBar().showMessage("Photo: " + photos[pos] + " " + str(pos+1) + "/" + str(len(photos)))

if __name__ == '__main__':
    app = QApplication([])
    main = Main()
    app.exec()