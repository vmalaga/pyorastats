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
  
  Now if you want send this metrics to graphite need to complete your collectd config with this new 2 sections:
  ```
  LoadPlugin exec
  <Plugin exec>
        Exec collectd "python" "/path/to/ora_system_stats.py" "ALL" "-u" "system" "-p" "passwd" "-s" "SID"
  </Plugin>

  LoadPlugin write_graphite
  <Plugin write_graphite>
    <Node "graphitehost">
      Host "localhost"
      Port "2003"
      Protocol "tcp"
      LogSendErrors true
      Prefix "collectd."
    </Node>
  </Plugin>
  ```

  
Screenshot grafana dashboard
http://lnxnet.es/oracle-dashboard-with-graphite-collectd-and-pyorastats/

![Alt text](http://i61.tinypic.com/35l6ubp.png)
