# pyorastats

## Oracle system stats with output for *collectd* and *cacti*

With pyorastats you can easy create a dashboard with graphite and grafana

usage: `ora_system_stats.py [-h] [-f {cacti,collectd}] {ASM,TBS,PHYSIO,ACTV,CURS,WAITS,ALL} ...`

stats arguments:<br />


    
* ASM    Get stats from ASM disks<br />
* TBS    Get stats from tablespaces<br />
* PHYSIO Get physical IO stats<br />
* ACTV   Get database activity stats<br />
* CURS   Get database cursors stats<br />
* WAITS  Get database waits stats<br />
* ALL    Get all database stats<br />


optional arguments:<br />
  -h, --help            show this help message and exit<br />
  -f {cacti,collectd}, --format {cacti,collectd} Output format, default collectd
  
  
Screenshot grafana dashboard

![Alt text](http://i61.tinypic.com/w7yhc6.png)
