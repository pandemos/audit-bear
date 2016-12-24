# EVENT ANOMALIES ANALYSES MODULE
import auditLog
import ballotImage
import dateMod
import dateutil.parser
import report

import operator
import string as stri
import math
import StringIO
import matplotlib
import matplotlib.pyplot as plt

from dateutil.parser import parse

def eventAnomalies(data, r):
    emMap = {}
    emMap2 = {}
    emList = []
    for x in data.getEntryList():
        if emMap.has_key(x.eventNumber):
            if x.serialNumber in emMap[x.eventNumber]:
                continue
            else:
                emMap[x.eventNumber] += [x.serialNumber]
        else:
            emMap[x.eventNumber] = [x.serialNumber]
    for x2 in emMap:
        emMap2[x2] = len(emMap[x2])
    emList = sorted(emMap2.iteritems(), key=operator.itemgetter(1))
    for x3 in emList:
        if x3[1] == 1:
            r.addTextBox("Machine %s has 1 occurence of event %s" % (emMap[x3[0]][0], x3[0]))
    return r
    
def lowBatteryMachines(data, ballot, date, r):
    plt.ioff()
    d = str(date.eday)
    d = d.split("-")
    d2 = d[1]+'/'+d[2]+'/'+d[0]
    r.addTitle('Machines with possible low batteries')
    lowBatteryList = []
    lowBatteryMap = {}
    totalList = []
    avg = 0
    ssum = 0.00000000
    ssum2 = 0.00000000
    stdev = 0.00000000
    for x in data.getEntryList():
        s = x.dateTime.split(" ")
        t = s[1].split(":")
        if t[0] == '':
            continue
        elif x.eventNumber == '0001635' and (s[0] == d2) and stri.atoi(t[0]) > 7 and stri.atoi(t[0]) < 19:
            if x.serialNumber not in lowBatteryList and not lowBatteryMap.has_key(x.serialNumber):
                lowBatteryList.append(x.serialNumber)
                lowBatteryMap[x.serialNumber] = 1
            elif lowBatteryMap.has_key(x.serialNumber):
                temp = lowBatteryMap[x.serialNumber]
                temp = temp + 1
                lowBatteryMap[x.serialNumber] = temp
    if len(lowBatteryMap) < 1:
        #lowBatteryTable.addRow('This county shows no indication of machines with low battery.')
        #r.addTextBox("This county shows no indication of machines with low battery.")
        r.addTextBox("No problems found.")
    else:
        lowBatteryTable = report.Table()
        for n in lowBatteryMap.values():
            avg = avg + n
        avg = avg/len(lowBatteryMap.values())
        for n2 in lowBatteryMap.values():
                ssum = ssum + ((n2-avg)**2)
        ssum2 = ssum/len(lowBatteryMap.values())
        stdev = math.sqrt(ssum2)
        #print avg
        #print stdev
        for l in lowBatteryMap:
            precinctNum = None
            precinctName = None
            if ballot.machinePrecinctNumMap.has_key(l):
                precinctNum = ballot.machinePrecinctNumMap[l]
                precinctName = ballot.machinePrecinctNameMap[l]
            elif l in ballot.earlyVotingList:
                precinctNum = '750'
                precinctName = 'Absentee'
            elif l in ballot.failsafeList:
                precinctNum = '850'            
                precinctName = 'Failsafe'
            if lowBatteryMap[l] >= (avg + (3*stdev)):
                totalList.append((precinctNum, l, precinctName, lowBatteryMap[l], '0001635', data.getEventDescription('0001635')))
        totalList.sort()        
        r.addTextBox("The following voting machines have an unusually large number of log messages related to their Internal Power Supply.  The meaning of these messages is not documented.  This might indicate potential battery or power supply issues.  You may wish to check whether the battery of these machines is in good working condition.")
        r.addTextBox(" ")
        for t in totalList:
            lowBatteryTable.addRow(['In %s (#%s), ' % (t[2], t[0]), '   ', ' machine %s had %d power-related events.' % (t[1], t[3])])
        r.addTable(lowBatteryTable)
    return r
    
