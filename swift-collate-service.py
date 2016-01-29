#!/bin/env python

from daemon import DaemonContext
from lockfile import FileLock
import grp
import signal
import server
import ConfigParser
import os.path

# Retrieve the configuration
config = ConfigParser.RawConfigParser()
config.read( os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'swift_collate.cfg')  )

root_path = config.get('daemon', 'root_path')
pidfile_path = config.get('daemon', 'pidfile_path')
grname = config.get('daemon', 'grname')
log_path = config.get('daemon', 'log_path')
error_log_path = config.get('daemon', 'error_log_path')

httpd_gid = grp.getgrnam(grname).gr_gid
stdout_file = open(log_path, 'w+')
stderr_file = open(error_log_path, 'w+')

def program_cleanup():
    stdout_file.close()
    stderr_file.close()

context = DaemonContext(
    working_directory=root_path,
    pidfile=FileLock(pidfile_path),
    gid=httpd_gid,
    initgroups=False, # RHEL Satellite dependency issues
    stdout=stdout_file,
    stderr=stderr_file,
    signal_map = {
        signal.SIGTERM: program_cleanup
        }
    )

with context:
    server.main()
