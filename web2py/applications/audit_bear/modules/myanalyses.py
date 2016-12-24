#Place to put my analyses for now
import auditLog
import ballotImage
import dateMod
import datetime
import dateutil.parser
import report

def datesUnset(dateclass, ballotclass):
    r = report.Report()
    t1 = report.Table()
    t2 = report.Table()
    
    r.addTitle('Incorrectly Set Dates')

    if not (len(dateclass.D1) or len(dateclass.D2)):
        r.addTextBox('No dates were found to be incorrectly set after being opened for elections')
    else:
        precinctMap = ballotclass.getPrecinctNameMap()
        d = {}

        r.addTextBox('These machines have been identified as having incorrectly set clocks. Having invalid clocks can preclude further log analysis. The results have been catagorized into two tables')

        r.addTextBox('<p><b>Table 1: Precincts Manually Adjusted During Elections</b>')
        if len(dateclass.D1) == 0:
            r.addTextBox('No machines found.')
        else:
            r.addTextBox('<i>List of machines by precinct with manual time adjustments during election day and after being opened for voting</i></p>')
            t1.addHeader('Precinct')
            t1.addHeader('# of Machines')

            for k in dateclass.D1.keys():
                if k in precinctMap:
                    key = precinctMap[k]
                elif k in ballotclass.getEarlyVotingList():
                    key = 'Absentee'
                elif k in ballotclass.getFailsafeList():
                    key = 'Failsafe'
                else:
                    key = k

                if key in d:
                    d[key] = d[key] + 1
                else:
                    d.update({key:1})
            for k,v in d.iteritems():
                t1.addRow([k, str(v)])

            r.addTable(t1)

        if len(dateclass.D2) != 0:
            r.addTextBox('<p><b>Table 2: Machines never set correctly</b>')
            r.addTextBox('<i>List of machines that conducted election day voting start to finish with an incorrect clock.</i></p>')
            t2.addHeader('Serial #')
            t2.addHeader('Open Date')
            t2.addHeader('Close Date')
            for k,v in dateclass.D2.iteritems():
                t2.addRow([str(k), str(v[0]), str(v[1])])

            r.addTable(t2)
        else:
            r.addTextBox('No machines found.')

    return r 

def dateErrors(dateclass, ballotclass):
    r = report.Report()
    t = report.Table()
    
    r.addTitle('Datetime Errors')

    if len(dateclass.D3) == 0:
        r.addTextBox('No date errors found')
    else:
        r.addTextBox('List machines with detected date anomalies.  Includes last known "good" event as well as what event was determined to be the error and how many following events it affected.')
        t.addHeader('Machine')
        t.addHeader('Last Event')
        t.addHeader('Anomalous Event')
        t.addHeader('Occurances')
        for k,v in dateclass.D3.iteritems():
            t.addRow([k, str(v[0]), str(v[1]), str(v[2])])

        r.addTable(t)

    return r 
