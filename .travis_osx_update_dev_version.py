"""For updating the version from git.

setup.py contains a __version__ field.
Update that.


If we are on master, we want to update the version as a pre-release.
git describe --tags



With these:
    setup.py
        __version__= '0.0.2'
    git describe --tags
        0.0.1-22-g729a5ae

We want this:
    setup.py
        __version__= '1.9.4.dev169'

Get the branch/tag name with this.
    git symbolic-ref -q --short HEAD || git describe --tags --exact-match



"""
import io
import os
import re
import subprocess


def migrate_source_attribute(attr, to_this, target_file, regex):
    """Updates __magic__ attributes in the source file"""
    change_this = re.compile(regex, re.S)
    new_file = []
    found = False

    with open(target_file, 'r') as fp:
        lines = fp.readlines()

    for line in lines:
        if line.startswith(attr):
            found = True
            line = re.sub(change_this, to_this, line)
        new_file.append(line)

    if found:
        with open(target_file, 'w') as fp:
            fp.writelines(new_file)

def migrate_version(target_file, new_version):
    """Updates __version__ in the source file"""
    regex = r"['\"](.*)['\"]"
    migrate_source_attribute('__version__', "'%s'" % new_version, target_file, regex)


def is_master_or_mastertest():
    cmd = ('git rev-parse --abbrev-ref HEAD')
    tag_branch = subprocess.check_output(cmd, shell=True)
    return tag_branch in [b'master\n', b'mastertest\n']

def git_tag_name():
    cmd = ('git describe --tags')
    tag_branch = subprocess.check_output(cmd, shell=True)
    tag_branch = tag_branch.decode().strip()
    return tag_branch

def get_git_version_info():
    cmd = 'git describe --tags'
    ver_str = subprocess.check_output(cmd, shell=True)
    ver, commits_since, githash = ver_str.decode().strip().split('-')
    return ver, commits_since, githash

def prerelease_version():
    """ return what the prerelease version should be.
    https://packaging.python.org/tutorials/distributing-packages/#pre-release-versioning

    0.0.2.dev22
    """
    ver, commits_since, githash = get_git_version_info()
    setuppy_ver = get_version()

    parts = setuppy_ver.split('.')
    if 'dev' in parts[-1]:
        # if it is something like 'dev0', just make it 'dev'.
        # We add 'commits_since' to it later anyway.
        parts[-1] = 'dev'
    setuppy_ver = '.'.join(parts)
    assert len(parts) in [3, 4], 'setup.py version should be like 1.9.4 or 1.9.4.dev'
    assert setuppy_ver > ver, 'the setup.py version should be newer than the last tagged release.'
    return '%s%s' % (setuppy_ver, commits_since)

def read(*parts):
    """ Reads in file from *parts.
    """
    try:
        return io.open(os.path.join(*parts), 'r', encoding='utf-8').read()
    except IOError:
        return ''

def get_version():
    """ Returns version from setup.py
    """
    version_file = read('setup.py')
    version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]',
                              version_file, re.MULTILINE)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def release_version_correct():
    """Makes sure the:
    - prerelease verion for master is correct.
    - release version is correct for tags.
    """
    fname = 'setup.py'
    if is_master_or_mastertest():
        # update for a pre release version.
        if os.path.exists(fname):
            target_version = os.path.abspath(fname)
            new_version = prerelease_version()
            print('updating version in %s from %s to %s' % (fname, target_version, new_version))
            migrate_version(target_version, new_version)
    else:
        # check that we are a tag with the same version as in __init__.py
        assert get_version() == git_tag_name(), 'git tag/branch name not the same as pygame/__init__.py __verion__'


if __name__ == '__main__':
    release_version_correct()