def getCalibrationEvents3(data, ballot, date, r):
    d = str(date.eday)
    d = d.split("-")
    d2 = d[1]+'/'+d[2]+'/'+d[0]
    r.addTitle("Machines with recurring display issues")
    totalCalMap = {}
    for x in data.getEntryList():
        s = x.dateTime.split(" ")
        t = s[1].split(":")
        if t[0] == '':
            continue
        elif stri.atoi(t[0]) > 7 and stri.atoi(t[0]) < 19 and (s[0] == d2):
            if x.eventNumber == '0001628':
                if x.serialNumber not in ballot.earlyVotingList and x.serialNumber not in ballot.failsafeList and ballot.machinePrecinctNumMap.has_key(x.serialNumber):
                    if totalCalMap.has_key(x.serialNumber):
                        temp = totalCalMap[x.serialNumber]
                        temp = temp + 1
                        totalCalMap[x.serialNumber] = temp
                    else:
                        totalCalMap[x.serialNumber] = 1
    totalCalList = []
    for z in totalCalMap:
        if ballot.machinePrecinctNameMap.has_key(z) and totalCalMap[z] > 3:
            totalCalList.append(ballot.machinePrecinctNumMap[z], ballot.machinePrecinctNameMap[z], z, totalCalMap[z])
    totalCalList.sort()
    calTable = report.Table()
    b = True
    if len(totalCalList) > 0:
        for y in totalCalList:
            if b == True:
                r.addTextBox('The following machines recorded at least one log message related to the calibration of the screen.  The detailed meaning of this event is not documented.  You may want to check why the machine recorded calibration errors and whether it indicates any kind of problem with the machine that should be addressed before future elections.')
                r.addTextBox(" ")
                b = False
            calTable.addRow(["In %s  (#%s) " % (y[1], y[0]),  "machine %s recorded %d calibration errors." % (y, totalCalMap[y])])
    if b == True:
        #r.addTextBox("This county experienced no anomalous calibration errors.")
        r.addTextBox("No problems found.")
    r.addTable(calTable)
    return r        
    
def getCalibrationEvents2(data, ballot, date, r):
    d = str(date.eday)
    d = d.split("-")
    d2 = d[1]+'/'+d[2]+'/'+d[0]
    r.addTitle("Votes cast when the voting machine screen may not have been calibrated")
    calMap = {}
    calList = []
    for x in data.getEntryList():
        s = x.dateTime.split(" ")
        t = s[1].split(":")
        if t[0] == '':
            continue
        elif stri.atoi(t[0]) > 6 and stri.atoi(t[0]) < 19 and (s[0] == d2):
            if x.eventNumber == '0001651':
                if calMap.has_key(x.serialNumber):
                    if calMap[x.serialNumber] == 0:
                        continue
                    elif calMap[x.serialNumber] == 2:
                        calMap[x.serialNumber] == 0
                else:
                    calMap[x.serialNumber] = False
            elif x.eventNumber == '0001510' or x.eventNumber == '0001511':
                if calMap.has_key(x.serialNumber):
                    if calMap[x.serialNumber] == 0:
                        calMap[x.serialNumber] = 1
            elif x.eventNumber == '0001655':
                if calMap.has_key(x.serialNumber):
                    if calMap[x.serialNumber] == 0:
                        calMap[x.serialNumber] = 2
                    elif calMap[x.serialNumber] == 1:
                        calMap[x.serialNumber] = 2
    b = True
    calTable = report.Table()
    for y in calMap:
        if calMap[y] == 1:
            if ballot.machinePrecinctNumMap.has_key(y):
                calList.append((ballot.machinePrecinctNumMap[y], ballot.machinePrecinctNameMap[y], y))
    calList.sort()
    for y2 in calList:
        if ballot.machinePrecinctNameMap.has_key(y):
            if b == True:
                r.addTextBox("The following machines may have recorded votes being cast while the terminal screen seemed to have calibration problems.  You may wish to find these machines and check whether their screen is properly calibrated and verify the votes.")
                r.addTextBox(" ")
                b = False
            calTable.addRow(["In %s (#%s), " % (y2[1], y2[0]), "machine %s had votes cast when it was possibly not calibrated." % (y2[2],)])
    if b == True:
        r.addTextBox("No problems found.")
    r.addTable(calTable)
    return r
                
            
    
