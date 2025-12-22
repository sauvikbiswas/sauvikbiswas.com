import os
import shutil
from pathlib import Path
import logging
import paramiko
import yaml
from pprint import pprint

filetypes = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.mp4', '.mov', '.avi', '.mkv', '.webm']

# selective_copy copies source directory to destination directory
# but only for files that match the pattern
# the tree of the destination directory should be the same as the tree of the source directory
# If not, it is created as such.
def selective_copy(source_dir, target_dir):
    """Selective copy of files from source directory to target directory."""
    logging.info(f"Copying from {source_dir} to {target_dir}")
    for file in source_dir.iterdir():
        path = Path(file)
        if path.is_dir():
            logging.info(f"Creating directory {target_dir / path.name}")
            (target_dir / path.name).mkdir(parents=True, exist_ok=True)
            selective_copy(path, target_dir / path.name)
            continue;
        if path.suffix not in filetypes:
            logging.info(f"Skipping {path.name} because it is not a valid filetype")
            continue;
        logging.info(f"Copied {path.name} to {target_dir / path.name}")
        shutil.copy(path, target_dir / path.name)

def sftp_copy(config, source_dir):
    """SFTP copy of files from source directory to target directory.""" 
    root = Path(config['sftp']['root'])
    with paramiko.Transport(config['sftp']['host'], config['sftp']['port']) as transport:
        transport.connect(username=config['sftp']['user'], password=config['sftp']['password'])
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            _sftp_copy(sftp, source_dir, Path(config['sftp']['root']))

def _sftp_copy(sftp, source_dir, target_base):
    """Recursively copy source_dir to target_base via SFTP, preserving structure."""
    for item in source_dir.iterdir():
        path = Path(item)
        if path.is_dir():
            remote_dir = target_base / path.name
            try:
                # Create full path recursively
                mkdir_p(sftp, str(remote_dir))
                logging.info(f"Created/verified directory {remote_dir}")
            except Exception as e:
                logging.error(f"Error creating {remote_dir}: {e}")
                continue
            _sftp_copy(sftp, path, remote_dir)
        else:
            if path.suffix not in filetypes:
                logging.info(f"Skipping {path.name}")
                continue
            remote_file = target_base / path.name
            try:
                mkdir_p(sftp, str(remote_file.parent))  # Ensure parent exists
                sftp.put(str(path), str(remote_file))
                logging.info(f"Copied {path.name} to {remote_file}")
            except Exception as e:
                logging.error(f"Error copying {path.name} to {remote_file}: {e}")

def mkdir_p(sftp, remote_path):
    """Create remote directory and all parents."""
    path = Path(remote_path)
    if path == path.parent:
        return  # Root
    try:
        sftp.stat(str(path))
        return  # Exists
    except FileNotFoundError:
        mkdir_p(sftp, str(path.parent))
    try:
        sftp.mkdir(str(path))
    except FileExistsError:
        pass  # Race condition OK


def get_config():
    """Get configuration from config.yaml."""
    with open('scripts/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        return config

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # selective_copy(Path("content/posts"), Path("external/posts"))
    config = get_config()
    pprint(config)
    sftp_copy(config, Path("static"))