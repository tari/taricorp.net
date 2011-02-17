from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['tari@taricorp.net']

def deploy():
    TEMP_ARC = '/tmp/deploy.tar.bz2'
    with cd('deploy'):
        local('tar cjf %s *' %TEMP_ARC, capture=False)
    put(TEMP_ARC, '/tmp/')
    with cd('/srv/http'):
        run('tar xjf ' + TEMP_ARC)
        run('rm ' + TEMP_ARC)
    local('rm ' + TEMP_ARC)