def getCalibrationEvents(data, ballot, r):
    plt.ioff()
    r.addTitle('Terminals with Callibration Problems')
    numOccurrencesWarningMap = {}
    numOccurrencesRecalibrationMap = {}
    timeOccurrencesMap = {}
    totalWarningList = []
    totalRecalibrationList = []
    avg = 0
    stdev = 0.00000000
    ssum = 0.00000000
    ssum2 = 0.00000000
    for x in data.getEntryList():
        s = x.dateTime.split(" ")
        t = s[1].split(":")
        if t[0] == '':
            continue
        elif stri.atoi(t[0]) > 6 and stri.atoi(t[0]) < 19 and (s[0] == '11/02/2010' or s[0] == '06/08/2010'):
            if x.eventNumber == '0001651':
                if numOccurrencesWarningMap.has_key(x.serialNumber):
                    temp = numOccurrencesWarningMap[x.serialNumber]
                    temp = temp + 1
                    numOccurrencesWarningMap[x.serialNumber] = temp
                else:
                    totalWarningList.append((x.serialNumber, ballot.machinePrecinctNumMap[x.serialNumber], ballot.machinePrecinctNameMap[x.serialNumber]))
                    numOccurrencesWarningMap[x.serialNumber] = 1
            elif x.eventNumber == '0001655':
                if numOccurrencesRecalibrationMap.has_key(x.serialNumber):
                    temp = numOccurrencesRecalibrationMap[x.serialNumber]
                    temp = temp + 1
                    numOccurrencesRecalibrationMap[x.serialNumber] = temp
                else:
                    if not ballot.machinePrecinctNumMap.has_key(x.serialNumber):
                        totalRecalibrationList.append((x.serialNumber, " ", " "))
                    else:
                        totalRecalibrationList.append((x.serialNumber, ballot.machinePrecinctNumMap[x.serialNumber], ballot.machinePrecinctNameMap[x.serialNumber]))
                    numOccurrencesRecalibrationMap[x.serialNumber] = 1
    warningTable = report.Table()
    if len(numOccurrencesWarningMap) < 1:
        warningTable.addRow("This county experienced no callibration problems.")
        #r.addTextBox("This county experienced no callibration problems.")
    else:
        for w in numOccurrencesWarningMap.values():
            avg = avg + w
        avg = avg/len(numOccurrencesWarningMap.values())
        for w2 in numOccurrencesWarningMap.values():
            ssum = ssum + ((w2-avg)**2)
        ssum2 = ssum/len(numOccurrencesWarningMap.values())
        stdev = math.sqrt(ssum2)
        b = True
        for y in numOccurrencesWarningMap:
            if numOccurrencesWarningMap[y] > (avg + (2.5*stdev)):
                for y2 in totalWarningList:
                    if y2[0] == y:
                        if b == True:
                            r.addTextBox("The following machines have an unusually large number of log messages related to an uncalibrated screen.  The meaning of these messages is not documented.  It is possible that they might indicate a problem with the terminal touch screen.  You may wish to check if the machine is calibrated or if the touch screen is in good working condition.")
                            r.addTextBox(" ")
                            b = False
                        warningTable.addRow(["%s (#%s) " % (y2[2], y2[1]), "  %s had %d occurrences of this event." % (y2[0], numOccurrencesWarningMap[y])])
                        #r.addTextBox("%s (#%s)   %s had %d occurrences of this event." % (y2[2], y2[1], y2[0], numOccurrencesWarningMap[y]))
        warningTable2 = report.Table()
        b2 = True
        for z in numOccurrencesWarningMap:
            if numOccurrencesRecalibrationMap.has_key(z):
                if numOccurrencesWarningMap[z] != numOccurrencesRecalibrationMap[z]:
                    for z2 in totalRecalibrationList:
                        for z3 in totalWarningList:
                            if z2[0] == z == z3[0]:
                                if b2 == True:
                                    r.addTextBox(" ")
                                    r.addTextBox("The following machines experienced screen calibration issues and were not always recalibrated.  You may wish to check if the screen is calibrated.")
                                    r.addTextBox(" ")
                                    b2 = False
                                warningTable2.addRow(["%s (#%s) " % (z3[2], z3[1]), "  %s experienced %d events warning about calibration, but it was only recalibrated %d time(s)." % (z3[0], numOccurrencesWarningMap[z], numOccurrencesRecalibrationMap[z])])
                                #r.addTextBox("%s (#%s)   %s experienced %d events warning about calibration, but it was only recalibrated %d time(s)." % (z3[2], z3[1], z3[0], numOccurrencesWarningMap[z], numOccurrencesRecalibrationMap[z]))
            else:
                for z4 in totalWarningList:
                    if z4[0] == z:
                        if b2 == True:
                            r.addTextBox(" ")
                            r.addTextBox("The following machines experienced screen calibration issues and were not always recalibrated.  You may wish to check if the screen is calibrated.")
                            r.addTextBox(" ")
                            b2 = False
                        warningTable2.addRow(["%s (#%s)  " % (z4[2], z4[1]), "  %s experienced %d events warning about calibration, but it was never recalibrated." % (z4[0], numOccurrencesWarningMap[z])])
                        #r.addTextBox("%s (#%s)   %s experienced %d events warning about calibration, but it was never recalibrated." % (z4[2], z4[1], z4[0], numOccurrencesWarningMap[z]))
        r.addTable(warningTable)
        r.addTable(warningTable2)
    return r
                   
