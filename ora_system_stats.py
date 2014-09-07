__author__ = 'vmalaga'

import os
import sys
import cx_Oracle
import argparse
import string

hostname = os.uname()[1]

class orastats:

    def asmdf(self, user, passwd, sid, diskname, format):
        connection = cx_Oracle.connect( user , passwd , sid )
        cursor = connection.cursor()
        cursor.execute("select FREE_MB,TOTAL_MB from v$asm_diskgroup where NAME='"+diskname+"'")
        for free_val, total_val in cursor:
            used = (total_val - free_val)
            if format == 'cacti':
                sys.stdout.write("free:%s total:%s used:%s" % (free_val, total_val, used))
            else:
                print "PUTVAL %s/oracle/disk_free interval=30 N:%s" % (hostname, free_val)
                print "PUTVAL %s/oracle/disk_free interval=30 N:%s" % (hostname, total_val)
                print "PUTVAL %s/oracle/disk_free interval=30 N:%s" % (hostname, used)
        cursor.close()
        connection.close()

    def phishio(self,USER,PASSWD,SID,format):
        connection = cx_Oracle.connect( USER , PASSWD , SID )
        cursor = connection.cursor()
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
                print "PUTVAL %s/oracle/physicalio-datafile_reads interval=30 N:%s" % (hostname, datafile_reads)
                print "PUTVAL %s/oracle/physicalio-datafile_writes interval=30 N:%s" % (hostname, datafile_writes)
                print "PUTVAL %s/oracle/physicalio-redo_writes interval=30 N:%s" % (hostname, redo_writes)
        cursor.close()
        connection.close()

    def activity(self,USER,PASSWD,SID,format):
        connection = cx_Oracle.connect( USER , PASSWD , SID )
        cursor = connection.cursor()
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
                print "PUTVAL %s/oracle/activity-parse_count interval=30 N:%s" % (hostname, parse_count)
                print "PUTVAL %s/oracle/activity-execute_count interval=30 N:%s" % (hostname, execute_count)
                print "PUTVAL %s/oracle/activity-user_commits interval=30 N:%s" % (hostname, u_commit)
                print "PUTVAL %s/oracle/activity-user_rollbacks interval=30 N:%s" % (hostname, u_rollback)
        cursor.close()
        connection.close()

    def cursorstats(self,USER,PASSWD,SID,format):
        connection = cx_Oracle.connect( USER , PASSWD , SID )
        cursor = connection.cursor()
        cursor.execute("""
        select sum ( decode ( name, 'opened cursors cumulative', value, 0)) total_cursors,sum ( decode ( name, 'opened cursors current',value,0)) current_cursors,sum ( decode ( name, 'session cursor cache hits',value,0)) sess_cur_cache_hits from v$sysstat where name in ( 'opened cursors cumulative','opened cursors current','session cursor cache hits' )""")
        for total_cursors, current_cursors, sess_cur_cache_hits in cursor:
            if format == 'cacti':
                sys.stdout.write("total_cursors:%s current_cursors:%s sess_cur_cache_hits:%s" % (total_cursors, current_cursors, sess_cur_cache_hits))
            else:
                print "PUTVAL %s/oracle/cursors-total interval=30 N:%s" % (hostname, total_cursors)
                print "PUTVAL %s/oracle/cursors-current interval=30 N:%s" % (hostname, current_cursors)
                print "PUTVAL %s/oracle/cursors-cachehits interval=30 N:%s" % (hostname, sess_cur_cache_hits)
        cursor.close()
        connection.close()





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

    args = parser.parse_args()

    if args.stat == "ASM":
        #args_asm = parser_asm.parse_args()
        stats = orastats()
        stats.asmdf(args.user,args.passwd,args.sid,args.disk,args.format)

    if args.stat == "PHYSIO":
        stats = orastats()
        stats.phishio(args.user, args.passwd, args.sid, args.format)

    if args.stat == "ACTV":
        stats = orastats()
        stats.activity(args.user, args.passwd, args.sid, args.format)

    if args.stat == "CURS":
        stats = orastats()
        stats.cursorstats(args.user, args.passwd, args.sid, args.format)