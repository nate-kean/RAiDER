"""
Script to assist in regenerating each Python version's lockfiles after making
changes to environment.yml.
"""

import re
import subprocess
import tempfile
from pathlib import Path

from tqdm import tqdm


# RAiDER's supported Python versions. The last entry in the list will be placed
# in the project root.
VERSIONS = [
    '3.9',
    '3.10',
    '3.11',
    '3.12',
]

# The dependencies entry for python.
# First group: " - python"
# Second group: ">=3.9" or any version specification
PATTERN_PYTHON_DEP = re.compile(r'^(\s*-\s*python)([<>=~]?=?.+$)', re.MULTILINE)

ENVIROMENT_YML_PATH = Path('environment.yml')


def generate_lock(out_path: Path, version: str, template: str) -> None:
    """
    Use conda-lock to generate a lockfile for this version of the
    environment.yml file, and place it at the specified output path.
    """
    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        env_path = tmp_dir / 'environment.yml'

        # Hardcode a copy of the environment.yml file to this Python version
        with env_path.open('w', encoding='utf-8') as f_env:
            f_env.write(re.sub(PATTERN_PYTHON_DEP, f'\\1=={version}', template))

        # Platforms explicitly listed in order to exclude win-64, since isce3
        # and wand (and therefore RAiDER) are not compatible with Windows.
        cmd = f'conda-lock --file {env_path} --lockfile {out_path} -p linux-64 -p osx-64 -p osx-arm64'
        result = subprocess.run(cmd.split(' '), stdout=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(f'Command exited with non-zero status code {result.returncode}: "{cmd}"')


def main() -> None:
    with ENVIROMENT_YML_PATH.open(encoding='utf-8') as fin:
        yml_content = fin.read()

    for i, version in tqdm(enumerate(VERSIONS), total=len(VERSIONS), unit='lockfiles written'):
        if i < len(VERSIONS) - 1:
            generate_lock(Path(f'.circleci/conda-lock-{version}.yml'), version, yml_content)
        else:
            generate_lock(Path('conda-lock.yml'), version, yml_content)


if __name__ == '__main__':
    main()
