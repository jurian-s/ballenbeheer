# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 21:44:29 2024

@author: Jurian
"""

import json
import csv
import datetime
import sys
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QCompleter, QBoxLayout, QMessageBox, QPushButton, QListWidget, QListWidgetItem, QLabel, QComboBox, QTableView, QFrame, QHeaderView, QFileDialog
from PySide6 import QtGui
from PySide6.QtCore import Qt
import pyqtgraph as pg


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self) 
        self.DB = BallenBestand()
        MainButtons = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        StartCountButton = QPushButton("Start telling")
        StartCountButton.clicked.connect(self.startCount)
        
        BestandBeheerButton = QPushButton("Beheer ballenbestand")
        BestandBeheerButton.clicked.connect(self.BeheerBallenbestand)
        
        ExporteerButton = QPushButton("Exporteer")
        ExporteerButton.clicked.connect(self.ExportTelling)
        
        StatsButton = QPushButton("Statistieken")
        StatsButton.clicked.connect(self.Statistieken)
        
        MainButtons.addWidget(StartCountButton)
        MainButtons.addWidget(BestandBeheerButton)
        MainButtons.addWidget(ExporteerButton)
        MainButtons.addWidget(StatsButton)
        
        self.BalStatsPerLoc = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        
        self.HeaderBalStats = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.HeaderBalStats.addWidget(QLabel("Balwaardes in: "))
        self.BalStatYear =  QComboBox()
        self.populateYearComboBox(self.BalStatYear)        
        self.HeaderBalStats.addWidget(self.BalStatYear)
        self.LocatieLabelList = []
        self.TellingSelectorList = []
        self.waardeList = []
        self.TotaleWaardeLabel = QLabel(f"Totale waarde (Zonder ballen niet in gebruik): {sum(self.waardeList):.2f}")
        self.BalStatsPerLoc.addLayout(self.HeaderBalStats)
        self.TellingLocMap = {}
        for Idx, locaties in enumerate(self.DB.Ballenbestand["Telling"]):
            Balstat = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            Loc = self.DB.Ballenbestand["LocatieDict"][str(locaties)]
            nBalls = len(list(self.DB.Ballenbestand["Telling"][locaties].values())[-1]["Ballen"])
            Value = self.DB.getValueTelling(list(self.DB.Ballenbestand["Telling"][locaties].values())[-1], int(self.BalStatYear.currentText()))
            self.waardeList.append(Value)
            self.LocatieLabelList.append(QLabel(f"Op {Loc} zijn er {nBalls} ballen met een waarde van {Value:.2f} Euro"))
            self.TellingSelectorList.append(QComboBox())
            self.TellingSelectorList[Idx].currentIndexChanged.connect(self.changeSelectedCount)
            self.TellingLocMap[locaties] = Idx
            for keys in self.DB.Ballenbestand["Telling"][locaties].keys():                
                self.TellingSelectorList[Idx].addItem(keys)
            self.TellingSelectorList[Idx].setCurrentIndex(self.TellingSelectorList[Idx].count()-1)
            Balstat.addWidget(self.LocatieLabelList[Idx], 5) 
            Balstat.addWidget(self.TellingSelectorList[Idx], 1) 
            self.BalStatsPerLoc.addLayout(Balstat)
        
        self.TotaleWaardeLabel.setText(f"Totale waarde (Zonder ballen niet in gebruik): {sum(self.waardeList):.2f}")
        self.BalStatsPerLoc.addWidget(self.TotaleWaardeLabel)
        self.layout.addLayout(self.BalStatsPerLoc)
        self.layout.addLayout(MainButtons)
        
        
        
        
    def UpdateBalStats(self):
        if len(self.LocatieLabelList) != len(widget.DB.Ballenbestand["Telling"].keys()):
            self.LocatieLabelList = []
            self.TellingSelectorList = []
            self.waardeList = []
            self.clearLayout(self.BalStatsPerLoc, 1)
            self.BalStatsPerLoc = QBoxLayout(QBoxLayout.Direction.TopToBottom)          
            self.BalStatsPerLoc.addLayout(self.HeaderBalStats)                
            for locaties in self.DB.Ballenbestand["Telling"]:
                Balstat = QBoxLayout(QBoxLayout.Direction.LeftToRight)
                Loc = self.DB.Ballenbestand["LocatieDict"][str(locaties)]
                nBalls = len(list(self.DB.Ballenbestand["Telling"][locaties].values())[-1]["Ballen"])
                Value = self.DB.getValueTelling(list(self.DB.Ballenbestand["Telling"][locaties].values())[-1], int(self.BalStatYear.currentText()))
                self.waardeList.append(Value)
                self.LocatieLabelList.append(QLabel(f"Op {Loc} zijn er {nBalls} ballen met een waarde van {Value:.2f} Euro"))
                self.TellingSelectorList.append(QComboBox())
                self.TellingSelectorList[-1].currentIndexChanged.connect(self.changeSelectedCount)
                for keys in self.DB.Ballenbestand["Telling"][locaties].keys():                
                    self.TellingSelectorList[-1].addItem(keys)
                Balstat.addWidget(self.LocatieLabelList[-1], 5) 
                Balstat.addWidget(self.TellingSelectorList[-1], 1) 
                self.BalStatsPerLoc.addLayout(Balstat)
            self.TotaleWaardeLabel = QLabel(f"Totale waarde (Zonder ballen niet in gebruik): {sum(self.waardeList):.2f}")
            self.BalStatsPerLoc.addWidget(self.TotaleWaardeLabel)
            self.layout.insertLayout(1, self.BalStatsPerLoc)
            
            self.TotaleWaardeLabel.setText(f"Totale waarde (Zonder ballen niet in gebruik): {sum(self.waardeList):.2f}")
            
        else:
            for i in range(len(self.LocatieLabelList)):
                locaties = list(self.DB.Ballenbestand["Telling"].keys())[i]
                Loc = self.DB.Ballenbestand["LocatieDict"][str(locaties)]
                # if self.TellingSelectorList[i].currentIndex() > len(list(self.DB.Ballenbestand["Telling"][locaties].values())):
                #     self.TellingSelectorList[i].setCurrentIndex(len(list(self.DB.Ballenbestand["Telling"][locaties].values())))
                SelectedCount = self.TellingSelectorList[i].currentIndex()
                if len(self.DB.Ballenbestand["Telling"][locaties].keys()) != self.TellingSelectorList[i].count():
                    self.TellingSelectorList[i].clear()
                    for keys in self.DB.Ballenbestand["Telling"][locaties].keys():                
                        self.TellingSelectorList[i].addItem(keys)
                    if SelectedCount+1 > len(self.DB.Ballenbestand["Telling"][locaties].keys()):
                        SelectedCount = len(self.DB.Ballenbestand["Telling"][locaties].keys())-1
                    self.TellingSelectorList[i].setCurrentIndex(SelectedCount)
                Value = self.DB.getValueTelling(list(self.DB.Ballenbestand["Telling"][locaties].values())[SelectedCount], int(self.BalStatYear.currentText()))
                self.waardeList[i] = Value
                nBalls = len(list(self.DB.Ballenbestand["Telling"][locaties].values())[SelectedCount]["Ballen"])
                self.LocatieLabelList[i].setText((f"Op {Loc} zijn er {nBalls} ballen met een waarde van {Value:.2f} Euro"))
                
            self.TotaleWaardeLabel.setText(f"Totale waarde (Zonder ballen niet in gebruik): {sum(self.waardeList):.2f}")
            
        
    def clearLayout(self, Layout, startI):
                for i in reversed(range(startI, Layout.count())):
                    item = Layout.takeAt(i)
                    if item.layout():
                        self.clearLayout(item.layout(), 0)
                    if item.widget():
                        item.widget().deleteLater()
                        
    def populateYearComboBox(self, Combobox):
        currentYear = datetime.datetime.now().year
        numYears = 25  # You can adjust the number of years to display
        for i in range(numYears):
            Combobox.addItem(str((currentYear -(numYears - 2)) + i))
        Combobox.setCurrentText(str(currentYear))
        Combobox.currentIndexChanged.connect(self.UpdateBalStats)
            
            
            
    def changeSelectedCount(self, index):
        sender = self.sender()  # Get the sender object
        comboBoxIndex = self.TellingSelectorList.index(sender)  # Get the index of the combobox in the list
        SelectedCount = sender.currentIndex()  # Get the selected item text
        locaties = list(self.DB.Ballenbestand["Telling"].keys())[comboBoxIndex]
        Loc = self.DB.Ballenbestand["LocatieDict"][str(locaties)]
        Value = self.DB.getValueTelling(list(self.DB.Ballenbestand["Telling"][locaties].values())[SelectedCount], int(self.BalStatYear.currentText()))
        self.waardeList[comboBoxIndex] = Value
        nBalls = len(list(self.DB.Ballenbestand["Telling"][locaties].values())[SelectedCount]["Ballen"])
        self.LocatieLabelList[comboBoxIndex].setText((f"Op {Loc} zijn er {nBalls} ballen met een waarde van {Value} Euro"))
        self.TotaleWaardeLabel.setText(f"Totale waarde (Zonder ballen niet in gebruik): {sum(self.waardeList):.2f}")
        
    def ExportTelling(self):
        SaveDialog = QFileDialog.getSaveFileName(self, dir="count", caption="Opslaan", filter="CSV file (*.csv)")
        FieldNames = ["BalID", "Type", "Jaar", "Waarde", "LocatieGeteld", "Datum Geteld"]
        ExportList = []
        for i in range(len(self.TellingSelectorList)):
            LocIdx = list(self.DB.Ballenbestand["Telling"].keys())[i]
            Locatie = self.DB.Ballenbestand["LocatieDict"][str(LocIdx)]
            Telling = self.TellingSelectorList[i].currentText()
            for Bal in self.DB.Ballenbestand["Telling"][LocIdx][Telling]["Ballen"]:
                BalData = self.DB.Ballenbestand["Balvoorraad"][Bal]
                BalInfo = {"BalID": Bal,
                           "Type": self.DB.Ballenbestand["BalTypeDict"][str(BalData["Soort"])]["Balsoort"],
                           "Jaar": BalData["Jaar"],
                           "Waarde": self.DB.getValueBall(Bal, int(self.BalStatYear.currentText())),
                           "LocatieGeteld": Locatie,
                           "Datum Geteld": Telling}
                ExportList.append(BalInfo)
        with open(SaveDialog[0], 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=FieldNames, dialect="excel")
            writer.writeheader()
            writer.writerows(ExportList)
                
        
        
    def Statistieken(self):
        self.Statspanel = QWidget()
        self.Statspanel.setWindowModality(Qt.ApplicationModal)
        StatsLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.Statspanel)
        HeaderLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        Header = QLabel("Statistieken")
        Font = Header.font()
        Font.setPointSize(20)
        Header.setFont(Font)
        HeaderLayout.addWidget(Header)
        self.StatSelect = QComboBox()
        self.StatSelect.addItem("Aantal ballen")
        self.StatSelect.addItem("Waarde ballen")
        HeaderLayout.addWidget(self.StatSelect)
        StatsLayout.addLayout(HeaderLayout)
        self.StatsPlot = pg.PlotWidget()  
        self.StatSelect.currentIndexChanged.connect(self.PlotStats)
                    
        self.PlotStats()       
        
        StatsLayout.addWidget(self.StatsPlot) 
        OKButton = QPushButton("OK")
        OKButton.clicked.connect(lambda: self.CloseWidget(self.Statspanel))
        StatsLayout.addWidget(OKButton)
        self.Statspanel.show()
        
    def PlotStats(self):
        colors = ['#D36E70',
                  '#332288',
                  '#88CCEE',
                  '#44AA99',
                  '#117733',
                  '#999933',
                  '#DDCC77',
                  '#CC6677',
                  '#882255',
                  '#AA4499',
                  '#3366FF'] 
        self.StatsPlot.clear()
        date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        def format_tick_string(ticks, scale, spacing):
            return [datetime.datetime.fromtimestamp(t).strftime('%d-%m-%y') for t in ticks]
        date_axis.tickStrings = format_tick_string
        self.StatsPlot.setAxisItems({'bottom': date_axis})
        self.StatsPlot.addLegend()       
        for I, Locatie in enumerate(self.DB.Ballenbestand["Telling"].keys()):
            LocatieNaam = self.DB.Ballenbestand["LocatieDict"][Locatie]
            Dates = []
            NBalls = [] 
            for Telling in self.DB.Ballenbestand["Telling"][Locatie].values():
                Dates.append(datetime.datetime.strptime(Telling["Datum"], "%Y-%m-%d"))
                if self.StatSelect.currentText() == "Aantal ballen":
                    NBalls.append(len(Telling["Ballen"]))
                else:
                    NBalls.append(self.DB.getValueTelling(Telling, int(Telling["Datum"][:4])))
            timestamps = [pg.QtCore.QDateTime(d).toSecsSinceEpoch() for d in Dates]
            self.StatsPlot.plot(timestamps, NBalls, name=LocatieNaam, pen=pg.mkPen(colors[I%len(colors)], width=3))
        self.StatsPlot.getAxis('bottom').setLabel('Date')
        if self.StatSelect.currentText() == "Aantal ballen":  
            self.StatsPlot.getAxis('left').setLabel('Aantal ballen')
        else:
            self.StatsPlot.getAxis('left').setLabel('Waarde ballen', unit="Euro's")
        
        
                
                    
    def BeheerBallenbestand(self):
        self.BeheerPopup = QWidget()
        self.BeheerPopup.setWindowModality(Qt.ApplicationModal)
        Beheerlayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.BeheerPopup)
        BeheerOnderdelenLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        
        LocatieLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        LocatieLayout.addWidget(QLabel("Locaties:"))
        self.BeheerDB_LocatieList = QListWidget()
        self.UpdateLocatieList()
        
        LocatieLayout.addWidget(self.BeheerDB_LocatieList)      
        EditLocatie = QPushButton("Hernoem")
        DeleteLocatie = QPushButton("Verwijder")
        AddLocatie = QPushButton("Toevoegen")
        EditLocatie.clicked.connect(lambda: self.EditLocatie(False))
        DeleteLocatie.clicked.connect(self.DeleteLocatie)
        AddLocatie.clicked.connect(lambda: self.EditLocatie(True))
        
        
        LocatieLayout.addWidget(EditLocatie)
        LocatieLayout.addWidget(DeleteLocatie)
        LocatieLayout.addWidget(AddLocatie)
        
        BalTypeLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        BalTypeLayout.addWidget(QLabel("Balsoorten:"))
        self.BeheerDB_TypeList = QListWidget()
        self.UpdateSoortList()

        BalTypeLayout.addWidget(self.BeheerDB_TypeList)      
        EditSoort = QPushButton("Aanpassen")
        DeleteSoort = QPushButton("Verwijder")
        AddSoort = QPushButton("Toevoegen")
        EditSoort.clicked.connect(lambda: self.EditSoort(False))
        DeleteSoort.clicked.connect(self.DeleteSoort)
        AddSoort.clicked.connect(lambda: self.EditSoort(True))
        BalTypeLayout.addWidget(EditSoort)
        BalTypeLayout.addWidget(DeleteSoort)
        BalTypeLayout.addWidget(AddSoort)
        
        TellingLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        TellingLayout.addWidget(QLabel("Tellingen: "))
        self.BeheerDB_LocatieDropdown = QComboBox()
        self.BeheerDB_LocatieDropMap = []
        TellingLayout.addWidget(self.BeheerDB_LocatieDropdown)
        
        self.BeheerDB_TellingList = QListWidget()
        self.TellingUpdating = False
        self.UpdateTellingList()
        self.BeheerDB_LocatieDropdown.currentIndexChanged.connect(self.UpdateTellingList)        
        TellingLayout.addWidget(self.BeheerDB_TellingList)
        EditTelling = QPushButton("Aanpassen")
        EditTelling.clicked.connect(self.EditTelling)
        DeleteTelling = QPushButton("Verwijder")
        DeleteTelling.clicked.connect(self.DeleteTelling)
        ImportTelling = QPushButton("Importeren")
        ImportTelling.clicked.connect(self.ImportTelling)
        TellingLayout.addWidget(EditTelling)
        TellingLayout.addWidget(DeleteTelling)
        TellingLayout.addWidget(ImportTelling)           
        
        
        BalVoorraadLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        BalVoorraadLayout.addWidget(QLabel("Ballen: "))
        self.BeheerDB_BalVoorraad = QListWidget()
        self.UpdateBalVoorraadList()
        BalVoorraadLayout.addWidget(self.BeheerDB_BalVoorraad)
        EditBal = QPushButton("Aanpassen")
        EditBal.clicked.connect(self.EditBal)
        DeleteBal = QPushButton("Verwijder ongetelde ballen")
        DeleteBal.clicked.connect(self.PurgeBalls)
        
        BalVoorraadLayout.addWidget(EditBal)
        BalVoorraadLayout.addWidget(DeleteBal)
        
        BeheerOnderdelenLayout.addLayout(LocatieLayout)
        BeheerOnderdelenLayout.addLayout(BalTypeLayout)
        BeheerOnderdelenLayout.addLayout(TellingLayout)
        BeheerOnderdelenLayout.addLayout(BalVoorraadLayout)
        Beheerlayout.addLayout(BeheerOnderdelenLayout)
        Beheerlayout.addWidget(QHLine())
        SaveButton = QPushButton("Opslaan")
        SaveButton.clicked.connect(self.SaveBallenbestand)
        CancelButton = QPushButton("Annuleren")
        CancelButton.clicked.connect(self.CancelBeheer)
        
        
        LowerButtons = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        LowerButtons.addWidget(SaveButton)
        LowerButtons.addWidget(CancelButton)
        Beheerlayout.addLayout(LowerButtons)
        self.BeheerPopup.show()    
        
    def EditLocatie(self, AddMode):
        self.EditLocatieWindow = QWidget()
        self.EditLocatieWindow.setWindowModality(Qt.ApplicationModal)
        
        Layout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.EditLocatieWindow)
        self.LocatieNameInput = QLineEdit()
        if AddMode:
            Layout.addWidget(QLabel("Voeg locatie toe:"))
            Index = str(min(set(range(1, max(self.BeheerDB_LocatieMap) + 2)) - set(self.BeheerDB_LocatieMap)))            
        else:
            Layout.addWidget(QLabel("Pas Locatie aan"))        
            self.LocatieNameInput.setText(self.BeheerDB_LocatieList.currentItem().text())
            Index = str(self.BeheerDB_LocatieMap[self.BeheerDB_LocatieList.currentIndex().row()])           
        Layout.addWidget(self.LocatieNameInput)
        ButtonLayout = QBoxLayout(QBoxLayout.LeftToRight)
        AcceptButton = QPushButton("OK")
        AcceptButton.clicked.connect(lambda: self.SaveLocatie(Index, self.EditLocatieWindow))
        CancelButton = QPushButton("Annuleer")
        CancelButton.clicked.connect(lambda: self.CloseWidget(self.EditLocatieWindow))
        ButtonLayout.addWidget(AcceptButton)
        ButtonLayout.addWidget(CancelButton)
        Layout.addLayout(ButtonLayout)
        self.EditLocatieWindow.show()
        
    def SaveLocatie(self, Index, Widget):
        self.DB.Ballenbestand["LocatieDict"][Index] = self.LocatieNameInput.text()
        Widget.close()
        self.UpdateLocatieList()
        
    def DeleteLocatie(self):
        Index = self.BeheerDB_LocatieMap[self.BeheerDB_LocatieList.currentIndex().row()]
        if str(Index) in self.DB.Ballenbestand["Telling"].keys():
            self.WarningPopup = QWidget()
            self.WarningPopup.setWindowModality(Qt.ApplicationModal)
            WarningLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.WarningPopup)
            WarningLayout.addWidget(QLabel("Er zijn nog tellingen met deze locatie, verwijder deze eerst"))
            CloseButton = QPushButton("OK")
            CloseButton.clicked.connect(lambda: self.CloseWidget(self.WarningPopup))
            WarningLayout.addWidget(CloseButton)
            self.WarningPopup.show()
        else:                                  
            if self.GeenBallenMetLocatie(Index):
                del self.DB.Ballenbestand["LocatieDict"][str(Index)]
                self.UpdateLocatieList()                 
            else:
                self.NieuwLocatiePopup = QWidget()
                self.NieuwLocatiePopup.setWindowModality(Qt.ApplicationModal)
                NieuwLocatieLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.NieuwLocatiePopup)
                NieuwLocatieLayout.addWidget(QLabel("Er zijn nog ballen met deze locatie, wil je deze locatie aanpassen naar:"))
                self.NieuwLocatieDrop = QComboBox()
                self.NieuwLocatieDropMap = []
                for Locaties in self.DB.Ballenbestand["LocatieDict"].keys():
                    if int(Locaties) != Index:
                        self.NieuwLocatieDrop.addItem(self.DB.Ballenbestand["LocatieDict"][Locaties])
                        self.NieuwLocatieDropMap.append(int(Locaties))
                NieuwLocatieLayout.addWidget(self.NieuwLocatieDrop)
                ButtonLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
                AcceptButton = QPushButton("Verander locatie")
                AcceptButton.clicked.connect(lambda: self.VeranderLocatieEnDelete(Index))                    
                CloseButton = QPushButton("Annuleer")
                CloseButton.clicked.connect(lambda: self.CloseWidget(self.NieuwLocatiePopup))
                ButtonLayout.addWidget(AcceptButton)
                ButtonLayout.addWidget(CloseButton)
                NieuwLocatieLayout.addLayout(ButtonLayout)
                self.NieuwLocatiePopup.show()
                
                            
        
    def GeenBallenMetLocatie(self, Locatie):
        for Bal in self.DB.Ballenbestand["Balvoorraad"].keys():
            if self.DB.Ballenbestand["Balvoorraad"][Bal]["Locatie"] == Locatie:
                return False
        return True
   
    def VeranderLocatieEnDelete(self, Locatie):
        NieuwLocatie = self.NieuwLocatieDropMap[self.NieuwLocatieDrop.currentIndex()]
        for Bal in self.DB.Ballenbestand["Balvoorraad"].keys():
            if self.DB.Ballenbestand["Balvoorraad"][Bal]["Locatie"] == Locatie:
                self.DB.Ballenbestand["Balvoorraad"][Bal]["Locatie"] = NieuwLocatie  
        del self.DB.Ballenbestand["LocatieDict"][str(Locatie)]
        self.UpdateLocatieList()
        self.NieuwLocatiePopup.close()
      
    def EditSoort(self, AddMode):
        self.EditSoortWindow = QWidget()     
        self.EditSoortWindow.setWindowModality(Qt.ApplicationModal)
        Layout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.EditSoortWindow)
        self.SoortNameInput = QLineEdit()
        self.AfschrijvingList = QTableView()
        if AddMode:
            Layout.addWidget(QLabel("Voeg Baltype toe"))
            self.AfschrijvingenModel = AfschrijvingModel([50, 40, 25, 10, 0])
            Index = str(min(set(range(1, max(self.BeheerDB_SoortMap) + 2)) - set(self.BeheerDB_SoortMap)))

        else:
            Index = str(self.BeheerDB_SoortMap[self.BeheerDB_TypeList.currentIndex().row()])
            Layout.addWidget(QLabel("Pas Baltype aan"))
            self.SoortNameInput.setText(self.BeheerDB_TypeList.currentItem().text())
            self.AfschrijvingenModel = AfschrijvingModel(self.DB.Ballenbestand["BalTypeDict"][Index]["Afschrijving"])     
        
        self.AfschrijvingList.setModel(self.AfschrijvingenModel)
        Layout.addWidget(self.SoortNameInput)        
        Layout.addWidget(QLabel("Afschrijving"))
        Layout.addWidget(self.AfschrijvingList)
        AddYear = QPushButton("Voeg rij toe")
        AddYear.clicked.connect(self.AfschrijvingenModel.addRow)
        RemoveYear = QPushButton("Haal rij weg")
        RemoveYear.clicked.connect(lambda: self.AfschrijvingenModel.removeRow(self.AfschrijvingenModel.rowCount()))        
        Layout.addWidget(AddYear)
        Layout.addWidget(RemoveYear)        
        ButtonLayout = QBoxLayout(QBoxLayout.LeftToRight)
        AcceptButton = QPushButton("OK")
        AcceptButton.clicked.connect(lambda: self.SaveSoort(Index, self.EditSoortWindow))
        CancelButton = QPushButton("Annuleer")
        CancelButton.clicked.connect(lambda: self.CloseWidget(self.EditSoortWindow))
        ButtonLayout.addWidget(AcceptButton)
        ButtonLayout.addWidget(CancelButton)
        Layout.addLayout(ButtonLayout)
        self.EditSoortWindow.show()
        
    def SaveSoort(self, Index, Widget):
        Afschrijvingen = [Afschrijving for Afschrijving in self.AfschrijvingenModel.getItems() if Afschrijving != ""]
        Afschrijvingen.append(0) if Afschrijvingen[-1] != 0 else ""
        print(Afschrijvingen)
        self.DB.Ballenbestand["BalTypeDict"][Index] = {
            "Balsoort": self.SoortNameInput.text(),
            "Afschrijving": Afschrijvingen}
        Widget.close()
        self.UpdateSoortList()
        
    def DeleteSoort(self):
        Index = self.BeheerDB_SoortMap[self.BeheerDB_TypeList.currentIndex().row()]
        if self.GeenBallenMetType(Index):
            del self.DB.Ballenbestand["BalTypeDict"][str(Index)]
            self.UpdateSoortList()   
        else:
            self.NieuwSoortPopup = QWidget()
            self.NieuwSoortPopup.setWindowModality(Qt.ApplicationModal)
            NieuwSoortLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.NieuwSoortPopup)
            NieuwSoortLayout.addWidget(QLabel("Er zijn nog ballen van deze soort, wil je de soort aanpassen naar:"))
            self.NieuwSoortDrop = QComboBox()
            self.NieuwSoortDropMap = []
            for Soort in self.DB.Ballenbestand["BalTypeDict"].keys():
                if int(Soort) != Index:
                    self.NieuwSoortDrop.addItem(self.DB.Ballenbestand["BalTypeDict"][Soort]["Balsoort"])
                    self.NieuwSoortDropMap.append(int(Soort))
            NieuwSoortLayout.addWidget(self.NieuwSoortDrop)
            ButtonLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            AcceptButton = QPushButton("Verander locatie")
            AcceptButton.clicked.connect(lambda: self.VeranderSoortEnDelete(Index))                    
            CloseButton = QPushButton("Annuleer")
            CloseButton.clicked.connect(lambda: self.CloseWidget(self.NieuwSoortPopup))
            ButtonLayout.addWidget(AcceptButton)
            ButtonLayout.addWidget(CloseButton)
            NieuwSoortLayout.addLayout(ButtonLayout)
            self.NieuwSoortPopup.show()
        
    def GeenBallenMetType(self, Soort):
        for Bal in self.DB.Ballenbestand["Balvoorraad"].keys():
            if self.DB.Ballenbestand["Balvoorraad"][Bal]["Soort"] == Soort:
                return False
        return True
    
    def VeranderSoortEnDelete(self, Soort):
        NieuwSoort = self.NieuwSoortDropMap[self.NieuwSoortDrop.currentIndex()]
        for Bal in self.DB.Ballenbestand["Balvoorraad"].keys():
            if self.DB.Ballenbestand["Balvoorraad"][Bal]["Soort"] == Soort:
                self.DB.Ballenbestand["Balvoorraad"][Bal]["Soort"] = NieuwSoort
        del self.DB.Ballenbestand["BalTypeDict"][str(Soort)]
        self.UpdateSoortList()
        self.NieuwSoortPopup.close()
                
    
    def EditTelling(self):
        if self.BeheerDB_TellingList.currentItem():
            SelectedLoc = self.BeheerDB_LocatieDropMap[self.BeheerDB_LocatieDropdown.currentIndex()]
            SelectedKey = self.BeheerDB_TellingList.currentItem().text()
            self.EditTellingPopup = QWidget()
            self.EditTellingPopup.setWindowModality(Qt.ApplicationModal)
            TellingPopupLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.EditTellingPopup)
            TellingPopupLayout.addWidget(QLabel("Ballen in telling:"))
            self.TellingBallenList = QListWidget()
            for Bal in self.DB.Ballenbestand["Telling"][str(SelectedLoc)][SelectedKey]["Ballen"]:
                self.TellingBallenList.addItem(Bal)        
            DeleteButton = QPushButton("Verwijder bal")
            DeleteButton.clicked.connect(lambda: self.TellingBallenList.takeItem(self.TellingBallenList.currentRow()))
            AddButton = QPushButton("Voeg bal toe")
            AddButton.clicked.connect(lambda: self.AddBalToTelling(str(SelectedLoc)))
            
            TellingPopupLayout.addWidget(self.TellingBallenList)
            TellingPopupLayout.addWidget(AddButton)
            TellingPopupLayout.addWidget(DeleteButton)
            
            ButtonLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
            AcceptButton = QPushButton("Opslaan")
            AcceptButton.clicked.connect(lambda: self.SaveTelling(SelectedLoc, SelectedKey))                    
            CloseButton = QPushButton("Annuleer")
            CloseButton.clicked.connect(lambda: self.CloseWidget(self.EditTellingPopup))
            ButtonLayout.addWidget(AcceptButton)
            ButtonLayout.addWidget(CloseButton)
            TellingPopupLayout.addLayout(ButtonLayout)
            self.EditTellingPopup.show()
            
    def AddBalToTelling(self, Locatie):
        self.AddBalPopup = QWidget()
        self.AddBalPopup.setWindowModality(Qt.ApplicationModal)
        AddBalLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.AddBalPopup)
        AddBalLayout.addWidget(QLabel("Voeg bal toe aan telling: "))
        self.BalDropdown = QComboBox()        
        for Bal in self.DB.Ballenbestand["Balvoorraad"].keys():
            if self.DB.Ballenbestand["Balvoorraad"][Bal]["Locatie"] == int(Locatie):
                self.BalDropdown.addItem(Bal)    
        AddBalLayout.addWidget(self.BalDropdown)
        ButtonLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        AcceptButton = QPushButton("Opslaan")
        AcceptButton.clicked.connect(lambda: self.TellingBallenList.addItem(self.BalDropdown.currentText()))  
        AcceptButton.clicked.connect(lambda: self.CloseWidget(self.AddBalPopup))                    
        CloseButton = QPushButton("Annuleer")
        CloseButton.clicked.connect(lambda: self.CloseWidget(self.AddBalPopup))
        ButtonLayout.addWidget(AcceptButton)
        ButtonLayout.addWidget(CloseButton)
        AddBalLayout.addLayout(ButtonLayout)
        self.AddBalPopup.show()
        
    def SaveTelling(self, SelectedLoc, SelectedKey):
        TellingBallenlist = []
        for Index in range(self.TellingBallenList.count()):
            TellingBallenlist.append(self.TellingBallenList.item(Index).text())
        self.DB.Ballenbestand["Telling"][str(SelectedLoc)][SelectedKey]["Ballen"] = TellingBallenlist
        self.EditTellingPopup.close()
        
    
    def ImportTelling(self):
        LoadDialog = QFileDialog.getOpenFileName(self, "Open Ballenbestand", filter="Json files (*.json)")
        self.ImportDB = BallenBestand(LoadDialog[0])
        self.ImportSelector = QWidget()
        self.ImportSelector.setWindowModality(Qt.ApplicationModal)
        ImportSelectorLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.ImportSelector)
        ImportSelectorLayout.addWidget(QLabel("Selecteer telling om te importeren"))
        self.ImportDB_LocatieDropdown = QComboBox()        
        self.ImportDB_LocatieDropMap = []
        for Locs in self.ImportDB.Ballenbestand["Telling"].keys():
            self.ImportDB_LocatieDropdown.addItem(self.ImportDB.Ballenbestand["LocatieDict"][str(Locs)])
            self.ImportDB_LocatieDropMap.append(Locs)     
        self.ImportDB_TellingList = QListWidget()
        self.UpdateImportTellingSelect()
        self.ImportDB_LocatieDropdown.currentIndexChanged.connect(self.UpdateImportTellingSelect)
        ImportSelectorLayout.addWidget(self.ImportDB_LocatieDropdown)
        ImportSelectorLayout.addWidget(self.ImportDB_TellingList)
        ButtonLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        AcceptButton = QPushButton("Importeer")
        AcceptButton.clicked.connect(self.ProcessImport)  
        CloseButton = QPushButton("Annuleer")
        CloseButton.clicked.connect(lambda: self.CloseWidget(self.ImportSelector))
        ButtonLayout.addWidget(AcceptButton)
        ButtonLayout.addWidget(CloseButton)
        ImportSelectorLayout.addLayout(ButtonLayout)
        self.ImportSelector.show()
        
            
            
            
    def UpdateImportTellingSelect(self):
        self.ImportDB_TellingList.clear()
        SelectedLoc = self.ImportDB_LocatieDropMap[self.ImportDB_LocatieDropdown.currentIndex()]
        for Telling in self.ImportDB.Ballenbestand["Telling"][str(SelectedLoc)].keys():
            self.ImportDB_TellingList.addItem(Telling)
        
        
    def ProcessImport(self):
        SelectedLoc = self.ImportDB_LocatieDropMap[self.ImportDB_LocatieDropdown.currentIndex()]
        SelectedKey = self.ImportDB_TellingList.currentItem().text()
        if self.ImportDB.Ballenbestand["LocatieDict"][str(SelectedLoc)] in self.DB.Ballenbestand["LocatieDict"].values():
            LocName = self.ImportDB.Ballenbestand["LocatieDict"][str(SelectedLoc)]
            LocIdx = str(list(self.DB.Ballenbestand["LocatieDict"].keys())[list(self.DB.Ballenbestand["LocatieDict"].values()).index(LocName)])
        else:
            LocName = self.ImportDB.Ballenbestand["LocatieDict"][str(SelectedLoc)]
            LocIdx = str(min(set(range(1, max(self.BeheerDB_LocatieMap) + 2)) - set(self.BeheerDB_LocatieMap)))
            self.DB.Ballenbestand["LocatieDict"][LocIdx] = LocName
            self.DB.Ballenbestand["Telling"][LocIdx] = {}
        ImportTelling = self.ImportDB.Ballenbestand["Telling"][str(SelectedLoc)][SelectedKey]
        ImportTelling["Locatie"] = int(LocIdx)
        if SelectedKey in self.DB.Ballenbestand["Telling"][LocIdx].keys():
            self.ImportPopup = QWidget()
            self.ImportPopup.setWindowModality(Qt.ApplicationModal)
            Layout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.ImportPopup)
            Layout.addWidget(QLabel("Telling al ballenbestand"))
            OKButton = QPushButton("OK")
            OKButton.clicked.connect(lambda: self.CloseWidget(self.ImportPopup))
            OKButton.clicked.connect(lambda: self.CloseWidget(self.ImportSelector))
            Layout.addWidget(OKButton)
            self.ImportPopup.show()
        else:
            self.DB.Ballenbestand["Telling"][LocIdx][SelectedKey] = ImportTelling
            for Bal in ImportTelling["Ballen"]:
                if Bal not in self.DB.Ballenbestand["Balvoorraad"].keys():
                    ImportBal = self.ImportDB.Ballenbestand["Balvoorraad"][Bal]
                    ImportBal["Locatie"] = int(LocIdx)
                    ImportBalSoort = self.ImportDB.Ballenbestand["BalTypeDict"][str(ImportBal["Soort"])]
                    MatchingSoort = [key for key, item in self.DB.Ballenbestand["BalTypeDict"].items() if item["Balsoort"] == ImportBalSoort["Balsoort"]]
                    if MatchingSoort:
                        SoortIdx = MatchingSoort[0]
                    else:
                        SoortIdx = str(min(set(range(1, max(self.BeheerDB_SoortMap) + 2)) - set(self.BeheerDB_SoortMap)))
                        self.DB.Ballenbestand["BalTypeDict"][SoortIdx] = ImportBalSoort
                    ImportBal["Soort"] = int(SoortIdx)
                    self.DB.Ballenbestand["Balvoorraad"][Bal] = ImportBal
                    
            self.UpdateLocatieList()
            self.UpdateSoortList()
            self.UpdateTellingList()
            self.UpdateBalVoorraadList()
            self.ImportSelector.close()
                                          
    
    def DeleteTelling(self):
        SelectedLoc = self.BeheerDB_LocatieDropMap[self.BeheerDB_LocatieDropdown.currentIndex()]
        SelectedKey = self.BeheerDB_TellingList.currentItem().text()
        del self.DB.Ballenbestand["Telling"][str(SelectedLoc)][SelectedKey]
        if len(self.DB.Ballenbestand["Telling"][str(SelectedLoc)]) == 0:
            del self.DB.Ballenbestand["Telling"][str(SelectedLoc)]
        self.UpdateTellingList()
        
    def EditBal(self):
        Index = self.BeheerDB_BalMap[self.BeheerDB_BalVoorraad.currentIndex().row()]
        Bal = self.DB.Ballenbestand["Balvoorraad"][Index]
        self.EditBalPopup = QWidget()
        self.EditBalPopup.setWindowModality(Qt.ApplicationModal)
        EditBalLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.EditBalPopup)
        EditBalLayout.addWidget(QLabel(f"Pas bal {Index} aan"))  
        
        SoortBalLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        SoortBalLayout.addWidget(QLabel("Soort: "))
        self.SoortBalDropdown = QComboBox()
        self.SoortBalMap = []
        for Soort in self.DB.Ballenbestand["BalTypeDict"].keys():
            self.SoortBalDropdown.addItem(self.DB.Ballenbestand["BalTypeDict"][Soort]["Balsoort"])
            self.SoortBalMap.append(int(Soort))
        SoortBalLayout.addWidget(self.SoortBalDropdown)
        self.SoortBalDropdown.setCurrentText(self.DB.Ballenbestand["BalTypeDict"][str(Bal["Soort"])]["Balsoort"])  
        
        LocatieBalLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        LocatieBalLayout.addWidget(QLabel("Locatie: "))
        self.LocatieBalDropdown = QComboBox()
        self.LocatieBalMap = []
        for Locatie in self.DB.Ballenbestand["LocatieDict"].keys():
            self.LocatieBalDropdown.addItem(self.DB.Ballenbestand["LocatieDict"][Locatie])
            self.LocatieBalMap.append(int(Locatie))
        LocatieBalLayout.addWidget(self.LocatieBalDropdown)
        self.LocatieBalDropdown.setCurrentText(self.DB.Ballenbestand["LocatieDict"][str(Bal["Locatie"])])                

        
        JaarBalLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        JaarBalLayout.addWidget(QLabel("Jaar: "))
        self.JaarBalDropdown = QComboBox()
        self.populateYearComboBox(self.JaarBalDropdown)
        self.JaarBalDropdown.setCurrentText(str(Bal["Jaar"]))
        JaarBalLayout.addWidget(self.JaarBalDropdown)
        
        EditBalLayout.addLayout(SoortBalLayout)
        EditBalLayout.addLayout(LocatieBalLayout)
        EditBalLayout.addLayout(JaarBalLayout)
        
        ButtonLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        AcceptButton = QPushButton("Opslaan")
        AcceptButton.clicked.connect(lambda: self.saveBal(Index))
        CloseButton = QPushButton("Annuleer")
        CloseButton.clicked.connect(lambda: self.CloseWidget(self.EditBalPopup))
        ButtonLayout.addWidget(AcceptButton)
        ButtonLayout.addWidget(CloseButton)
        EditBalLayout.addLayout(ButtonLayout)
        self.EditBalPopup.show()
        
    def saveBal(self, Index):
        self.DB.Ballenbestand["Balvoorraad"][Index] = {
            "Soort": self.SoortBalMap[self.SoortBalDropdown.currentIndex()],
            "Jaar": int(self.JaarBalDropdown.currentText()),
            "Locatie": self.LocatieBalMap[self.LocatieBalDropdown.currentIndex()]}
        self.UpdateBalVoorraadList()
        self.CloseWidget(self.EditBalPopup)
        
    def PurgeBalls(self):
        CountedBalSet = set()
        # Get a set of All Balls that have been counted
        for TelLocatie in self.DB.Ballenbestand["Telling"].keys():
            for Telling in self.DB.Ballenbestand["Telling"][TelLocatie].keys():
                for Bal in self.DB.Ballenbestand["Telling"][TelLocatie][Telling]["Ballen"]:
                    CountedBalSet.add(Bal)
        
        #Delete Balls that are not in the set
        Purgelist = []
        for Bal in self.DB.Ballenbestand["Balvoorraad"]:
            if Bal not in CountedBalSet:
                Purgelist.append(Bal)
                
        for Bal in Purgelist:
            del self.DB.Ballenbestand["Balvoorraad"][Bal]
        self.UpdateBalVoorraadList()
        
    
    def UpdateLocatieList(self):
        self.BeheerDB_LocatieList.clear()
        self.BeheerDB_LocatieMap = []
        for Locaties in sorted(self.DB.Ballenbestand["LocatieDict"].keys(), key=lambda k: self.DB.Ballenbestand["LocatieDict"][k]):
            self.BeheerDB_LocatieList.addItem(self.DB.Ballenbestand["LocatieDict"][Locaties])
            self.BeheerDB_LocatieMap.append(int(Locaties))
    
    def UpdateSoortList(self):
        self.BeheerDB_TypeList.clear()
        self.BeheerDB_SoortMap = []
        for Soorten in sorted(self.DB.Ballenbestand["BalTypeDict"].keys(), key=lambda k: self.DB.Ballenbestand["BalTypeDict"][k]["Balsoort"]):
            self.BeheerDB_TypeList.addItem(self.DB.Ballenbestand["BalTypeDict"][Soorten]["Balsoort"])
            self.BeheerDB_SoortMap.append(int(Soorten))
            
    def UpdateTellingList(self):
        if not self.TellingUpdating:
            self.TellingUpdating = True
            if len(self.DB.Ballenbestand["Telling"].keys()) != len(self.BeheerDB_LocatieDropMap):
                self.BeheerDB_LocatieDropdown.clear()
                self.BeheerDB_LocatieDropMap = []
                for Locs in sorted(self.DB.Ballenbestand["Telling"].keys(), key= lambda k: self.DB.Ballenbestand["LocatieDict"][k]):
                    self.BeheerDB_LocatieDropdown.addItem(self.DB.Ballenbestand["LocatieDict"][str(Locs)])
                    self.BeheerDB_LocatieDropMap.append(Locs)                
            self.BeheerDB_TellingList.clear()
            SelectedLoc = self.BeheerDB_LocatieDropMap[self.BeheerDB_LocatieDropdown.currentIndex()]
            for Telling in self.DB.Ballenbestand["Telling"][str(SelectedLoc)].keys():
                self.BeheerDB_TellingList.addItem(Telling)
            self.TellingUpdating = False
            
            
    def UpdateBalVoorraadList(self):
        self.BeheerDB_BalVoorraad.clear()
        self.BeheerDB_BalMap = []
        for Ballen in sorted(self.DB.Ballenbestand["Balvoorraad"].keys()):
            Balwaarde = self.DB.getValueBall(Ballen,  int(datetime.datetime.now().strftime("%Y")))
            spacing = " "*(15 - len(Ballen))
            self.BeheerDB_BalVoorraad.addItem(f"{Ballen} {spacing} met waarde: \u20ac {Balwaarde}")
            self.BeheerDB_BalMap.append(Ballen)
    
    def CloseWidget(self, Widget):
        Widget.close()
        

    def SaveBallenbestand(self):
        self.DB.save("ballenbestand.json")
        self.UpdateBalStats()
        self.BeheerPopup.close()
        
        
    def CancelBeheer(self):
        self.DB = BallenBestand()
        self.UpdateBalStats()
        self.BeheerPopup.close()
        
            
        

        
        
    def startCount(self):
        self.CountPopup = QWidget()
        self.CountPopup.setWindowModality(Qt.ApplicationModal)
        PopupLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.CountPopup) 
        self.LocatieList = QListWidget()
        for locaties in self.DB.Ballenbestand["LocatieDict"].values():
            self.LocatieList.addItem(locaties)
        PopupLayout.addWidget(self.LocatieList)
        self.CountPopup.show()
        ButtonLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight) 
        nextButton = QPushButton("Volgende")
        nextButton.clicked.connect(self.openCountWidget)
        cancelButton = QPushButton("Annuleer")
        cancelButton.clicked.connect(self.closeCountPopup)
        ButtonLayout.addWidget(nextButton)
        ButtonLayout.addWidget(cancelButton)
        
        PopupLayout.addLayout(ButtonLayout)
        #CountWidget(self, "0")
        
    def closeCountPopup(self):
        self.CountPopup.close()
        
    def openCountWidget(self):
        self.CountPopup.close()
        self.Count = CountWidget(self, self.LocatieList.currentIndex().row())
        self.Count.setWindowModality(Qt.ApplicationModal)
        self.Count.show()
        
        
        


class CountWidget(QWidget):
    def __init__(self, parent=Main, Locatie=0):
        super().__init__()
        self.DagTelling = datetime.datetime.now().strftime("%Y-%m-%d")
        self.Jaar = datetime.datetime.now().strftime("%Y")
        self.parent = parent
        self.Locatie = Locatie
        self.layout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self)  
        self.CountWidgetLabel = QLabel("Druk op enter om bal te tellen")
        self.layout.addWidget(self.CountWidgetLabel)
        self.BallenInTelling = set()
        
        self.line_edit = QLineEdit(self)        
        completer = QCompleter(parent.DB.Ballenbestand["Balvoorraad"].keys(), self)
        self.line_edit.setCompleter(completer)
        self.line_edit.returnPressed.connect(self.EnteredValueParser)  
        
        ButtonLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight) 
        nextButton = QPushButton("Klaar met tellen")
        nextButton.clicked.connect(self.saveCount)
        cancelButton = QPushButton("Annuleer")
        cancelButton.clicked.connect(self.closeCount)
        ButtonLayout.addWidget(nextButton)
        ButtonLayout.addWidget(cancelButton)
        
        # Add the line edit to the layout
        self.layout.addWidget(self.line_edit)
        self.layout.addLayout(ButtonLayout)
        
    def EnteredValueParser(self):
        BalID = self.line_edit.text()
        if BalID not in self.parent.DB.Ballenbestand["Balvoorraad"].keys():
            self.addBal()
            self.line_edit.clear()
        else:
            if  self.parent.DB.Ballenbestand["Balvoorraad"][BalID]["Locatie"] != self.Locatie:
                self.IncompLocatieMsg(BalID)
                self.line_edit.clear()
            else:
                if BalID in self.BallenInTelling:
                    self.CountWidgetLabel.setText(f"Bal {BalID} is al geteld")
                    self.line_edit.clear()
                else:                   
                    self.BallenInTelling.add(BalID)
                    self.CountWidgetLabel.setText(f"Bal {BalID} is geteld")
                    self.line_edit.clear()
            
    def IncompLocatieMsg(self, BalID):
        msgBox = QMessageBox()
        changeButton = msgBox.addButton("Verander Locatie", QMessageBox.AcceptRole)
        cancelButton = msgBox.addButton("Tel bal niet", QMessageBox.RejectRole)
        dbLoc = self.parent.DB.Ballenbestand["LocatieDict"][str(self.parent.DB.Ballenbestand['Balvoorraad'][BalID]['Locatie'])]
        Loc = self.parent.DB.Ballenbestand["LocatieDict"][str(self.Locatie)]
        msgBox.setText("Ballocatie incorrect")
        msgBox.setInformativeText(f"Bal locatie is volgens database {dbLoc} en niet {Loc}")
        msgBox.exec()
        if msgBox.clickedButton() == changeButton:
            self.parent.DB.Ballenbestand["Balvoorraad"][BalID]["Locatie"] = self.Locatie
            self.BallenInTelling.append(BalID)
            self.CountWidgetLabel.setText(f"Bal {BalID} is geteld")
            msgBox.close()
            
    def addBal(self):
        self.addBalWidget = QWidget()
        self.addBalWidget.setWindowModality(Qt.ApplicationModal)
        addBalLayout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.addBalWidget)
        addBalLayout.addWidget(QLabel("Bal bestaat nog niet toevoegen?"))
        BalIDLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        BalIDLabel = QLabel("Balnummer: ")
        self.BalIDInput = QLineEdit(self.line_edit.text())
        BalIDLayout.addWidget(BalIDLabel)
        BalIDLayout.addWidget(self.BalIDInput)
        addBalLayout.addLayout(BalIDLayout)
        
        BalSoortLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        BalsoortLabel = QLabel("Baltype: ")
        self.BalSoortInput = QComboBox()
        for types in self.parent.DB.Ballenbestand["BalTypeDict"].values():
            self.BalSoortInput.addItem(types["Balsoort"])
        BalSoortLayout.addWidget(BalsoortLabel)
        BalSoortLayout.addWidget(self.BalSoortInput)
        addBalLayout.addLayout(BalSoortLayout)
        ButtonLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        nextButton = QPushButton("Opslaan")
        nextButton.clicked.connect(self.saveBall)
        cancelButton = QPushButton("Annuleer")
        cancelButton.clicked.connect(self.closeAddBal)
        ButtonLayout.addWidget(nextButton)
        ButtonLayout.addWidget(cancelButton)
        addBalLayout.addLayout(ButtonLayout)
        self.addBalWidget.show()

        
        
        
    def closeAddBal(self):
        self.addBalWidget.close()
        
    def saveBall(self):
        ID = self.BalIDInput.text()
        Soort = self.BalSoortInput.currentIndex()
        self.parent.DB.Ballenbestand["Balvoorraad"][ID] = {
            "Soort": Soort,
            "Jaar": self.Jaar,
            "Locatie": self.Locatie}
        self.BallenInTelling.add(ID)
        self.CountWidgetLabel.setText(f"Bal {ID} is geteld")
        self.addBalWidget.close()
        
        
    def closeCount(self):
        self.close()
        
    def saveCount(self):
        if str(self.Locatie) not in self.parent.DB.Ballenbestand["Telling"].keys():
            self.parent.DB.Ballenbestand["Telling"][str(self.Locatie)] = {}
        self.parent.DB.Ballenbestand["Telling"][str(self.Locatie)][self.DagTelling] = {
            "Datum": self.DagTelling,
            "Locatie": self.Locatie,
            "Ballen": list(self.BallenInTelling)}
        self.parent.DB.save("ballenbestand.json")
        self.parent.UpdateBalStats()
        self.parent.TellingSelectorList[self.parent.TellingLocMap[str(self.Locatie)]].setCurrentIndex(self.parent.TellingSelectorList[self.parent.TellingLocMap[str(self.Locatie)]].count()-1)
        self.close()
        
        

class BallenBestand:
    def __init__(self, file="ballenbestand.json"):
        with open(file) as f:
            self.Ballenbestand = json.load(f)
            
    def save(self, Path):
        with open(Path, "w") as f:
            json.dump(self.Ballenbestand, f, indent=4)
            
    def addTelling(self, TelNaam, Telling):
        self.Ballenbestand["Telling"][TelNaam] = Telling
    
    def getValueBall(self, BalID, Jaar):
        Bal = self.Ballenbestand["Balvoorraad"][BalID]
        AfschrijvingBal = self.Ballenbestand["BalTypeDict"][str(Bal["Soort"])]["Afschrijving"]
        Age = Jaar - Bal["Jaar"]
        if Age < 0:
            Age = -1 #Zorgt dat ballen die nog niet bestaan geen waarde hebben
        Value = AfschrijvingBal[Age] if Age < len(AfschrijvingBal) else AfschrijvingBal[-1]
        return Value
    
    def getValueTelling(self, Telling, Jaar):
        TotalValue = 0
        for BalID in Telling["Ballen"]:
            TotalValue = TotalValue + self.getValueBall(BalID, Jaar)
        return TotalValue
            
class AfschrijvingModel(QtGui.QStandardItemModel):
    def __init__(self, List):
        super().__init__(len(List), 1)
        self.List = List
        self.setHorizontalHeaderLabels(["Waarde"])
        for i, key in enumerate(List):
            self.setItem(i, 0, self.createItem(str(key)))
            self.setVerticalHeaderItem(i, self.createItem(str(i)))

    def createItem(self, text):
        item = QtGui.QStandardItem(text)
        item.setEditable(True)
        return item
    
    def addRow(self):
        self.appendRow([self.createItem("")])
        self.setVerticalHeaderItem(self.rowCount()-1, self.createItem(str(self.rowCount()-1)))
    def getItems(self):
        Afschrijflist = []
        for i in range(self.rowCount()):
            if self.item(i, 0).text() != "":
                Afschrijflist.append(float(self.item(i, 0).text()))
        return(Afschrijflist)
     
        

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationDisplayName("Ballenbeheer")
    app.setApplicationName("Ballenbeheer")
    widget = Main()
    widget.show()
    sys.exit(app.exec())