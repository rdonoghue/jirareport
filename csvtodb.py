import sys, csv, sqlite3


def parseheader(csv_file):
# necessary to parse this every time because the number of columns
# varies based on the number of comments, attachements, etc.
# if I cared more I think I could make this smarter, but I don't
    try:
        parse_f = open(csv_file, 'rt')
    except:
        sys.exit("No such file!")
    reader = csv.reader(parse_f)
    for firstrow in reader:
        local_indices = {
        "Issue_ID": firstrow.index("Issue id"),
        "Issue_Key": firstrow.index("Issue key"),
        "Issue_Type": firstrow.index("Issue Type"),
        "Team":       firstrow.index("Custom field (Luminal Team)"),
        "Estimate" : firstrow.index("Custom field (Story Points)"),
        "Effort": firstrow.index("Custom field (Final Effort Assessment)"),
        "Status": firstrow.index("Status"),
#        "Summary": firstrow.index("Summary"),
#        I was burning a lot of effort trying to sterilize the
#       content of the summary but then I realized I don't
#       Actually use it. Maybe a future feature.
        }
        break
    parse_f.close()
    return local_indices

def teamline(full_team,short_team):
    cur.execute("SELECT SUM(Estimate), sum(Effort) FROM t WHERE Team = '{}'".format(full_team))
    all_rows = cur.fetchall()
    clean_rows=all_rows[0]
    current_estimates=clean_rows[0]
    current_effort=clean_rows[1]
    cur.execute("SELECT SUM(Estimate), sum(Effort) FROM t WHERE Team = '{}' AND Issue_Type = 'Bug'".format(full_team))
    bug_rows = cur.fetchall()
    clean_bug_rows=bug_rows[0]
#    print(clean_bug_rows)
    bug_estimates = int(clean_bug_rows[0] or 0)
    bug_effort = int(clean_bug_rows[1] or 0)

    cur.execute("SELECT SUM(Estimate), sum(Effort) FROM t WHERE Team = '{}' AND status !='Done' and status !='Will Not Fix'".format(full_team))
    unfinished_rows = cur.fetchall()
    clean_unfinished_rows=unfinished_rows[0]
    unfinished_estimates = clean_unfinished_rows[0]
    unfinished_effort = clean_unfinished_rows[1]
    cur.execute("SELECT SUM(Estimate), sum(Effort) FROM t WHERE Team = '{}' AND (status ='Done' or status = 'Will Not Fix')".format(full_team))
    finished_rows = cur.fetchall()
    clean_finished_rows=finished_rows[0]
    finished_estimates = clean_finished_rows[0]
    finished_effort = clean_finished_rows[1]
    if current_estimates is None:
        current_estimates=0
    if current_effort is None:
        current_effort=0
    if finished_effort is None:
        finished_effort=0
    if unfinished_effort is None:
        unfinished_effort=0
    if bug_effort is None:
        bug_effort=0
    current_effort=int(current_effort)

#    current_estimates = 2
#    current_effort=3
#    finished_effort=4
#    unfinished_effort=5
#    bug_effort=6


    print("{0:<15s}{1:>8g}{2:>10g}{3:>12g}{4:>12g}{5:>7g}".format(short_team,\
    current_estimates,\
    current_effort,\
    finished_effort,\
    unfinished_effort,\
    bug_effort))


def sumline():
    cur.execute("SELECT SUM(Estimate), sum(Effort) FROM t")
    all_rows = cur.fetchall()
    clean_rows=all_rows[0]
    current_estimates=clean_rows[0]
    current_effort=clean_rows[1]
    cur.execute("SELECT SUM(Estimate), sum(Effort) FROM t WHERE Issue_Type = 'Bug'")
    bug_rows = cur.fetchall()
    clean_bug_rows=bug_rows[0]
    bug_estimates = clean_bug_rows[0]
    bug_effort = clean_bug_rows[1]
    cur.execute("SELECT SUM(Estimate), sum(Effort) FROM t WHERE status !='Done'")
    unfinished_rows = cur.fetchall()
    clean_unfinished_rows=unfinished_rows[0]
    unfinished_estimates = clean_unfinished_rows[0]
    unfinished_effort = clean_unfinished_rows[1]
    cur.execute("SELECT SUM(Estimate), sum(Effort) FROM t WHERE status ='Done'")
    finished_rows = cur.fetchall()
    clean_finished_rows=finished_rows[0]
    finished_estimates = clean_finished_rows[0]
    finished_effort = clean_finished_rows[1]

    print("{0:<15s}{1:>8g}{2:>10g}{3:>12g}{4:>12g}{5:>7g}".format("Total",current_estimates,current_effort,finished_effort,unfinished_effort,bug_effort))


if len(sys.argv) > 1:
    samplefile=sys.argv[1]
else:
    sys.exit("No file selected!")


jira_indices = parseheader(samplefile)

header_list=[]







con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("CREATE TABLE t ('Issue_ID' INTEGER PRIMARY KEY)")
for headername in jira_indices:
    if headername != "Issue_ID":
        cur.execute("ALTER TABLE t ADD COLUMN '{colname}'".\
        format(colname=headername))

ex_f = open(samplefile, 'rt')

ex_reader = csv.reader(ex_f)
ex_rowcount=0
for ex_row in ex_reader:
    if (ex_rowcount !=0):
        thisrow = list(ex_row)
        key_id=(thisrow[jira_indices["Issue_ID"]])
## Ok, need to CREATE and empty row first, then try to update it

        for keyheaders in jira_indices:
            columnname=keyheaders
            offset=jira_indices[keyheaders]
            write_value=thisrow[offset].replace("'","XXXXX")
            if not write_value:
                write_value=0
            if keyheaders == "Issue_ID":
                cur.execute("INSERT INTO t ({c}) VALUES ({w})".\
                format(c=keyheaders, w=write_value))
            else:
                cur.execute("UPDATE t SET {}='{}' WHERE Issue_ID={}".\
                format(keyheaders, write_value, key_id))

##            cur.execute(sqlstring)
    #            cur.execute(sqlstring)
    #            print("Update t SET",keyheaders,"= '",write_value)
    #            print("UPDATE t SET {c}='{w}' WHERE Issue_ID='{k}'".\
    #            format(c=keyheaders, w=write_value, k=key_id))
    ex_rowcount+=1

# Cloud OS Results

if len(sys.argv) > 2:
    print("Development Sprint {}".format(sys.argv[2]))

print("{0:<15s}{1:<10s}{2:>8s}{3:>12s}{4:>12s}{5:>7s}".format(" ","Estimate","Effort","Finished","Unfinished","Bugs"))
print("-" * 14,"-" * 8,"-" * 9, "-" * 11, "-" * 11,"-" * 6,)
teamline("CloudOS Team","COS")
teamline("LRT Team","LRT")
teamline("Toolchain Team","TC")
teamline("NBN Team","NBN")
teamline("Transcriber","Transcriber")
teamline("Capture Team","Capture")
teamline("QA Team","QA")
teamline("Crossteam","Cross Team")
print("-" * 14,"-" * 8,"-" * 9, "-" * 11, "-" * 11,"-" * 6,)
sumline()




ex_f.close()
con.close()
