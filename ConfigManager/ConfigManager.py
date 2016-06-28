# -*- coding: utf-8 -*-
import os
import sys
import ConfigParser
import pprint


class ConfigManager:
    def __init__(self):
        self.config_map = {}
        self.config_dir = ""
        self.config_parser = ConfigParser.ConfigParser()
        self.init_config()

    def init_config(self):
        self.config_dir = os.path.join(os.path.dirname(sys.path[0]), 'Config')
        if os.path.isdir(self.config_dir):
            print "{} is a dir".format(self.config_dir)
            for config_file in os.listdir(self.config_dir):
                print config_file
                if config_file == "parameters.ini":
                    #(mapkey, _) = os.path.splitext(conffile)
                    config_file = os.path.join(self.config_dir, config_file)
                    if os.path.isfile(config_file):
                        print "{} is a file".format(config_file)
                        self.config_parser.read(config_file)
                        self.config_map['GLOBAL'] = dict(self.config_parser.items('GLOBAL'))
                        self.config_map['STOCK_LIST'] = dict(self.config_parser.items('STOCK_LIST'))

    def get_api_key(self):
        return self.config_map['GLOBAL']['api_key']

    def get_stock_list(self):
        return self.config_map['STOCK_LIST']['stock_list']

    def get_stock_type(self):
        return self.config_map['STOCK_LIST']['stock_type']

    def get_stock_multi(self):
        return self.config_map['STOCK_LIST']['stock_multi']

    def printf(self):
        pprint.pprint(self.config_map['GLOBAL'])
        pprint.pprint(self.config_map['STOCK_LIST'])

    @classmethod
    def instance(cls):
        # print "call instance"
        if not hasattr(cls, '__instance__'):
            cls.__instance__ = ConfigManager()
        return cls.__instance__

if __name__ == '__main__':
    ConfigManager.instance().printf()
