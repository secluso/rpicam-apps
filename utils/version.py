#!/usr/bin/python3

# Copyright (C) 2021, Raspberry Pi (Trading) Limited
# Generate version information for rpicam-apps

import subprocess
import sys
import os
from datetime import datetime, timezone
from string import hexdigits

digits = 12


def git_commit_epoch():
    r = subprocess.run(['git', 'show', '--no-patch', '--format=%ct', 'HEAD'],
                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
    if r.returncode:
        return None
    out = r.stdout.strip()
    if not out.isdigit():
        return None
    return int(out)


def build_timestamp(commit_epoch):
    source_date_epoch = os.environ.get('SOURCE_DATE_EPOCH')
    if source_date_epoch:
        try:
            return datetime.fromtimestamp(int(source_date_epoch), tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            print('ERR: Invalid SOURCE_DATE_EPOCH, falling back to commit/build time.', file=sys.stderr)

    if commit_epoch is not None:
        return datetime.fromtimestamp(commit_epoch, tz=timezone.utc)

    return datetime.now(timezone.utc)


def generate_version():
    commit = '0' * digits + '-invalid'
    commit_epoch = None

    try:
        if len(sys.argv) == 2:
            # Check if this is a git directory
            r = subprocess.run(['git', 'rev-parse', '--git-dir'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, universal_newlines=True)
            if r.returncode:
                raise RuntimeError('Invalid git directory!')

            # Get commit id
            r = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
            if r.returncode:
                raise RuntimeError('Invalid git commit!')

            commit = r.stdout.strip('\n')[0:digits]
            commit_epoch = git_commit_epoch()

            # Check dirty status
            r = subprocess.run(['git', 'diff-index', '--quiet', 'HEAD'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, universal_newlines=True)
            if r.returncode:
                commit = commit + '-dirty'

        elif len(sys.argv) == 3:
            commit = sys.argv[2].lower().strip()
            if any(c not in hexdigits for c in commit):
                raise RuntimeError('Invalid git sha!')

            commit = commit[0:digits]

        else:
            raise RuntimeError('Invalid number of command line arguments')

    except RuntimeError as e:
        print(f'ERR: {e}', file=sys.stderr)

    ts = build_timestamp(commit_epoch)
    print(f'v{sys.argv[1]} {commit} {ts.strftime("%d-%m-%Y (%H:%M:%S)")}', end="")


if __name__ == "__main__":
    generate_version()