def getTerminalClosedEarlyEvents(data, ballot, date, r):
    plt.ioff()
    d = str(date.eday)
    d = d.split("-")
    d2 = d[1]+'/'+d[2]+'/'+d[0]
    r.addTitle('Terminals that were closed early')
    totalEarlyList = []
    for x in data.getEntryList():
        s = x.dateTime.split(" ")
        t = s[1].split(":")
        if t[0] == '':
            continue
        elif stri.atoi(t[0]) > 7 and stri.atoi(t[0]) < 19 and (s[0] == d2):
            if x.eventNumber == '0001628':
                if x.serialNumber not in ballot.earlyVotingList and x.serialNumber not in ballot.failsafeList and ballot.machinePrecinctNumMap.has_key(x.serialNumber):
                    totalEarlyList.append((ballot.machinePrecinctNumMap[x.serialNumber], s[1], x.serialNumber, ballot.machinePrecinctNameMap[x.serialNumber]))
    totalEarlyList.sort()
    earlyTable = report.Table()
    b = True
    if len(totalEarlyList) > 0:
        if b == True:
            r.addTextBox('The following machines recorded at least one log message related to the terminal closing early.  The detailed meaning of this event is not documented.  This may indicate that a rover closed the voting machine early.  You may want to check why the machine was closed early and whether it indicates any kind of problem with the machine that should be addressed before future elections.')
            r.addTextBox(" ")
            b = False
        for y in totalEarlyList:
            earlyTable.addRow(["In %s  (#%s) " % (y[3], y[0]),  "machine %s was closed at %s" % (y[2], y[1])])
            #r.addTextBox("%s (#%s)   %s was closed at %s" % (y[3], y[2], y[0], y[1]))
    else:
        #earlyTable.addRow(["This county experienced no anomalous terminals closing early."])
        #r.addTextBox("This county experienced no anomalous terminals closing early.")
        r.addTextBox("No problems found.")
    r.addTable(earlyTable)
    return r        
   
