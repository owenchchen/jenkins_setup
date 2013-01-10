#!/usr/bin/env python

import urllib2
import yaml


class Cob_Distro(object):
    def __init__(self, name, repos_dict=None):

        self.repositories = {}

        if not repos_dict:
            self.url = 'https://raw.github.com/fmw-jk/jenkins_setup/master/releases/cob_%s.yaml' % name  # TODO change to ipa320
            self.release_file = urllib2.urlopen(self.url)
            self.repos_dict = yaml.load(self.release_file.read())['repositories']
        else:
            self.repos_dict = repos_dict

        for repo_name, data in self.repos_dict.iteritems():
            repo = Cob_Distro_Repo(repo_name, data)
            self.repositories[repo_name] = repo


class Cob_Distro_Repo(object):
    def __init__(self, name, data):
        self.name = name
        self.type = data['type']
        self.url = data['url']
        self.version = None
        if 'version' in data:
            self.version = data['version']

    def get_rosinstall(self):
        if self.version:
            return yaml.dump([{self.type: {'local-name': self.name,
                                           'uri': '%s' % self.url,
                                           'version': '%s' % self.version}}],
                             default_style=False)
        else:
            return yaml.dump([{self.type: {'local-name': self.name,
                                           'uri': '%s' % self.url}}],
                             default_style=False)