import config
import urequests
import json
import os

user = 'prefixFelix'
repo = 'WordClockPy'
ignore_files = ['git_fetch.py', 'config.py', 'boot.py', 'language.py']


def status():
    """Check if local version matches remote VERSION file"""
    try:
        url = f'https://raw.githubusercontent.com/{user}/{repo}/main/VERSION'
        r = urequests.get(url, headers={'User-Agent': 'micropython'})
        remote_version = r.text.strip()
        r.close()
        print(f'\t[+] Local: {config.version}, Remote: {remote_version}')
        return config.version == remote_version
    except Exception as e:
        print(f'\t[!] Status check failed: {e}')
        return True


def pull():
    """Safely download, then replace files"""
    temp_dir = '/temp_update'
    try:
        # Get repository tree
        tree_url = f'https://api.github.com/repos/{user}/{repo}/git/trees/main?recursive=1'
        r = urequests.get(tree_url, headers={'User-Agent': 'micropython'})
        tree = json.loads(r.text)
        r.close()

        # Create temp directory
        try:
            os.mkdir(temp_dir)
        except:
            pass

        # Download all files to temp first
        base_url = f'https://raw.githubusercontent.com/{user}/{repo}/main/'
        downloads = []

        for item in tree['tree']:
            if (item['type'] == 'blob' and item['path'].startswith('src/') and
                    not any(ignore in item['path'] for ignore in ignore_files)):
                local_path = item['path'][4:]  # Remove 'src/' prefix
                temp_path = temp_dir + '/' + local_path.replace('/', '_')
                print(f'\t[>] Downloading {local_path}...', end='')

                if _download_file(base_url + item['path'], temp_path):
                    downloads.append((temp_path, local_path))
                    print('OK')
                else:
                    raise Exception(f'Failed to download {local_path}')

        # Get new version
        r = urequests.get(base_url + 'VERSION', headers={'User-Agent': 'micropython'})
        new_version = r.text.strip()
        r.close()

        print(f'\t[+] All files downloaded. Replacing...')

        # Now safely replace: delete local files then move from temp
        _delete_local_files('/')

        for temp_path, local_path in downloads:
            _create_dirs(local_path)
            _move_file(temp_path, local_path)

        # Update version in config
        _update_version(new_version)

        # Cleanup temp
        _cleanup_temp(temp_dir)

        print(f'\t[+] Pull completed. Updated to version: {new_version}')

    except Exception as e:
        print(f'\t[!] Pull failed: {e}')
        _cleanup_temp(temp_dir)


def _download_file(url, local_path):
    """Download file, return success"""
    try:
        r = urequests.get(url, headers={'User-Agent': 'micropython'})
        with open(local_path, 'w') as f:
            f.write(r.text)
        r.close()
        return True
    except:
        return False


def _move_file(src, dst):
    """Move file from src to dst"""
    try:
        with open(src, 'r') as f_src, open(dst, 'w') as f_dst:
            f_dst.write(f_src.read())
        os.remove(src)
    except Exception as e:
        print(f'\t[!] Failed to move {src} to {dst}: {e}')


def _create_dirs(file_path):
    """Create directories for file path"""
    dirs = file_path.split('/')[:-1]
    path = ''
    for d in dirs:
        path += d + '/'
        try:
            os.mkdir(path.rstrip('/'))
        except:
            pass


def _update_version(new_version):
    """Update version in config file"""
    try:
        with open('config.py', 'r') as f:
            lines = f.readlines()
        lines[0] = f'version = "{new_version}"\n'
        with open('config.py', 'w') as f:
            for line in lines:
                f.write(line)
    except Exception as e:
        print(f'\t[!] Failed to update version: {e}')


def _delete_local_files(path):
    """Recursively delete files except ignore files"""
    try:
        for item in os.listdir(path):
            if item in ignore_files or item == 'temp_update':
                continue
            full_path = f'{path.rstrip("/")}/{item}'
            try:
                if _is_dir(full_path):
                    _delete_local_files(full_path)
                    os.rmdir(full_path)
                else:
                    os.remove(full_path)
            except:
                pass
    except:
        pass


def _cleanup_temp(temp_dir):
    """Remove temp directory"""
    try:
        for item in os.listdir(temp_dir):
            os.remove(f'{temp_dir}/{item}')
        os.rmdir(temp_dir)
    except:
        pass


def _is_dir(path):
    """Check if path is directory"""
    try:
        return os.stat(path)[0] & 0x4000 != 0
    except:
        return False