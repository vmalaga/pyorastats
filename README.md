ora_system_stats
================

Oracle system stats with output for collectd and cacti

usage: ora_system_stats.py [-h] [-f {cacti,collectd}] {ASM,TBS,PHYSIO,ACTV,CURS} ...

stats arguments:
    ASM                 Get stats from ASM disks
    TBS                 Get stats from tablespaces
    PHYSIO              Get physical IO stats
    ACTV                Get database activity stats
    CURS                Get database cursors stats

optional arguments:
  -h, --help            show this help message and exit
  -f {cacti,collectd}, --format {cacti,collectd}
                        Output format, default collectd