def getUnknownEvents(data, ballot, date, r):
    d = str(date.eday)
    d = d.split("-")
    d2 = d[1]+'/'+d[2]+'/'+d[0]
    r.addTitle('Terminals with unknown events')
    unknownEvents = ['0001703', '0001704', '0001404']
    totalUnknownEventsMap = {}
    totalUnknownList = []
    totalsMap = {}
    for x in data.getEntryList():
        s = x.dateTime.split(" ")
        if x.eventNumber in unknownEvents and s[0] == d2:
            if totalUnknownEventsMap.has_key(x.serialNumber):
                if totalUnknownEventsMap[x.serialNumber][1].has_key(x.eventNumber):
                    temp = totalUnknownEventsMap[x.serialNumber][1][x.eventNumber]
                    temp = temp + 1
                    totalUnknownEventsMap[x.serialNumber][1][x.eventNumber] = temp
                else:
                    totalUnknownEventsMap[x.serialNumber][1][x.eventNumber] = 1
            else:
                tempMap = {}
                tempMap[x.eventNumber] = 1
                if ballot.machinePrecinctNumMap.has_key(x.serialNumber):
                    totalUnknownEventsMap[x.serialNumber] = ((ballot.machinePrecinctNumMap[x.serialNumber], ballot.machinePrecinctNameMap[x.serialNumber]),tempMap)
    for x2 in totalUnknownEventsMap:
        if x2 in ballot.earlyVotingList or x2 in ballot.failsafeList:
            continue
        else:
            totalUnknownList.append((ballot.machinePrecinctNumMap[x2], ballot.machinePrecinctNameMap[x2], x2))
    totalUnknownList.sort()
    for y in totalUnknownEventsMap:
        if totalsMap.has_key(y):
            for y2 in totalUnknownEventsMap[y][1]:
                totalsMap[y] += totalUnknownEventsMap[y][1][y2]
        else:
            totalsMap[y] = 0
            for y2 in totalUnknownEventsMap[y][1]:
                totalsMap[y] += totalUnknownEventsMap[y][1][y2]
    unknownTable = report.Table()
    if len(totalUnknownEventsMap) < 1:
        #unknownTable.addRow(["This county did not experience any anomalous unknown events."])
        #r.addTextBox("This county did not experience any anomalous unknown events.")
        r.addTextBox("No problems found.")
    else:
        r.addTextBox("The following machines each had at least one unknown warning event.  The unknown warning events have these descriptions: ")
        r.addTextBox(" ")
        r.addTextBox("Warning - no valid term audit data")
        r.addTextBox("Warning - PEB I/O Flag Set")
        r.addTextBox("Warning - I/O Flagged PEB will be used")
        r.addTextBox(" ")
        r.addTextBox("The meanings of these events is not documented.  You may wish to inspect these machines for potential problems.")
        r.addTextBox(" ")
        for z in totalUnknownList:
            unknownTable.addRow(["%s (#%s) " % (z[1], z[0]), "%s has %d total unknown warnings." % (z[2], totalsMap[z[2]])])
            #r.addTextBox("%s (#%s)  %s has %d total unknown warnings." % (totalUnknownEventsMap[z][0][1], totalUnknownEventsMap[z][0][0], z, totalsMap[z])) 
    r.addTable(unknownTable)
    return r
   
def getWarningEvents(data,ballot,r):
    plt.ioff()
    r.addTitle('Detection of Anomalous Warning Events')
    wMap = {}
    wNumMap = {}
    list1628 = []
    list1651 = []
    list1703 = []
    list1704 = []
    list1404 = []
    totalList = []
    minorTicks = (.5,)
    avg = 0
    maxNumOccurrences = 0   
    stdev = 0.00000000
    ssum = 0.00000000
    ssum2 = 0.00000000     
    wEvents = ['0001628', '0001651', '0001703', '0001704']
    for x in data.getEntryList():
        s = x.dateTime.split(" ")
        t = s[1].split(":")
        if t[0] == '':
            continue
        elif stri.atoi(t[0]) > 7 and stri.atoi(t[0]) < 19 and (s[0] == date.eday):
            if x.eventNumber in wEvents:
                if wMap.has_key(x.serialNumber):
                    if wMap[x.serialNumber].has_key(x.eventNumber):
                        temp = wMap[x.serialNumber][x.eventNumber]
                        temp = temp + 1
                        wMap[x.serialNumber][x.eventNumber] = temp
                    else:
                        tempMap = wMap[x.serialNumber]
                        tempMap[x.eventNumber] = 1
                        wMap[x.serialNumber] = tempMap
                else:
                    tempMap = {}
                    tempMap[x.eventNumber] = 1
                    wMap[x.serialNumber] = tempMap
    for y in wMap:
        temp = 0
        for y2 in wMap[y]:
            temp = temp + wMap[y][y2]
        wNumMap[y] = temp
    
    if len(wMap) < 1:
        r.addTextBox("This county experienced no Warning events.")
        #print "This county experienced no 'Warning' events."
    else:
        for z in wMap:
            for z2 in wMap[z]:
                precinctNum = None
                precinctName = None
                if ballot.machinePrecinctNumMap.has_key(z):
                    precinctNum = ballot.machinePrecinctNumMap[z]
                    precinctName = ballot.machinePrecinctNameMap[z]
                elif z in ballot.earlyVotingList:
                    precinctNum = '750'
                    precinctName = 'Absentee'
                elif z in ballot.failsafeList:
                    precinctNum = '850'
                    precinctName = 'Absentee'
                totalList.append((z, precinctNum, precinctName, wMap[z][z2], z2, data.getEventDescription(z2)))
                if wMap[z][z2] > maxNumOccurrences:
                    maxNumOccurrences = wMap[z][z2] 
                if z2 == '0001628':
                    list1628.append(wMap[z][z2])
                elif z2 == '0001651':
                    list1651.append(wMap[z][z2]) 
                elif z2 == '0001703':
                    list1703.append(wMap[z][z2])
                elif z2 == '0001704':
                    list1704.append(wMap[z][z2])
                elif z2 == '0001404':
                    list1404.append(wMap[z][z2])
                    
        for w in totalList:
            avg = avg + w[3]
        avg = avg/len(totalList)
        for w2 in totalList:
            ssum = ssum + ((w2[3]-avg)**2)
        ssum2 = ssum/len(totalList)
        stdev = math.sqrt(ssum2)
        for w3 in totalList:
            if w3[3] >= math.floor(avg + (2.5*stdev)):
                #print w3[3]
                pass
    return r
    
