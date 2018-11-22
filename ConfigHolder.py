import ConfigParser
from framework.Singleton import Singleton

class ConfigHolder():
    __metaclass__ = Singleton

    def __init__(self, configPath):
        self.config = ConfigParser.ConfigParser()
        self.config.read(configPath)