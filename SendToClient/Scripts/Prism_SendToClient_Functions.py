# -*- coding: utf-8 -*-
#
####################################################
#
# PRISM - Pipeline for animation and VFX projects
#
# www.prism-pipeline.com
#
# contact: contact@prism-pipeline.com
#
####################################################
#
#
# Copyright (C) 2016-2021 Richard Frangenberg
#
# Licensed under GNU LGPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.
####################################################
# Plugin author: Elise Vidal
# Contact: evidal@artfx.fr
# Beta Testeur: Simon 'ca marche pas' Tarsiguel

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

import os
import shutil
import datetime
import re
from SetName import SetName
import subprocess


class Prism_SendToClient_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        # Only for Prism Standalone
        if self.core.appPlugin.pluginName == "Standalone":
            self.core.registerCallback(
                "openPBFileContextMenu", self.openPBFileContextMenu, plugin=self.plugin
            )
            self.core.registerCallback(
                "openPBListContextMenu", self.openPBListContextMenu, plugin=self.plugin
            )
            self.core.registerCallback(
                "productSelectorContextMenuRequested", self.productSelectorContextMenuRequested, plugin=self.plugin
            )
            self.core.registerCallback(
                "mediaPlayerContextMenuRequested", self.mediaPlayerContextMenuRequested, plugin=self.plugin
            )

    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True
    
    def openPBFileContextMenu(self, origin, menu, path):
        
        # if click on a scenefile
        if os.path.isfile(path):

            # get file data
            data = self.core.getScenefileData(path, getEntityFromPath=True)

            # create button build layout and add it to the build menu
            self.create_buttons(menu, data)

    def mediaPlayerContextMenuRequested(self, mediaplayer, menu):
        data = mediaplayer.origin.getCurrentVersion()
        self.create_buttons(menu, data)

    def openPBListContextMenu(self, mediabrowser, menu, lw, item, path):
        if lw == mediabrowser.lw_version:
            data = mediabrowser.getCurrentVersion()
            if data:
                self.create_buttons(menu, data)

    def productSelectorContextMenuRequested(self, productbrowser, lw, pos, menu):
        if lw == productbrowser.tw_versions:
            data = productbrowser.getCurrentVersion()
            if data:
                self.create_buttons(menu, data)

    def create_buttons(self, menu, data):

        send_menu = QMenu("Send to client")
        send_act = QAction("Send to client", menu)
        send_act.triggered.connect(lambda : self.copyToClient(data))
        send_menu.addAction(send_act)

        quick_send_act = QAction("Quick Send to client", menu)
        quick_send_act.triggered.connect(lambda : self.quick_copyToClient(data))
        send_menu.addAction(quick_send_act)

        menu.addMenu(send_menu)


    @err_catcher(name=__name__)
    def format_toClient_media_name(self, data):
        try:            
            asset_name = ''
            # for media
            if "identifier" in data.keys():
                return data.get('identifier')

            # for product
            if "product" in data.keys():
                return data.get('product')
            
            # for scene files
            else:
                if data.get('type') == 'shot':
                    asset_name = data.get('shot')
                elif data.get('type') == 'asset':
                    asset_name = data.get('asset_path')

            for k, v in data.items():
                self.core.popup(f"{k} : {v}")
                
            task = data.get('task')
            
            formatted_toClient_media_name = asset_name + '_' + task

            return formatted_toClient_media_name
        except Exception as e:
            self.core.popup(e)

    @err_catcher(name=__name__)
    def open_explorer(self, path):
        path = path.replace('/', '\\')
        cmd = 'explorer ' + path
        subprocess.Popen(cmd)

    @err_catcher(name=__name__)
    def get_toClient_folder(self, data):
        project_path = data['project_path']

        return f"{project_path}/08_ToClient".replace('\\', '/')

    @err_catcher(name=__name__)
    def get_toClient_media_folder(self):
        date = datetime.datetime.now()
        date = date.strftime('%y%m%d')
        toClient_media_folder = date + '_'
        return toClient_media_folder

    @err_catcher(name=__name__)
    def copy_files(self, src, dst):

        src = src.replace('/', '\\')
        dst = dst.replace('/', '\\')

        if not os.path.exists(src):
            raise FileNotFoundError(f"Source file doesn't exists : {src}")
        
        # dst folder creation
        if not os.path.exists(dst):
            os.makedirs(dst)

        # src is a file
        if os.path.isfile(src):
            return shutil.copy2(src, dst)

        # src is a folder
        elif os.path.isdir(src):
            base_name = os.path.basename(os.path.normpath(src))
            target_path = os.path.join(dst, base_name)
            if os.path.abspath(src) == os.path.abspath(target_path):
                raise ValueError("Source and destination must be different. ")

            def ignore_patterns_custom(dir_path, names):
                ignored = []
                for name in names:
                    full_path = os.path.join(dir_path, name)
                    if name == "versioninfo.json":
                        ignored.append(name)
                    elif name == "_thumbs" and os.path.isdir(full_path):
                        ignored.append(name)
                return ignored

            return shutil.copytree(src, target_path, dirs_exist_ok=True, ignore=ignore_patterns_custom)
        else:
            raise ValueError(f"Src must me a folder or a file : {src}")

    @err_catcher(name=__name__)  
    def rename_files(self, src, name):
        if os.path.isfile(src):
            ext = os.path.splitext(src)[1]
            new_name = f"{os.path.dirname(src)}/{name}{ext}"
            
            os.replace(src, new_name)
        elif os.path.isdir(src):
            folders = src.split('\\')[:-1]
            folders.append(name)
            target = '\\'.join(folders)
            if os.path.exists(target):
                self.merge_folders(src, target)
            else:
                os.replace(src, target)

    @err_catcher(name=__name__)
    def get_existing_folders(self, search_dir):
        existing_folders = []
        for dir in os.listdir(search_dir):
            if os.path.isdir(os.path.join(search_dir, dir)):
                existing_folders.append(dir)
        return existing_folders[::-1]
    
    @err_catcher(name=__name__)
    def quick_copyToClient(self, data):
        media_folder = ""
        if "filename" in data.keys():
            media_folder = data.get('filename')
        elif "path" in data.keys():
            media_folder = data.get('path')
        
        placeholder_media_name = self.format_toClient_media_name(data)
        toClient_folder = self.get_toClient_folder(data)
        placeholder_media_folder = self.get_toClient_media_folder()

        # RETRIEVE AND FORMAT USER INPUT
        toClient_media_folder = placeholder_media_name
        toClient_media_folder = re.sub(
            r"[^a-zA-Z0-9]", "_", toClient_media_folder
            )
        toClient_media_path = os.path.join(
            toClient_folder, placeholder_media_folder
            )
        toClient_media_name = placeholder_media_folder
        toClient_media_name = re.sub(r"[^a-zA-Z0-9]", "_", toClient_media_name)

        copied = self.copy_files(media_folder, toClient_media_path)

        self.rename_files(copied, placeholder_media_name)

    @err_catcher(name=__name__)
    def copyToClient(self, data):
        media_folder = ""
        if "filename" in data.keys():
            media_folder = data.get('filename')
        elif "path" in data.keys():
            media_folder = data.get('path')

        placeholder_media_name = self.format_toClient_media_name(data)

        toClient_folder = self.get_toClient_folder(data)

        # GET MEDIA NAME FROM USER INPUT
        dlg = SetName()
        dlg.e_mediaName.setText(placeholder_media_name)
        existing_folders = self.get_existing_folders(toClient_folder)
        placeholder_media_folder = self.get_toClient_media_folder()
        existing_folders.insert(0, placeholder_media_folder)
        dlg.c_mediaFolders.addItems(existing_folders)
        dlg.b_explorer.clicked.connect(
            lambda: self.open_explorer(toClient_folder)
            )
        result = dlg.exec_()
        if result == 0:
            return

        # RETRIEVE AND FORMAT USER INPUT
        toClient_media_folder = dlg.c_mediaFolders.currentText()
        toClient_media_folder = re.sub(
            r"[^a-zA-Z0-9]", "_", toClient_media_folder
            )
        toClient_media_path = os.path.join(
            toClient_folder, toClient_media_folder
            )
        toClient_media_name = dlg.e_mediaName.text()
        toClient_media_name = re.sub(r"[^a-zA-Z0-9]", "_", toClient_media_name)

        copied = self.copy_files(media_folder, toClient_media_path)

        self.rename_files(copied, toClient_media_name)

    def merge_folders(self, src, dst):
        if not os.path.isdir(src):
            raise ValueError(f"{src} n'est pas un dossier valide.")
        if not os.path.isdir(dst):
            os.makedirs(dst)

        for item in os.listdir(src):
            src_path = os.path.join(src, item)
            dst_path = os.path.join(dst, item)

            if os.path.isdir(src_path):
                self.merge_folders(src_path, dst_path)  # Recursion pour les sous-dossiers
            else:
                shutil.copy2(src_path, dst_path)  # Remplace ou copie les fichiers