def getVoteCancelledEvents(data,ballot, date, r):
    plt.ioff()
    d = str(date.eday)
    d = d.split("-")
    d2 = d[1]+'/'+d[2]+'/'+d[0]
    r.addTitle('Anomalous vote cancelled events')
    vcMap = {}
    vcNumMap = {}
    list1513 = []
    list1514 = []
    list1515 = []
    list1516 = []
    list1517 = []
    list1518 = []
    list1519 = []
    totalList = []
    minorTicks = (.5,)
    maxNumOccurrences = 0
    avg = 0
    count = 0
    stdev = 0.00000000
    ssum = 0.00000000
    ssum2 = 0.00000000
    vcEvents = ['0001513', '0001514', '0001515', '0001516', '0001517', '0001518', '0001519']
    for x in data.getEntryList():
        s = x.dateTime.split(" ")
        t = s[1].split(":")
        if t[0] == '':
            continue
        if stri.atoi(t[0]) > 7 and stri.atoi(t[0]) < 19 and s[0] == d2:
            if x.eventNumber in vcEvents:
                if vcMap.has_key(x.serialNumber):
                    if vcMap[x.serialNumber].has_key(x.eventNumber):
                        temp = vcMap[x.serialNumber][x.eventNumber]
                        temp = temp + 1
                        vcMap[x.serialNumber][x.eventNumber] = temp
                    else:
                        tempMap = vcMap[x.serialNumber]
                        tempMap[x.eventNumber] = 1
                        vcMap[x.serialNumber] = tempMap
                else:
                    tempMap = {}
                    tempMap[x.eventNumber] = 1
                    vcMap[x.serialNumber] = tempMap
    for y in vcMap:
        temp = 0
        for y2 in vcMap[y]:
            temp = temp + vcMap[y][y2]
        vcNumMap[y] = temp
    #print vcNumMap
    vcTable = report.Table()
    if len(vcMap) < 1:
        #vcTable.addRow(["This county experienced no Vote Cancelled events."])
        r.addTextBox("No problems found.")
    else:
        for z in vcMap:
            for z2 in vcMap[z]:
                precinctNum = None
                precinctName = None
                if ballot.machinePrecinctNumMap.has_key(z):
                    precinctNum = ballot.machinePrecinctNumMap[z]
                    precinctName = ballot.machinePrecinctNameMap[z]
                elif z in ballot.earlyVotingList:
                    precinctNum = '750'
                    precinctName = 'Absentee'
                elif z in ballot.failsafeList:
                    precinctNum = '850'
                    precinctName = 'Absentee'
                totalList.append((precinctNum, z, precinctName, vcMap[z][z2], z2, data.getEventDescription(z2)))
                if vcMap[z][z2] > maxNumOccurrences:
                    maxNumOccurrences = vcMap[z][z2] 
                if z2 == '0001513':
                    list1513.append(vcMap[z][z2])
                elif z2 == '0001514':
                    list1514.append(vcMap[z][z2])
                elif z2 == '0001515':
                    list1515.append(vcMap[z][z2])
                elif z2 == '0001516':
                    list1516.append(vcMap[z][z2])
                elif z2 == '0001517':
                    list1517.append(vcMap[z][z2])
                elif z2 == '0001518':
                    list1518.append(vcMap[z][z2])
                elif z2 == '0001519':
                    list1519.append(vcMap[z][z2])
        for w in totalList:
            avg = avg + w[3]
        avg = avg/len(totalList)
        for w2 in totalList:
            ssum = ssum + ((w2[3]-avg)**2)
        ssum2 = ssum/len(totalList)
        stdev = math.sqrt(ssum2)
        totalList2 = []
        for w3 in totalList:
            if w3[3] > (avg + (4*stdev)):
                totalList2.append(w3)
        totalList2.sort()
        b = True
        b2 = True
        vcTable2 = report.Table()
        b3 = True
        vcTable3 = report.Table()
        b4 = True
        vcTable4 = report.Table()
        b5 = True
        vcTable5 = report.Table()
        b6 = True
        vcTable6 = report.Table()
        b7 = True
        vcTable7 = report.Table()
        for w4 in totalList2:
            if w4[4] == '0001513':
                if b == True:
                    r.addTextBox("The following machines had an unusually large number of votes cancelled due to having the wrong ballot.  You may wish to review this section of the poll worker training manual.")
                    b = False
                #r.addTextBox("Machine %s had %d occurrences (in %s)" % (w4[0], w4[3], w4[2]))
                vcTable.addRow(["In %s, " % (w4[2],), "machine %s had %d vote cancellations." % (w4[1], w4[3])])
                #vcTable.addRow(["Machine %s had %d vote cancellation events  " % (w4[0], w4[3]), " (in %s)." % (w4[2],)])
        r.addTable(vcTable)
        for w4 in totalList2:
            if w4[4] == '0001514':
                if b2 == True:
                    r.addTextBox(" ")
                    r.addTextBox("The following machines had an unusually large number of votes cancelled because the voter left after the ballot was issued.  You may wish to inspect this machine for issues that would cause a voter not to vote.")
                    b2 = False
                #r.addTextBox("Machine %s had %d vote cancellation events (in %s)" % (w4[0], w4[3], w4[2]))
                #vcTable2.addRow(["Machine %s had %d vote cancellation events  " % (w4[0], w4[3]), " (in %s)." % (w4[2],)])
                vcTable2.addRow(["In %s, " % (w4[2],), "machine %s had %d vote cancellations." % (w4[1], w4[3])])
        r.addTable(vcTable2)
        for w4 in totalList2:
            if w4[4] == '0001515':
                if b3 == True:
                    r.addTextBox(" ")
                    r.addTextBox("The following machines had an unusually large number of votes cancelled because the voter left before the ballot was issued.  You may wish to inspect this machine for issues that would cause a voter not to vote.")
                    b3 = False
                #r.addTextBox("Machine %s had %d vote cancellation events (in %s)" % (w4[0], w4[3], w4[2]))
                #vcTable3.addRow(["Machine %s had %d vote cancellation events  " % (w4[0], w4[3]), " (in %s)." % (w4[2],)])
                vcTable3.addRow(["In %s, " % (w4[2],), "machine %s had %d vote cancellations." % (w4[1], w4[3])])
        r.addTable(vcTable3)
        for w4 in totalList2:
            if w4[4] == '0001516':
                if b4 == True:
                    r.addTextBox(" ")
                    r.addTextBox("The following machines had an unusually large number of votes cancelled by a voter.  You may wish to inspect this machine for issues that would cause a voter not to vote.")
                    b4 = False
                #r.addTextBox("Machine %s had %d vote cancellation events (in %s)" % (w4[0], w4[3], w4[2]))
                #vcTable4.addRow(["Machine %s had %d vote cancellation events  " % (w4[0], w4[3]), " (in %s)." % (w4[2],)])
                vcTable4.addRow(["In %s, " % (w4[2],), "machine %s had %d vote cancellations." % (w4[1], w4[3])])
        r.addTable(vcTable4)
        for w4 in totalList2:
            if w4[4] == '0001517':
                if b5 == True:
                    r.addTextBox(" ")
                    r.addTextBox("The following machines had an unusually large number of votes cancelled due to a printer problem.  You may wish to inspect the machine for potential problems.  ")
                    b5 = False
                #r.addTextBox("Machine %s had %d vote cancellation events (in %s)" % (w4[0], w4[3], w4[2]))
                #vcTable5.addRow(["Machine %s had %d vote cancellation events  " % (w4[0], w4[3]), " (in %s)." % (w4[2],)])
                vcTable5.addRow(["In %s, " % (w4[2],), "machine %s had %d vote cancellations." % (w4[1], w4[3])])
        r.addTable(vcTable5)
        for w4 in totalList2:
            if w4[4] == '0001518':
                if b6 == True:
                    r.addTextBox(" ")
                    r.addTextBox("The following machines had an unusually large number of votes cancelled due to a terminal problem.  You may wish to inspect the machine for potential problems.  ")
                    b6 = False
                #r.addTextBox("Machine %s had %d vote cancellation events (in %s)" % (w4[0], w4[3], w4[2]))
               # vcTable6.addRow(["Machine %s had %d vote cancellation events  " % (w4[0], w4[3]), " (in %s)." % (w4[2],)])
                vcTable6.addRow(["In %s, " % (w4[2],), "machine %s had %d vote cancellations." % (w4[1], w4[3])])
        r.addTable(vcTable6)
        for w4 in totalList2:
            if w4[4] == '0001519':
                if b7 == True:
                    r.addTextBox(" ")
                    r.addTextBox("The following machines had an unusually large number of votes cancelled for an unknown reason.  You may wish to consult with the poll workers and maintenance staff at the following precincts.  ")
                    b7 = False
                #r.addTextBox("Machine %s had %d vote cancellation events (in %s)" % (w4[0], w4[3], w4[2]))
                #vcTable7.addRow(["Machine %s had %d vote cancellation events  " % (w4[0], w4[3]), " (in %s)." % (w4[2],)])
                vcTable7.addRow(["In %s, " % (w4[2],), "machine %s had %d vote cancellations." % (w4[1], w4[3])])
        r.addTable(vcTable7)
        avg2 = 0
        ssum3 = 0.00000000
        ssum4 = 0.00000000
        stdev2 = 0.00000000
        for w in vcNumMap.values():
            avg2 = avg2 + w
        avg2 = avg2/len(vcNumMap.values())
        for w2 in vcNumMap.values():
            ssum3 = ssum3 + ((w2-avg2)**2)
        ssum4 = ssum3/len(vcNumMap.values())
        stdev2 = math.sqrt(ssum4)   
        outliers = []
        for u in vcNumMap:
            if vcNumMap[u] > (3*stdev2):
                if ballot.machinePrecinctNameMap.has_key(u):
                    outliers.append((ballot.machinePrecinctNumMap[u], u, ballot.machinePrecinctNameMap[u], vcNumMap[u]))     
        outliers.sort()
        b8 = True
        vcTable8 = report.Table()
        for w5 in outliers:
            if b8 == True:
                r.addTextBox(" ")
                r.addTextBox("The following machines had an unusually large number of vote cancellations in total.")  
                b8 = False  
            #r.addTextBox("Machine %s had %d vote cancellation events (in %s)." % (w5[0], w5[2], w5[1]))
            #vcTable8.addRow(["Machine %s had %d vote cancellation events " % (w5[0], w5[2]), " (in %s)." % (w5[1],)])
            vcTable8.addRow(["In %s, " % (w5[2],), "machine %s had %d vote cancellations." % (w5[1], w5[3])])
        r.addTable(vcTable8)
    return r
