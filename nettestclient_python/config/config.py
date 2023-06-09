import json
import os
import sys
import threading


class Config:
    def __init__(self):
        # if not hasattr(Config, "_first_init"):
        #     Config._first_init = True
        #     self.settings = dict()
        self.load()

    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(Config, "_instance"):
    #         Config._instance = object.__new__(cls)
    #     return Config._instance

    def load(self, configPath=""):
        if not configPath:
            dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
            Path = "config/appsettings.json"
            configPath = os.path.join(dirname, Path)
        with open(configPath, "r") as f:
            strs = ""
            for str in f.readlines():
                strs += str
            self.settings = json.loads(strs)
        if "Path" in self.settings:
            self.settings['Path'] = self.settings['Path']
        else:
            self.settings['Path'] = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'Data', 'Data')
        if "LogPath" in self.settings:
            self.settings['LogPath'] = self.settings['LogPath']
        else:
            self.settings['LogPath'] = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'Data', 'log')
        if "DescPath" in self.settings:
            self.settings['DescPath'] = self.settings['DescPath']
        else:
            self.settings['DescPath'] = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'temp', 'tmp')
        if not os.path.exists(self.settings['Path']):
            os.makedirs(self.settings['Path'])
        if not os.path.exists(self.settings['LogPath']):
            os.makedirs(self.settings['LogPath'])
        if not os.path.exists(self.settings['DescPath']):
            os.makedirs(self.settings['DescPath'])
