"""
Svelte Studios Django projects deployment scripts.
"""
from fabric.api import *

__author__ = 'Andrey Shipilov <andrey@sveltestudios.com> https://www.andreyshipilov.com/'

env.project_name = 'app'
env.hosts = ['...webfactional.com']
env.user = ''
env.password = ''
env.venv_path = '../venv'


@task
def staging():
    """
    Sets staging environment variables.
    """

    env.type = 'staging'
    env.settings = '{0}.settings.staging'.format(env.project_name)
    env.settings_args = '--settings={0}.settings.{1}'.format(env.project_name, env.type)
    env.root_dir = '/home/.../webapps/{0}_staging/{1}_django'.format(env.project_name, env.project_name)


@task
def prod():
    """
    Sets production environment variables.
    """

    env.type = 'prod'
    env.settings = '{0}.settings.prod'.format(env.project_name)
    env.settings_args = '--settings={0}.settings.{1}'.format(env.project_name, env.type)
    env.root_dir = '/home/.../webapps/{0}_production/{1}_django'.format(env.project_name, env.project_name)


@task
def restart():
    """
    Restarts Apache service.
    """

    with cd(env.root_dir):
        run('../apache2/bin/restart')


@task
def update():
    """
    Updates the code from GIT. Installs all the requirements. Syncs database.
    Migrates schema changes. Collects static files.
    """

    with cd(env.root_dir):
        run('git pull')
        with prefix(". {0}/{1}/bin/activate".format(env.root_dir, env.venv_path)):
            run('pip install -r requirements/{0}.txt'.format(env.type))
            run('python manage.py migrate {0}'.format(env.settings_args))
            run('python manage.py collectstatic --noinput {0}'.format(env.settings_args))


@task
def clear_cache():
    """
    Clears 'sorl.thumbnail' cache and Django cache set by the settings.
    """

    with cd(env.root_dir):
        with prefix(". {0}/{1}/bin/activate".format(env.root_dir, env.venv_path)):
            run('python manage.py thumbnail cleanup {0}'.format(env.settings_args))
            run('python manage.py clear_cache {0}'.format(env.settings_args))


@task
def deploy():
    """
    Deploys the project using selected settings.
    Runs all the needed commands one after another.
    """

    update()
    clear_cache()
    restart()
