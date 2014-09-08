__author__ = 'vmalaga'

import os
import sys
#import cx_Oracle
import argparse
#import string
import re

hostname = os.uname()[1]

class OraStats():
    def __init__(self, user, passwd, sid):
        import cx_Oracle
        self.user = user
        self.passwd = passwd
        self.sid = sid
        self.connection = cx_Oracle.connect( self.user , self.passwd , self.sid )
        cursor = self.connection.cursor()
        cursor.execute("select HOST_NAME from v$instance")
        for hostname in cursor:
            self.hostname = hostname[0]

    def asmdf(self, user, passwd, sid, diskname, format):
        #connection = cx_Oracle.connect( user , passwd , sid )
        cursor = self.connection.cursor()
        cursor.execute("select FREE_MB,TOTAL_MB from v$asm_diskgroup where NAME='"+diskname+"'")
        for free_val, total_val in cursor:
            used = (total_val - free_val)
            if format == 'cacti':
                sys.stdout.write("free:%s total:%s used:%s" % (free_val, total_val, used))
            else:
                print "PUTVAL %s/oracle/%s/gauge-disk_free interval=30 N:%s" % (self.hostname, sid, free_val)
                print "PUTVAL %s/oracle/%s/gauge-disk_free interval=30 N:%s" % (self.hostname, sid, total_val)
                print "PUTVAL %s/oracle/%s/gauge-disk_free interval=30 N:%s" % (self.hostname, sid, used)
        cursor.close()
        #connection.close()

    def phishio(self,user,passwrd,sid,format):
        cursor = self.connection.cursor()
        cursor.execute("""
        select sum ( decode ( name, 'physical reads', value, 0 ) ) datafile_reads,
        sum ( decode ( name, 'physical writes', value, 0 ) ) datafile_writes,
        sum ( decode ( name, 'redo writes', value, 0 ) ) redo_writes
        from v$sysstat
        where name in ( 'physical reads', 'physical writes', 'redo writes' )""")
        for datafile_reads, datafile_writes, redo_writes in cursor:
            if format == 'cacti':
                sys.stdout.write("datafile_reads:%s datafile_writes:%s redo_writes:%s" % (datafile_reads, datafile_writes, redo_writes))
            else:
                print "PUTVAL %s/oracle_%s/counter-physicalio_datafile_reads interval=30 N:%s" % (self.hostname, sid, datafile_reads)
                print "PUTVAL %s/oracle_%s/counter-physicalio_datafile_writes interval=30 N:%s" % (self.hostname, sid, datafile_writes)
                print "PUTVAL %s/oracle_%s/counter-physicalio_redo_writes interval=30 N:%s" % (self.hostname, sid, redo_writes)
        cursor.close()

    def activity(self,user, passwd, sid, format):
        cursor = self.connection.cursor()
        cursor.execute("""
        select sum ( decode ( name, 'parse count (total)', value, 0 ) ) parse_count
        , sum ( decode ( name, 'execute count', value, 0 ) ) execute_count
        , sum ( decode ( name, 'user commits', value, 0 ) ) u_commit
        , sum ( decode ( name, 'user rollbacks', value, 0 ) ) u_rollback
        from v$sysstat
        where name in ( 'parse count (total)', 'execute count', 'user commits', 'user rollbacks' )""")
        for parse_count, execute_count, u_commit, u_rollback in cursor:
            if format == 'cacti':
                sys.stdout.write("parse_count:%s execute_count:%s u_commit:%s u_rollback:%s" % (parse_count, execute_count, u_commit, u_rollback))
            else:
                print "PUTVAL %s/oracle_%s/counter-activity_parse_count interval=30 N:%s" % (self.hostname, sid, parse_count)
                print "PUTVAL %s/oracle_%s/counter-activity_execute_count interval=30 N:%s" % (self.hostname, sid, execute_count)
                print "PUTVAL %s/oracle_%s/counter-activity_user_commits interval=30 N:%s" % (self.hostname, sid, u_commit)
                print "PUTVAL %s/oracle_%s/counter-activity_user_rollbacks interval=30 N:%s" % (self.hostname, sid, u_rollback)
        cursor.close()

    def cursorstats(self,user, passwd, sid,format):
        cursor = self.connection.cursor()
        cursor.execute("""
        select sum ( decode ( name, 'opened cursors cumulative', value, 0)) total_cursors,sum ( decode ( name, 'opened cursors current',value,0)) current_cursors,sum ( decode ( name, 'session cursor cache hits',value,0)) sess_cur_cache_hits from v$sysstat where name in ( 'opened cursors cumulative','opened cursors current','session cursor cache hits' )""")
        for total_cursors, current_cursors, sess_cur_cache_hits in cursor:
            if format == 'cacti':
                sys.stdout.write("total_cursors:%s current_cursors:%s sess_cur_cache_hits:%s" % (total_cursors, current_cursors, sess_cur_cache_hits))
            else:
                print "PUTVAL %s/oracle_%s/counter-cursors_total interval=30 N:%s" % (self.hostname, sid, total_cursors)
                print "PUTVAL %s/oracle_%s/gauge-cursors_current interval=30 N:%s" % (self.hostname, sid, current_cursors)
                print "PUTVAL %s/oracle_%s/counter-cursors_cachehits interval=30 N:%s" % (self.hostname, sid, sess_cur_cache_hits)
        cursor.close()

    def waitstats(self, user, passwd, sid, format):
        cursor = self.connection.cursor()
        cursor.execute("""
        select n.wait_class, round(m.time_waited/m.INTSIZE_CSEC,3) AAS
        from   v$waitclassmetric  m, v$system_wait_class n
        where m.wait_class_id=n.wait_class_id and n.wait_class != 'Idle'
        union
        select  'CPU', round(value/100,3) AAS
        from v$sysmetric where metric_name='CPU Usage Per Sec' and group_id=2
        union select 'CPU_OS', round((prcnt.busy*parameter.cpu_count)/100,3) - aas.cpu
        from
            ( select value busy
                from v$sysmetric
                where metric_name='Host CPU Utilization (%)'
                and group_id=2 ) prcnt,
                ( select value cpu_count from v$parameter where name='cpu_count' )  parameter,
                ( select  'CPU', round(value/100,3) cpu from v$sysmetric where metric_name='CPU Usage Per Sec' and group_id=2) aas
        """)
        for wait in cursor:
            wait_name = wait[0]
            wait_value = wait[1]
            if format == 'cacti':
                sys.stdout.write("%s:%s " % (re.sub(r'\W', '', wait_name), wait_value))
            else:
                #print re.sub(r'\W', '', wait_name).lower() , wait_value
                print "PUTVAL %s/oracle_%s/counter-wait_%s interval=30 N:%s" % (self.hostname, sid, re.sub(r'\W', '', wait_name).lower(), wait_value )

#connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--format', help="Output format, default collectd", choices=['cacti', 'collectd'], default='collectd')
    subparsers = parser.add_subparsers(dest='stat')
    parser_asm = subparsers.add_parser('ASM', help="Get stats from ASM disks")
    parser_asm.add_argument('-u', '--user', help="Username with sys views grant", required=True)
    parser_asm.add_argument('-p', '--passwd', required=True)
    parser_asm.add_argument('-s', '--sid', help="tnsnames SID to connect", required=True)
    parser_asm.add_argument('-d', '--disk', help="ASM disk to get stats", required=True)

    parser_tbs = subparsers.add_parser('TBS', help="Get stats from tablespaces")
    parser_tbs.add_argument('-u', '--user', help="Username with sys views grant", required=True)
    parser_tbs.add_argument('-p', '--passwd', required=True)
    parser_tbs.add_argument('-s', '--sid', help="tnsnames SID to connect", required=True)
    parser_tbs.add_argument('-t', '--tablespace', help="Tablespace to get stats", required=True)

    parser_phio = subparsers.add_parser('PHYSIO', help="Get physical IO stats")
    parser_phio.add_argument('-u', '--user', help="Username with sys views grant", required=True)
    parser_phio.add_argument('-p', '--passwd', required=True)
    parser_phio.add_argument('-s', '--sid', help="tnsnames SID to connect", required=True)

    parser_actv = subparsers.add_parser('ACTV', help="Get database activity stats")
    parser_actv.add_argument('-u', '--user', help="Username with sys views grant", required=True)
    parser_actv.add_argument('-p', '--passwd', required=True)
    parser_actv.add_argument('-s', '--sid', help="tnsnames SID to connect", required=True)

    parser_curs = subparsers.add_parser('CURS', help="Get database cursors stats")
    parser_curs.add_argument('-u', '--user', help="Username with sys views grant", required=True)
    parser_curs.add_argument('-p', '--passwd', required=True)
    parser_curs.add_argument('-s', '--sid', help="tnsnames SID to connect", required=True)

    parser_waits = subparsers.add_parser('WAITS', help="Get database waits stats")
    parser_waits.add_argument('-u', '--user', help="Username with sys views grant", required=True)
    parser_waits.add_argument('-p', '--passwd', required=True)
    parser_waits.add_argument('-s', '--sid', help="tnsnames SID to connect", required=True)

    parser_all = subparsers.add_parser('ALL', help="Get all database stats")
    parser_all.add_argument('-u', '--user', help="Username with sys views grant", required=True)
    parser_all.add_argument('-p', '--passwd', required=True)
    parser_all.add_argument('-s', '--sid', help="tnsnames SID to connect", required=True)

    args = parser.parse_args()

    if args.stat == "ASM":
        #args_asm = parser_asm.parse_args()
        stats = OraStats(args.user, args.passwd ,args.sid)
        stats.asmdf(args.user,args.passwd,args.sid,args.disk,args.format)

    if args.stat == "PHYSIO":
        stats = OraStats(args.user, args.passwd, args.sid)
        stats.phishio(args.user, args.passwd, args.sid, args.format)

    if args.stat == "ACTV":
        stats = OraStats(args.user, args.passwd, args.sid)
        stats.activity(args.user, args.passwd, args.sid, args.format)

    if args.stat == "CURS":
        stats = OraStats(args.user, args.passwd, args.sid)
        stats.cursorstats(args.user, args.passwd, args.sid, args.format)

    if args.stat == "WAITS":
        stats = OraStats(args.user, args.passwd, args.sid)
        stats.waitstats(args.user, args.passwd, args.sid, args.format)

    if args.stat == "ALL":
        stats = OraStats(args.user, args.passwd, args.sid)
        stats.cursorstats(args.user, args.passwd, args.sid, args.format)
        stats.phishio(args.user, args.passwd, args.sid, args.format)
        stats.activity(args.user, args.passwd, args.sid, args.format)
        stats.waitstats(args.user, args.passwd, args.sid, args.format)
