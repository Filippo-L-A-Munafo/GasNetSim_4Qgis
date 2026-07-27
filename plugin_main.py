# -*- coding: utf-8 -*-
import os.path
from PyQt5.QtCore import QSettings, QTranslator, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

class GasNetSim4QgisPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = '&GasNetSim_4Qgis'
        self.dlg = None

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        
        if status_tip is not None:
            action.setStatusTip(status_tip)
            
        if whats_this is not None:
            action.setWhatsThis(whats_this)
            
        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
            
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
            
        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.svg')
        self.add_action(
            icon_path,
            text='GasNetSim 4Qgis',
            callback=self.run,
            status_tip='Apri il Simulatore Idraulico Reti Gas',
            whats_this='GasNetSim 4Qgis — Simulatore idraulico per reti gas in QGIS',
            parent=self.iface.mainWindow()
        )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        if self.dlg is None:
            from .ui.main_dialog import GasNetSimMainDialog
            self.dlg = GasNetSimMainDialog(self.iface, self.plugin_dir)
        
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()
