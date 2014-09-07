# ora_system_stats

## Oracle system stats with output for *collectd* and *cacti*

usage: `ora_system_stats.py [-h] [-f {cacti,collectd}] {ASM,TBS,PHYSIO,ACTV,CURS} ...`

stats arguments:<br />


    
* ASM    Get stats from ASM disks<br />
* TBS    Get stats from tablespaces<br />
* PHYSIO Get physical IO stats<br />
* ACTV   Get database activity stats<br />
* CURS   Get database cursors stats<br />


optional arguments:<br />
  -h, --help            show this help message and exit<br />
  -f {cacti,collectd}, --format {cacti,collectd} Output format, default collectd
