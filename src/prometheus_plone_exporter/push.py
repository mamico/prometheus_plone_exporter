# push data to pushgateway
import re
import subprocess
import click
import requests
import psutil
import yaml
import logging
import time
from .utils import get_ts_pid

LOG = logging.getLogger(__name__)

#!/bin/bash
# z=$(ps aux)
# while read -r z
# do
#    var=$var$(awk '{print "cpu_usage{process=\""$11"\", pid=\""$2"\"}", $3z}{print "virtual_memory{process=\""$11"\", pid=\""$2"\"}", $5z}');
#    vrt=$vrt$(awk '{print "virtual_memory{process=\""$11"\", pid=\""$2"\"}", $5z}');
#    rss=$rss$(awk '{print "rss_memory{process=\""$11"\", pid=\""$2"\"}", $6z}');
# done <<< "$z"
# # curl -X POST -H  "Content-Type: text/plain" --data "$var$vrt$rss
# curl -X POST -H  "Content-Type: text/plain" --data "$var
# " http://localhost:9091/metrics/job/top/instance/machine

@click.command()
@click.option('-p', '--pushgateway', required=True, default='http://localhost:9091')
@click.option('-e', '--every', default=0)
@click.option('-v', '--verbose', count=True)
@click.argument('config_yml')
def main(pushgateway, every, verbose, config_yml):

    with open(config_yml, 'r') as fh:
        config = yaml.safe_load(fh)

    if verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose == 0:
        logging.basicConfig(level=logging.WARNING)

    procs = {}

    def get_data(pid, name):
        if pid not in procs:
            try:
                procs[pid] = psutil.Process(pid)
            except psutil.NoSuchProcess:
                LOG.warning('no process for pid %s %s', pid, name)
                return
        proc = procs[pid]
        mem = proc.memory_info()
        cpu = proc.cpu_times()
        io = proc.io_counters()
        cpu_perc = proc.cpu_percent()  # interval=0.2)
        return f'''
process_cpu_seconds_total{{process="{name}"}} {cpu.user + cpu.system}
process_cpu_percentage{{process="{name}"}} {cpu_perc}
process_virtual_memory_bytes{{process="{name}"}} {mem.vms}
process_resident_memory_bytes{{process="{name}"}} {mem.rss}
process_open_fds{{process="{name}"}} {proc.num_fds()}
process_io_read_count{{process="{name}"}} {io.read_count}
process_io_write_count{{process="{name}"}} {io.write_count}
process_io_read_bytes{{process="{name}"}} {io.read_bytes}
process_io_write_bytes{{process="{name}"}} {io.write_bytes}
process_num_threads{{process="{name}"}} {proc.num_threads()}
'''

    while True:
        for buildout in config:
            has_data = False
            data = '''
# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
# TYPE process_cpu_seconds_total counter
# HELP process_cpu_percentage CPU utilization as a percentage.
# TYPE process_cpu_percentage gauge
# HELP process_max_fds Maximum number of open file descriptors.
# TYPE process_max_fds gauge
# HELP process_open_fds Number of open file descriptors.
# TYPE process_open_fds gauge
# HELP process_resident_memory_bytes Resident memory size in bytes.
# TYPE process_resident_memory_bytes gauge
# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
# TYPE process_start_time_seconds gauge
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
# TYPE process_virtual_memory_bytes gauge
# HELP process_io_read_count Total number of read operations performed.
# TYPE process_io_read_count counter
# HELP process_io_write_count Total number of write operations performed.
# TYPE process_io_write_count counter
# HELP process_io_read_bytes Total number of bytes read.
# TYPE process_io_read_bytes counter
# HELP process_io_write_bytes Total number of bytes written.
# TYPE process_io_write_bytes counter
# HELP process_num_threads The number of threads currently used by this process.
# TYPE process_num_threads gauge
'''
            if not config[buildout]:
                LOG.warning('no process defined for %s', buildout)
                continue
            for item in config[buildout]:
                if item.get('type') == 'supervisor':
                    try:
                        programs = subprocess.check_output([item['cmd'], 'status']).split(b'\n')
                    except:
                        LOG.exception('%s status error', item.get('cmd'))
                        continue
                    for line in programs:
                        # haproxy                          RUNNING    pid 32594, uptime 2 days, 1:25:38
                        line = line.decode('UTF-8')
                        match = re.match(r'^(?P<name>[\w\.]+)\s*RUNNING\s+pid\s+(?P<pid>[\d]+)', line)
                        if match:
                            name = match.group('name')
                            pid = match.group('pid')
                            if not pid or not pid.isdigit():
                                LOG.waring('missing pid in "%s"', line)
                                continue
                            pid = int(pid)
                            d = get_data(pid, name)
                            if d:
                                data += d
                                has_data = True
                else:
                    pidfile = item['pidfile']
                    name = item['process']
                    pid = get_ts_pid(pidfile)
                    if not pid:
                        continue
                    d = get_data(pid, name)
                    if d:
                        data += d
                        has_data = True
            if has_data:
                LOG.debug('%s %s',
                    f'{pushgateway}/metrics/job/node/buildout/{buildout}',
                    data)
                try:
                    # The default port the Pushgateway is listening to is 9091. The path looks like
                    # /metrics/job/<JOB_NAME>{/<LABEL_NAME>/<LABEL_VALUE>}
                    res = requests.post(
                        f'{pushgateway}/metrics/job/node/buildout/{buildout}',
                        headers={'Content-Type': 'text/plain'},
                        data=data)  # '\n'.join(data) + '\n\n'
                except requests.exceptions.ConnectionError:
                    LOG.warning('pushgateway connection error')
                    res = None
                if res is None:
                    pass
                elif not res:
                    LOG.warning('pushgateway error %s %s', res.status_code, res.text)
        if not every:
            break
        time.sleep(every)
