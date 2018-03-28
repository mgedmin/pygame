""" Uploads wheels to pypi from travisci.

The commit requires an UPLOAD line.
"""
import glob
import os
import subprocess
import sys

def is_master_or_mastertest():
    cmd = ('git rev-parse --abbrev-ref HEAD')
    tag_branch = subprocess.check_output(cmd, shell=True)
    return tag_branch in [b'master\n', b'mastertest\n']


# if --no-git we do not check with git if an upload is needed.
do_git_check = '--no-git' not in sys.argv
if do_git_check:
    commit = subprocess.check_output(['git', 'log', '-1'])
    print(commit)
    if not is_master_or_mastertest() or b'UPLOAD' not in commit:
        print('Not uploading')
        sys.exit(0)

# There should be exactly one .whl
filenames = glob.glob('dist/*.whl')
if os.environ.get('UPLOAD_SDIST', None):
    filenames += glob.glob('dist/*.tar.gz')


print('Calling twine to upload...')
try:
    for filename in filenames:
        cmd = ['twine', 'upload', '--config-file', 'pypirc', filename]
        print(' '.join(cmd))
        subprocess.check_call(cmd)
except:
    print('is twine installed?')
finally:
    os.unlink('pypirc')
