# -*- coding: utf-8 -*-
"""
This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    from .plugin_main import GasNetSim4QgisPlugin
    return GasNetSim4QgisPlugin(iface)
