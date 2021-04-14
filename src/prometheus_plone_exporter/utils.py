import logging
LOG = logging.getLogger(__name__)

def get_ts_pid(pidfile):
    """Read a pidfile, return a PID."""
    try:
        with open(pidfile) as f:
            pid = f.readline()
        if pid.strip().isdigit():
            pid = int(pid.strip())
        else:
            LOG.warning("Unable to read pidfile %s file contains %r; process metrics will fail!", pidfile, pid)
            pid = None
    except EnvironmentError:
        LOG.warning("Unable to read pidfile %s; process metrics will fail!", pidfile)
        pid = None
    return pid