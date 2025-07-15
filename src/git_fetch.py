import dev_config as config
import urequests
import json
import os

user = 'prefixFelix'
repo = 'WordClockPy'
ignore_files = ['git_fetch.py', 'config.py', 'boot.py']


def status():
    """Check if local version matches remote VERSION file"""
    try:
        url = f'https://raw.githubusercontent.com/{user}/{repo}/main/VERSION'
        r = urequests.get(url, headers={'User-Agent': 'micropython'})
        remote_version = r.text.strip()
        r.close()

        print(f'[+] Local: {config.version}, Remote: {remote_version}')
        return config.version == remote_version
    except Exception as e:
        print(f'[!] Status check failed: {e}')
        return True


def pull():
    """Delete all files (except ignore) and download src/ folder"""
    try:
        # Get repository tree
        tree_url = f'https://api.github.com/repos/{user}/{repo}/git/trees/main?recursive=1'
        r = urequests.get(tree_url, headers={'User-Agent': 'micropython'})
        tree = json.loads(r.text)
        r.close()

        # Delete local files (except ignore files)
        _delete_local_files('/')

        # Download files from src/ folder
        base_url = f'https://raw.githubusercontent.com/{user}/{repo}/main/'
        for item in tree['tree']:
            if (item['type'] == 'blob' and item['path'].startswith('src/') and not any(ignore in item['path'] for ignore in ignore_files)):
                local_path = item['path'][4:]  # Remove 'src/' prefix
                _download_file(base_url + item['path'], local_path)

        # Update VERSION file and config
        version_url = base_url + 'VERSION'
        r = urequests.get(version_url, headers={'User-Agent': 'micropython'})
        new_version = r.text.strip()
        r.close()

        # Update config.py with new version
        with open('dev_config.py', 'r') as f:
            lines = f.readlines()
        lines[0] = f'version = "{new_version}"\n'
        with open('dev_config.py', 'w') as f:
            f.writelines(lines)

        print(f'[+] Pull completed. Updated to version: {new_version}')

    except Exception as e:
        print(f'[!] Pull failed: {e}')


def _delete_local_files(path):
    """Recursively delete files except ignore files"""
    try:
        for item in os.listdir(path):
            full_path = path + item if path.endswith('/') else path + '/' + item
            if item in ignore_files:
                continue
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


def _download_file(url, local_path):
    """Download file and create directories if needed"""
    try:
        # Create directory if needed
        dirs = local_path.split('/')[:-1]
        current_dir = ''
        for d in dirs:
            current_dir += d + '/'
            try:
                os.mkdir(current_dir.rstrip('/'))
            except:
                pass

        # Download file
        r = urequests.get(url, headers={'User-Agent': 'micropython'})
        with open(local_path, 'w') as f:
            f.write(r.text)
        r.close()
        print(f'[+] Downloaded: {local_path}')

    except Exception as e:
        print(f'[!] Failed to download {local_path}: {e}')


def _is_dir(path):
    """Check if path is directory"""
    try:
        return os.stat(path)[0] & 0x4000 != 0
    except:
        return False