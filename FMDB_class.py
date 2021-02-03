# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 10:11:53 2021

@author: jackr
"""
import os.path as osp


class FMDB(object):
    def __init__(self, folder_path):
        self.folder_path = folder_path
        if self.exists_here():
            self.update()
            
    def exists_here(self):
        if osp.exists(self.folder_path):
            
    def update(self):