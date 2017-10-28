from Tkinter import *
import datetime       #Get/Manipulate Dates and Times
import os             #Examine file structure
import pickle         #Save and load variables
import events         #Event class variables (user-created)
import sys  	      #Raise errors
import copy


class Application:

	def __init__(self,master,eventList,fileSaveInfo,reminders):

		for i in range(len(eventList)):
			eventList[i].evUpdate()
		self.eventList = eventList
		self.fileSaveInfo = fileSaveInfo
		self.reminders = reminders

		curTime = datetime.datetime.now()
		self.firstTime = datetime.datetime( curTime.year , curTime.month , curTime.day, 0,0,0,0)
		self.lastTime  = self.firstTime + datetime.timedelta(7)

		self.drawCalendar(master)
		self.populateCalendar()

		self.sortEventList()
		self.list48hrEvents()

	def printCurrentTime(self):
		curTime = datetime.datetime.now()
		[curHr,curAP] = self.conv24hrToAP(curTime.hour)
		print '\n'+'It is '+curHr.rjust(2)+':'+str(curTime.minute).zfill(2)+' '+curAP+' on '+self.wdInt2Str(curTime.weekday())+', '+str(curTime.month).rjust(2)+'/'+str(curTime.day).zfill(2)+'\n'

	def sortEventList(self):
		eventList = self.eventList
		eStartTimes = [] #List of eventStart times
		sortEventList = copy.deepcopy(eventList) #Sorted event list

		#Populate event start times
		for i in range(len(eventList)):
			eStartTimes.append(eventList[i].startTime)
		eStartTimes.sort()

		#Sort event list
		for i in range(len(eStartTimes)):
			for j in range(len(eventList)):
				if eStartTimes[i] == eventList[j].startTime:
					sortEventList[i] = eventList[j]
					break
			else:
				print 'Error in sorting events'
				sys.exit()
		self.eventList = sortEventList

	def addEventFromPresent(self):

		#User Input
		stayInLoop = True
		while stayInLoop:

			#Find next available free time
			curTime = datetime.datetime.now()
			[startFree,endFree,noMoreSched] = self.findFreeTime(curTime)
			if not noMoreSched:
				freeTime = endFree-startFree
				[freeHours,freeMinutes] = self.dtMinHr(freeTime)

			[prHr,prAP] = self.conv24hrToAP(startFree.hour)
			print '\nNext available free time......'+str(startFree.month)+'/'+str(startFree.day)+', '+str(prHr)+':'+str(startFree.minute)+' '+prAP
			if not noMoreSched:
				print str(freeHours)+' hours and '+str(freeMinutes)+' minutes are available before next event'
			else:
				print '-No events are scheduled after this time.'

			usrIn = raw_input('\nEnter "s" to schedule an event, or "r" to return to the main menu: \n')
			if usrIn=='s':
				eventName = raw_input('Enter the event name: \n')
				stay2 = True
				while stay2:
					#Prompt
					if not noMoreSched:
						durHr   = raw_input('XX hrs, 00 min - Please enter duration hours, or enter "f" to fill the available free time: \n')
					else:
						durHr   = raw_input('XX hrs, 00 min - Please enter duration hours: \n')

					#Deal with input
					if durHr == 'f' and not noMoreSched:
						eventDuration = freeTime
						stay2 = False
					elif durHr == 'f' and noMoreSched:
						print 'Cannot fill free time; nothing is scheduled after the present time'
					elif durHr.isdigit() and int(durHr)>=0 and int(durHr)<=23:
						durMi   = self.solicitInput(str(durHr)+' hrs, XX min - Please enter duration minutes: \n','miDur')
						eventDuration  = datetime.timedelta(0,0,0,0,int(durMi),int(durHr))
						stay2 = False
					else:
						print 'Input not recognized'
				newEvent = events.Event(eventName ,datetime.datetime.now())
				newEvent.setStartDur(startFree,eventDuration)
				self.printEvent(newEvent)
				self.updateTime()
				self.eventList.append(newEvent)
				self.sortEventList()
				self.unsavedChanges = True
			elif usrIn=='r':
				print 'Return to main menu'
				stayInLoop = False
			else:
				print 'Input not recognized'

	def dtMinHr(self,dt):
		hours = dt.days*24 + dt.seconds/3600
		minutes = dt.seconds/60.0 - (dt.seconds/3600)*60
		#Validate
		totSec1 = dt.days*24*3600+dt.seconds
		totSec2 = hours*3600.0 + minutes*60.0
		if totSec1 != totSec2:
			print 'Time conversion error'
			sys.exit()
		minutes = round(minutes)
		return hours,minutes
			 

	def findFreeTime(self,checkTime): #Finds the first unscheduled period after checkTime

		inEventFlag = False
		
		noMoreScheduled = False
		#Checks to see if the given time is during a scheduled event
		for i in range(len(self.eventList)):
			ev = self.eventList[i]
			if checkTime>ev.startTime and checkTime>ev.stopTime:
				pass
			elif checkTime>=ev.startTime and checkTime<ev.stopTime:
				#In an event, go to in event loop
				inEventFlag = True
				break
			elif checkTime<ev.startTime:
				#Before an event, can define free time
				startFreeTime = checkTime
				endFreeTime   = ev.startTime
				break
		else: #Current time is after all events
			startFreeTime = checkTime
			endFreeTime   = datetime.datetime.max()
			noMoreScheduled = True


		if inEventFlag: #The given time IS during a scheduled event; steps forward until unscheduled time is found
			lenEvents = len(self.eventList)-1
			while i<=lenEvents-1 and self.eventList[i].stopTime>=self.eventList[i+1].startTime:
				i=i+1

			startFreeTime = self.eventList[i].stopTime
			if   i<lenEvents:
				endFreeTime = self.eventList[i+1].startTime
			elif i==lenEvents:
				endFreeTime    = datetime.datetime.max
				noMoreScheduled = True

		return startFreeTime,endFreeTime,noMoreScheduled		

	def populateCalendar(self):
		for i in range(len(self.eventList)):
			self.printEvent(self.eventList[i])
		
		#Draw line at current time
		curTime = datetime.datetime.now()
		[lb,rb,sb,eb] = self.getCalCoords(curTime,curTime+datetime.timedelta(0,1))
		self.tLine = Label(self.frame,bg='yellow',text='')
		self.curTimeLine = self.calSpace.create_window(lb,sb,height=3,width=(rb-lb),window=self.tLine,anchor=NW)
		self.tLine.lift()


	def getCalCoords(self,startT,endT):
		if startT.day != endT.day:
			print startT
			print endT
			print "Invalid cal coords"
			sys.exit()
		timeFromStart = startT-self.firstTime
		
		lb = 100*(timeFromStart.days+0)
		rb = 100*(timeFromStart.days+1)
		sb = (startT.hour/24.0 + startT.minute/(24.0*60.0))*600
		eb = (endT.hour  /24.0 + endT.minute  /(24.0*60.0))*600
		return lb,rb,sb,eb

	def updateTime(self):
		curTime = datetime.datetime.now()
		[lb,rb,sb,eb] = self.getCalCoords(curTime,curTime+datetime.timedelta(0,1))
		self.calSpace.coords(self.curTimeLine,lb,sb)
		self.tLine.lift()

	def assignEventColor(self,event):
		if 'sleep' in event.name or 'Sleep' in event.name:
			evColor = 'gray'
		elif 'transit' in event.name or 'Transit' in event.name or 'drive ' in event.name or 'Drive ' in event.name or 'go to' in event.name or 'Go to' in event.name or 'Walk to' in event.name or 'walk to' in event.name or 'walk home' in event.name or 'Walk home' in event.name:
			evColor = 'orange'
		elif 'eat' in event.name or 'Eat' in event.name or event.name=='Dinner' or event.name=='dinner' or event.name=='breakfast' or event.name == 'Breakfast' or event.name == 'lunch' or event.name == 'Lunch':
			evColor = 'red'
		else:
			evColor = 'blue'
		return evColor		

	def printEvent(self,event):
		oneSecond = datetime.timedelta(0,1)
		oneDay    = datetime.timedelta(1)	
		printName = event.name+', '+event.durString
		evColor = self.assignEventColor(event)		
		if event.startTime > self.firstTime and event.stopTime < self.lastTime: #Event is wholly on calendar
			nextDay = event.startTime + oneDay
			nextDayMidnight = datetime.datetime(nextDay.year , nextDay.month , nextDay.day , 0,0,0,0)
			if event.startTime.day == event.stopTime.day or event.stopTime.day == nextDayMidnight: #Event is contained in one day
				[lb,rb,sb,eb] = self.getCalCoords(event.startTime,event.stopTime)
				eventWin = Label(self.frame,fg="white",bg=evColor,wraplength=100-2*self.txBuf,text=printName,anchor=NW,relief=RAISED,borderwidth=2,justify=LEFT)
				self.calSpace.create_window(lb,sb,height=(eb-sb),width=(rb-lb),window=eventWin,anchor=NW)
			elif event.stopTime.day == nextDayMidnight.day: #Event straddles a day
				[lb,rb,sb,eb] = self.getCalCoords(event.startTime,nextDayMidnight-oneSecond)
				eventWin = Label(self.frame,fg="white",bg=evColor,wraplength=100-2*self.txBuf,text=printName,anchor=NW,relief=RAISED,borderwidth=2,justify=LEFT)
				self.calSpace.create_window(lb,sb,height=(eb-sb),width=(rb-lb),window=eventWin,anchor=NW)			
				[lb,rb,sb,eb] = self.getCalCoords(nextDayMidnight,event.stopTime)
				eventWin = Label(self.frame,fg="white",bg=evColor,wraplength=100-2*self.txBuf,text=printName,anchor=NW,relief=RAISED,borderwidth=2,justify=LEFT)
				self.calSpace.create_window(lb,sb,height=(eb-sb),width=(rb-lb),window=eventWin,anchor=NW)
			else:
				print "Event is too long, see printEvent function"
				sys.exit()
		
		elif event.startTime < self.firstTime and event.stopTime > self.firstTime: #Start is cut off
			[lb,rb,sb,eb] = self.getCalCoords(self.firstTime,event.stopTime)
			eventWin = Label(self.frame,fg="white",bg=evColor,wraplength=100-2*self.txBuf,text=printName,anchor=NW,relief=RAISED,borderwidth=2,justify=LEFT)
			self.calSpace.create_window(lb,sb,height=(eb-sb),width=(rb-lb),window=eventWin,anchor=NW)
	
		elif event.startTime < self.lastTime  and event.stopTime > self.lastTime: #Stop is cut off
			[lb,rb,sb,eb] = self.getCalCoords(event.startTime,self.lastTime-oneSecond)
			eventWin = Label(self.frame,fg="white",bg=evColor,wraplength=100-2*self.txBuf,text=printName,anchor=NW,relief=RAISED,borderwidth=2,justify=LEFT)
			self.calSpace.create_window(lb,sb,height=(eb-sb),width=(rb-lb),window=eventWin,anchor=NW)

	def drawCalendar(self,master):

		self.windHeight = 700
		self.windWidth  = 1200
		self.butHeight  = 50
		self.butWidth   = 100
		self.txBuf = 5

		self.unsavedChanges = False
		self.mstk = master
    
		master.minsize(width=self.windWidth,height=self.windHeight)

		self.frame = Frame(master)
		self.frame.place(height=self.windHeight,width=self.windWidth)

		self.calHeight = 600;
		self.calWidth  = 700;

		self.remWinWid = 350;
		self.remWinHgt = 175;

		self.butW = self.calWidth+100+25
		self.butN = 50

		self.calSpace = Canvas(self.frame, width = 700, height = self.calHeight)
		self.calSpace.place(x=100,y=50,anchor=NW)

		self.calSpace.create_rectangle(0,0,700,600, fill="black")
		#Day Dividers
		for x in range(0,800,100):
			self.calSpace.create_line(x,0,x,self.calHeight,fill="white")
		#Time Labels
		#Num day divisions = 8, pxIncrement = height/numDiv = 600/8 = 75
		y1 = 50; self.calTop = y1
		y2 = 125
		y3 = 200
		y4 = 275
		y5 = 350
		y6 = 425
		y7 = 500
		y8 = 575
		y9 = 650
		t1 = Label(self.frame,text="12:00 a.m.")
		t1.place(x=100,y=y1 ,anchor=E)
		L1 = self.calSpace.create_line(0,y1-50,self.calWidth,y1-50,fill="white",dash=(4,4))
		t2 = Label(self.frame,text="3:00 a.m.")
		t2.place(x=100,y=y2 ,anchor=E)
		L2 = self.calSpace.create_line(0,y2-50,self.calWidth,y2-50,fill="white",dash=(4,4))
		t3 = Label(self.frame,text="6:00 a.m.")
		t3.place(x=100,y=y3 ,anchor=E)
		L3 = self.calSpace.create_line(0,y3-50,self.calWidth,y3-50,fill="white",dash=(4,4))
		t4 = Label(self.frame,text="9:00 a.m.")
		t4.place(x=100,y=y4 ,anchor=E)
		L4 = self.calSpace.create_line(0,y4-50,self.calWidth,y4-50,fill="white",dash=(4,4))
		t5 = Label(self.frame,text="12:00 p.m.")
		t5.place(x=100,y=y5 ,anchor=E)
		L6 = self.calSpace.create_line(0,y5-50,self.calWidth,y5-50,fill="white",dash=(4,4))
		t6 = Label(self.frame,text="3:00 p.m.")
		t6.place(x=100,y=y6 ,anchor=E)
		L6 = self.calSpace.create_line(0,y6-50,self.calWidth,y6-50,fill="white",dash=(4,4))
		t7 = Label(self.frame,text="6:00 p.m.")
		t7.place(x=100,y=y7 ,anchor=E)
		L7 = self.calSpace.create_line(0,y7-50,self.calWidth,y7-50,fill="white",dash=(4,4))
		t8 = Label(self.frame,text="9:00 p.m.")
		t8.place(x=100,y=y8 ,anchor=E)
		L8 = self.calSpace.create_line(0,y8-50,self.calWidth,y8-50,fill="white",dash=(4,4))
		t9 = Label(self.frame,text="12:00 a.m.")
		t9.place(x=100,y=y9 ,anchor=E)
		L9 = self.calSpace.create_line(0,y9-50,self.calWidth,y9-50,fill="white",dash=(4,4))

		#Draw day labels
		self.dayLab = []
		self.drawDayLabels(self.firstTime)
		
		unsavedChanges = False;

		addB = Button(self.frame, text="Add Event", command=self.addEvent,wraplength=self.butWidth-2*self.txBuf)
		addB.place(height=self.butHeight,anchor=NW,x=self.butW+0*self.butWidth,y=self.butN+1*self.butHeight,width=self.butWidth)

		editB = Button(self.frame, text="Edit Event", command=self.editEvent,wraplength=self.butWidth-2*self.txBuf)
		editB.place(height=self.butHeight,anchor=NW,x=self.butW+1*self.butWidth,y=self.butN+3*self.butHeight,width=self.butWidth)

		saveB = Button(self.frame, text="Save Calendar", command=self.saveCal,wraplength=self.butWidth-2*self.txBuf)
		saveB.place(height=self.butHeight,anchor=NW,x=self.butW+2*self.butWidth,y=self.butN+2*self.butHeight,width=self.butWidth)

		exitB = Button(self.frame, text='Exit Calendar', command=self.exitCal,wraplength=self.butWidth-2*self.txBuf)
		exitB.place(height=self.butHeight,anchor=NW,x=self.butW+2*self.butWidth,y=self.butN+3*self.butHeight,width=self.butWidth)

		updaB = Button(self.frame, text='Update Current Time', command=self.updateTime,wraplength=self.butWidth-2*self.txBuf)
		updaB.place(height=self.butHeight,anchor=NW,x=self.butW+2*self.butWidth,y=self.butN+0*self.butHeight,width=self.butWidth)

		delB = Button(self.frame, text='Delete Event', command=lambda: self.deleteEvent(master),wraplength=self.butWidth-2*self.txBuf)
		delB.place(height=self.butHeight,anchor=NW,x=self.butW+0*self.butWidth,y=self.butN+2*self.butHeight,width=self.butWidth)

		qaB = Button(self.frame, text='Add Events from Present', command=self.addEventFromPresent,wraplength=self.butWidth-2*self.txBuf)
		qaB.place(height=self.butHeight,anchor=NW,x=self.butW+0*self.butWidth,y=self.butN+0*self.butHeight,width=self.butWidth)

		adrB = Button(self.frame, text='Add Reminders', command=self.addReminder,wraplength=self.butWidth-2*self.txBuf)
		adrB.place(height=self.butHeight,anchor=NW,x=self.butW+1*self.butWidth,y=self.butN+0*self.butHeight,width=self.butWidth)

		derB = Button(self.frame, text='Delete Reminders', command=self.deleteReminder,wraplength=self.butWidth-2*self.txBuf)
		derB.place(height=self.butHeight,anchor=NW,x=self.butW+1*self.butWidth,y=self.butN+1*self.butHeight,width=self.butWidth)

		recB = Button(self.frame, text='Add Recurring Event', command=self.recurringEventAdd,wraplength=self.butWidth-2*self.txBuf)
		recB.place(height=self.butHeight,anchor=NW,x=self.butW+0*self.butWidth,y=self.butN+3*self.butHeight,width=self.butWidth)

		recB = Button(self.frame, text='List 48 Hrs', command=self.list48hrEvents,wraplength=self.butWidth-2*self.txBuf)
		recB.place(height=self.butHeight,anchor=NW,x=self.butW+1*self.butWidth,y=self.butN+2*self.butHeight,width=self.butWidth)

		nexDayB = Button(self.frame, text='->', command=lambda: self.showNextDay(master),wraplength=(self.butWidth-2*self.txBuf)/2)
		nexDayB.place(height=self.butHeight,anchor=NW,x=self.butW+0*self.butWidth+self.butWidth/2,y=self.butN+4*self.butHeight,width=self.butWidth/2)

		prvDayB = Button(self.frame, text='<-', command=lambda: self.showPrevDay(master),wraplength=(self.butWidth-2*self.txBuf)/2)
		prvDayB.place(height=self.butHeight,anchor=NW,x=self.butW+0*self.butWidth,y=self.butN+4*self.butHeight,width=self.butWidth/2)


		self.remTxt = StringVar()
		eventWin = Label(self.frame,fg="white",bg="black",wraplength=self.remWinWid-2*self.txBuf,textvariable=self.remTxt,anchor=NW,justify=LEFT)
		eventWin.place(height=self.remWinHgt,width=self.remWinWid,anchor=NW,x=self.butW, y=9.5*self.butHeight)
		self.updateRemText()

	def showNextDay(self,master):
		oneDay = datetime.timedelta(1)
		self.firstTime = self.firstTime + oneDay
		self.lastTime  = self.lastTime  + oneDay
		self.drawCalendar(master)
		self.populateCalendar()

	def showPrevDay(self,master):
		oneDay = datetime.timedelta(1)
		self.firstTime = self.firstTime - oneDay
		self.lastTime  = self.lastTime  - oneDay
		self.drawCalendar(master)
		self.populateCalendar()

	def recurringEventAdd(self):

		eventName = raw_input('Enter the event name: \n')

		#Recurrence
		curTime = datetime.datetime.now()
		thisYear = curTime.year
		stayInLoop = True

		while stayInLoop: #Establish recurrence period (in days)
			usrStr = raw_input('Select recurrence frequency:\n"w" for a weekly event\n"d" for a daily event\n')
			if usrStr == 'w':
				recurPeriod = 7
				stayInLoop = False
			elif usrStr == 'd':
				recurPeriod = 1
				stayInLoop = False
			else:
				print 'Input not recognized'

		stayInLoop = True
		while stayInLoop: #Establish recurrence duration
			usrStr = raw_input('Specify recurrence period:\n"fn" to select first date and number of occurences\n"fe" to select first date and end date\n')
			if usrStr == 'fn' or 'fe': 
				startMo = self.solicitInput('XX/01/'+str(thisYear)+' - First event start month: \n','mo')
				startDa = self.solicitInput(str(startMo)+'/XX/'+str(thisYear)+' - First event start day: \n','da')
				print str(startMo)+'/'+str(startDa)+'/'+str(thisYear)
				startDate = datetime.date(thisYear,startMo,startDa)
				stayInLoop = False
			else:
				print 'Input not recognized'
		if usrStr == 'fn':
			stayInLoop = True
			while stayInLoop:
				numOccur = raw_input('Enter number of occurences:\n')
				if numOccur.isdigit() and int(numOccur)>0:
					stayInLoop = False
				else:
					print 'Number of occurences must be an integer greater than zero'
				numOccur = int(numOccur)			
		elif usrStr == 'fe':
			stayInLoop = True
			while stayInLoop:
				endMo = self.solicitInput('XX/01/'+str(thisYear)+' - Recurrence end month: \n','mo')
				endDa = self.solicitInput(str(startMo)+'/XX/'+str(thisYear)+' - Recurrence end day: \n','da')
				endDate   = datetime.date(thisYear,endMo,endDa)
				delt = endDate-startDate
				daySpan = delt.days
				if daySpan>0:
					numOccur = (daySpan/recurPeriod)+1
					stayInLoop = False
				else:
					print 'Recurrence end date must be after recurrence start date (after '+str(startMo)+'/'+str(startDa)+'/'+str(thisYear)
		
		print '\nRecurrence established\n'
		stayInLoop = True
		print 'Get time of day'
		#Time of day
		while stayInLoop:
			enterMethod = raw_input('Please enter:\n"sd" to specify start and duration, or \n"ed" to specify end and duration \n')			
			if enterMethod == "sd":

				startHr = self.solicitInput('XX:00 a.m. - Enter event start hour: \n','hr')
				startMi = self.solicitInput(str(startHr)+':XX a.m. - Enter event start minute: \n','mi')
				startAP = self.solicitInput(str(startHr)+':'+str(startMi)+' X.m. - Enter "a" for "a.m." or "p" for "p.m.": \n','ap')
				print str(startHr)+':'+str(startMi)+' '+startAP+'.m.'

				startHr = self.convAPto24hr(startHr,startAP)

				durHr   = self.solicitInput('XX hrs, 00 min - Please enter duration hours: \n','hrDur')
				durMi   = self.solicitInput(str(durHr)+' hrs, XX min - Please enter duration minutes: \n','miDur')

				stdt = datetime.datetime(thisYear,startMo,startDa,startHr,startMi)
				drdt = datetime.timedelta(0,0,0,0,durMi,durHr)

				stayInLoop = False

			elif enterMethod == "ed":

				endHr = self.solicitInput('XX:00 a.m. - Enter event end hour: \n','hr')
				endMi = self.solicitInput(str(endHr)+':XX a.m. - Enter event end minute: \n','mi')
				endAP = self.solicitInput(str(endHr)+':'+str(endMi)+' X.m. - Enter "a" for "a.m." or "p" for "p.m.": \n','ap')
				print str(endHr)+':'+str(endMi)+' '+endAP+'.m.'

				endHr   = self.convAPto24hr(endHr  ,endAP  )

				durHr   = self.solicitInput('XX hrs, 00 min - Please enter duration hours: \n','hrDur')
				durMi   = self.solicitInput(str(durHr)+' hrs, XX min - Please enter duration minutes: \n','miDur')

				eddt = datetime.datetime(thisYear,startMo,startDa,endHr  ,endMi)
				drdt = datetime.timedelta(0,0,0,0,durMi,durHr)
				stdt = eddt - drdt
				if stdt.day != eddt.day:
					stdt = stdt + datetime.timedelta(eddt.day-stdt.day)

				stayInLoop = False

			else:
				print "Input not recognized"

		#Establish recurring events
		recPer = datetime.timedelta(recurPeriod)		
		while numOccur>0:
			newEvent = events.Event(eventName ,datetime.datetime.now())
			newEvent.setStartDur(stdt,drdt)

			self.printEvent(newEvent)
			self.eventList.append(newEvent)
			
			stdt = stdt+recPer
			numOccur = numOccur-1
			
		self.unsavedChanges = True
		self.updateTime()
		self.sortEventList()
		print 'Recurring Event Added!'	

	def updateRemText(self):
		rTxt = 'Reminders:\n'
		for r in self.reminders:
			rTxt = rTxt+'-'+r+'\n'
		self.remTxt.set(rTxt)

	def addReminder(self):
		stayInLoop = True
		while stayInLoop:
			rem = raw_input('Enter reminder text, or enter "c" to return to main menu:\n')
			if rem == 'c':
				print 'Action Completed'
				stayInLoop = False
			else:
				sil2 = True
				while sil2:
					usrStr = raw_input('Enter "y" to keep reminder text or "r" to reenter text:\n')
					if usrStr == 'y':
						self.reminders.append(rem)
						self.unsavedChanges = True
						self.updateRemText()
						print "Reminder Added!"
						sil2 = False
					elif usrStr == 'r':
						sil2 = False
					else: 
						print "Input not recognized"

	def deleteReminder(self):
		stayInLoop = True
		while stayInLoop:			
			print 'Which reminder would you like to delete? Options are: \n'
			for i in range(len(self.reminders)):
				print 'Reminder #'+str(i)+'... '+self.reminders[i]

			delInt = raw_input('\n Enter reminder number to be deleted, or "f" to finish deleting:\n')
			if delInt == 'f':
				stayInLoop = False
				print 'Action Completed'
			elif delInt.isdigit() and int(delInt)>=0 and int(delInt) <=len(self.reminders)-1:
				delInt = int(delInt)
				del self.reminders[delInt]
				self.updateRemText()
				print 'Reminder Deleted'
				self.unsavedChanges = True
			else:
				print 'Input not recognized'
		

	def conv24hrToAP(self,hour):
		if int(hour)==0:
			evHr = '12'
			evAP = 'a.m.'
		elif int(hour)>0 and int(hour)<12:
			evHr = str(hour)
			evAP = 'a.m.'
		elif int(hour)==12:
			evHr = '12'
			evAP = 'p.m.'
		elif int(hour)>12 and int(hour)<24:
			evHr = str(hour-12)
			evAP = 'p.m.'
		else:
			print 'Unexpected entry'
			print hour
			sys.exit()
		return evHr,evAP

	def deleteEvent(self,master):
		stayInLoop = True
		srchString = raw_input('Search for events by title: \n')
		while stayInLoop:			
			
			eventInd = self.searchEvents(srchString)
			print 'Which event would you like to delete? Options are: \n'
			for i in range(len(eventInd)):
				ei   = eventInd[i]
				evnt = self.eventList[ei]
				if int(evnt.startTime.hour)==0:
					evHr = '12'
					evAP = 'a.m.'
				elif int(evnt.startTime.hour)>0 and int(evnt.startTime.hour)<12:
					evHr = str(evnt.startTime.hour)
					evAP = 'a.m.'
				elif int(evnt.startTime.hour)==12:
					evHr = '12'
					evAP = 'p.m.'
				elif int(evnt.startTime.hour)>12 and int(evnt.startTime.hour)<24:
					evHr = str(evnt.startTime.hour-12)
					evAP = 'p.m.'
				print 'Event #'+str(i)+'... '+str(evnt.name)+', starting at '+evHr+':'+str(evnt.startTime.minute)+' on '+evnt.startWD+', '+str(evnt.startTime.month)+'/'+str(evnt.startTime.day)
			delInt = raw_input('\n Enter event number to be deleted, or "f" to finish deleting:\n')
			if delInt == 'f':
				stayInLoop = False
				print 'Action Completed'
			elif delInt.isdigit() and int(delInt)>=0 and int(delInt) <=len(eventInd)-1:
				delInt = int(delInt)
				del self.eventList[eventInd[delInt]]
				self.drawCalendar(master)
				self.populateCalendar()
				print 'Event Deleted'
				self.unsavedChanges = True
			else:
				print 'Input not recognized'

	def list48hrEvents(self):
		#Lists events of the following 48 hrs
		#Find current event
		i=0
		firstEventFound = False
		lastEventFound  = False
		nDays = 2
		curTime = datetime.datetime.now()
		lasTime = curTime + datetime.timedelta(nDays)
		while i<len(self.eventList) and (not firstEventFound or not lastEventFound):
			ev = self.eventList[i]
			if ev.stopTime > curTime and not firstEventFound: #Found first event: Event stops after current time
				firstEvInd = i					
				firstEventFound = True
			if ev.startTime > lasTime and not lastEventFound: #Found last event: Event starts after search period
				lastEvInd = i-1
				if lastEvInd == -1: #If no events start in the 48 hour period
					lastEvInd = 0
				lastEventFound = True
			if i==len(self.eventList)-1 and not lastEventFound and firstEventFound: #Found last event: Reached end of list
				lastEvInd = i	
				lastEventFound = True	
			i=i+1
		evList = self.eventList[firstEvInd:lastEvInd+1]
		titleLen = 0
		for ev in evList:
			titleLen = max(len(ev.name),titleLen)
		titleLen = titleLen+3
		self.printCurrentTime()
		print 'The following events are planned over the next '+str(nDays*24)+' hours:'
		for i in range(len(evList)):
			evnt = evList[i]
			[sevHr,sevAP] = self.conv24hrToAP(evnt.startTime.hour)
			[eevHr,eevAP] = self.conv24hrToAP(evnt.stopTime.hour)
			prntTit = self.dotPad(evnt.name,titleLen)
			print prntTit+' '+sevHr.rjust(2)+':'+str(evnt.startTime.minute).zfill(2)+' '+sevAP+'-'+eevHr.rjust(2)+':'+str(evnt.stopTime.minute).zfill(2)+' '+eevAP+', '+str(evnt.startTime.month).rjust(2)+'/'+str(evnt.startTime.day).zfill(2)+' ('+evnt.startWD+')'

	def dotPad(self,string,strLen):
		nDots = strLen-len(string)
		if nDots>0:
			pad = '.'*nDots
			retStr = string+pad
		else:
			retStr = string[0:strLen+1]
		return retStr		
		

	def searchEvents(self,srchString):

		evInd = []
		for i in range(len(self.eventList)):
			if srchString in self.eventList[i].name:
				evInd.append(i)
		return evInd


	def drawDayLabels(self,firstDay):
		
		for i in range(0,7):
			newDay = firstDay + datetime.timedelta(i)
			#Create string
			#	Get weekday
			wkDay = newDay.weekday()
			wkDay = self.wdInt2Str(wkDay)
			tdTxt = wkDay+'\n'+str(newDay.month) + '/' + str(newDay.day)
			#Add to list
			self.dayLab.append( Label(self.frame,text=tdTxt) )
			#Place on calendar
			self.dayLab[i].place(x=150+self.calWidth*i/7,y=self.calTop,anchor=S)

	def wdInt2Str(self,wDayInt):
		if wDayInt == 0:
			wDayStr = 'Monday'
		elif wDayInt == 1:
			wDayStr = 'Tuesday' 
		elif wDayInt == 2:
			wDayStr = 'Wednesday'
		elif wDayInt == 3:
			wDayStr = 'Thursday' 
		elif wDayInt == 4:
			wDayStr = 'Friday'
		elif wDayInt == 5:
			wDayStr = 'Saturday' 
		elif wDayInt == 6:
			wDayStr = 'Sunday'
		else:
			print 'Bad weekday integer'
		return wDayStr
		



	def solicitInput(self,displayString,valType):
		goodInput = False
		while not goodInput:
			userDat = raw_input(displayString)
			[goodInput,userDat] = self.validateEntry(valType,userDat)
			if not goodInput:
				print "\n*******Invalid Entry*******\n"
		return userDat

	def validateEntry(self,valType,valData):
		#Val type:
			#ap: a.m. or p.m., entry must be "a" or "p"
			#mo: Month, must be integer 1-12
			#da: Day, must be integer 1-31
			#hr: Hour, must be integer 1-12
			#mi: Minute, must be integer 0-59
		#Converts strings to appropriate type
		valFlag = False
		if valType=='ap':
			if valData == 'a' or valData == 'p':
				valFlag = True
		elif valType=='mo' or valType=='hr':
			valData = int(valData)
			if valData>=1 and valData<=12:
				valFlag = True
		elif valType=='da':
			valData = int(valData)
			if valData>=1 and valData<=31:
				valFlag = True
		elif valType=='mi':
			valData = int(valData)
			if valData>=0 and valData<=59:
				valFlag = True
		elif valType=='hrDur':
			valData = int(valData)
			if valData>=0 and valData<=23:
				valFlag = True
		elif valType=='miDur':
			valData = int(valData)
			if valData>=0 and valData<=59:
				valFlag = True 
		else:
			print "Invalid validation type string (see call to validateEntry)"
			sys.exit()
		return valFlag,valData

	def convAPto24hr(self,hr,ap):
		if   ap == 'p' and hr<12:
			hr24 = hr+12
		elif ap == 'a' and hr==12:
			hr24 = 0
		else:
			hr24 = hr
		return hr24		

	def addEvent(self):
	
		#Solicit Input
		eventName = raw_input('Enter the event name: \n')				

		stayInLoop = True
		curTime = datetime.datetime.now()
		thisYear = curTime.year
		print "Specify event time:"
		while stayInLoop:
			enterMethod = raw_input('Please enter:\n"se" to specify start and end times \n"sd" to specify start and duration, or \n"ed" to specify end and duration \n')			
			if enterMethod == "se":
				
				startMo = self.solicitInput('XX/01/'+str(thisYear)+' - Enter event start month: \n','mo')
				startDa = self.solicitInput(str(startMo)+'/XX/'+str(thisYear)+' - Enter event start day: \n','da')
				print str(startMo)+'/'+str(startDa)+'/'+str(thisYear)
				startHr = self.solicitInput('XX:00 a.m. - Enter event start hour: \n','hr')
				startMi = self.solicitInput(str(startHr)+':XX a.m. - Enter event start minute: \n','mi')
				startAP = self.solicitInput(str(startHr)+':'+str(startMi)+' X.m. - Enter "a" for "a.m." or "p" for "p.m.": \n','ap')
				print str(startHr)+':'+str(startMi)+' '+startAP+'.m.'

				endMo = self.solicitInput('XX/01/'+str(thisYear)+' - Enter event end month: \n','mo')
				endDa = self.solicitInput(str(endMo)+'/XX/'+str(thisYear)+' - Enter event end day: \n','da')
				print str(endMo)+'/'+str(endDa)+'/'+str(thisYear)
				endHr = self.solicitInput('XX:00 a.m. - Enter event end hour: \n','hr')
				endMi = self.solicitInput(str(endHr)+':XX a.m. - Enter event end minute: \n','mi')
				endAP = self.solicitInput(str(endHr)+':'+str(endMi)+' X.m. - Enter "a" for "a.m." or "p" for "p.m.": \n','ap')
				print str(endHr)+':'+str(endMi)+' '+endAP+'.m.'

				startHr = self.convAPto24hr(startHr,startAP)
				endHr   = self.convAPto24hr(endHr  ,endAP  )

				stdt = datetime.datetime(thisYear,startMo,startDa,startHr,startMi)
				eddt = datetime.datetime(thisYear,endMo  ,endDa  ,endHr  ,endMi)

				newEvent = events.Event(eventName ,datetime.datetime.now())
				newEvent.setStartStop(stdt,eddt)
				stayInLoop = False
 
			elif enterMethod == "sd":

				startMo = self.solicitInput('XX/01/'+str(thisYear)+' - Enter event start month: \n','mo')
				startDa = self.solicitInput(str(startMo)+'/XX/'+str(thisYear)+' - Enter event start day: \n','da')
				print str(startMo)+'/'+str(startDa)+'/'+str(thisYear)
				startHr = self.solicitInput('XX:00 a.m. - Enter event start hour: \n','hr')
				startMi = self.solicitInput(str(startHr)+':XX a.m. - Enter event start minute: \n','mi')
				startAP = self.solicitInput(str(startHr)+':'+str(startMi)+' X.m. - Enter "a" for "a.m." or "p" for "p.m.": \n','ap')
				print str(startHr)+':'+str(startMi)+' '+startAP+'.m.'

				startHr = self.convAPto24hr(startHr,startAP)

				durHr   = self.solicitInput('XX hrs, 00 min - Please enter duration hours: \n','hrDur')
				durMi   = self.solicitInput(str(durHr)+' hrs, XX min - Please enter duration minutes: \n','miDur')

				stdt = datetime.datetime(thisYear,startMo,startDa,startHr,startMi)
				drdt = datetime.timedelta(0,0,0,0,durMi,durHr)

				newEvent = events.Event(eventName ,datetime.datetime.now())
				newEvent.setStartDur(stdt,drdt)
				stayInLoop = False


			elif enterMethod == "ed":

				endMo = self.solicitInput('XX/01/'+str(thisYear)+' - Enter event end month: \n','mo')
				endDa = self.solicitInput(str(endMo)+'/XX/'+str(thisYear)+' - Enter event end day: \n','da')
				print str(endMo)+'/'+str(endDa)+'/'+str(thisYear)
				endHr = self.solicitInput('XX:00 a.m. - Enter event end hour: \n','hr')
				endMi = self.solicitInput(str(endHr)+':XX a.m. - Enter event end minute: \n','mi')
				endAP = self.solicitInput(str(endHr)+':'+str(endMi)+' X.m. - Enter "a" for "a.m." or "p" for "p.m.": \n','ap')
				print str(endHr)+':'+str(endMi)+' '+endAP+'.m.'

				endHr   = self.convAPto24hr(endHr  ,endAP  )

				durHr   = self.solicitInput('XX hrs, 00 min - Please enter duration hours: \n','hrDur')
				durMi   = self.solicitInput(str(durHr)+' hrs, XX min - Please enter duration minutes: \n','miDur')

				eddt = datetime.datetime(thisYear,endMo  ,endDa  ,endHr  ,endMi)
				drdt = datetime.timedelta(0,0,0,0,durMi,durHr)

				
				newEvent = events.Event(eventName ,datetime.datetime.now())
				newEvent.setDurStop(drdt,eddt)
				stayInLoop = False

			else:
				print "Input not recognized"

		
		self.printEvent(newEvent)
		self.updateTime()
		self.eventList.append(newEvent)
		self.sortEventList()
		self.unsavedChanges = True
		print 'Event Added!'


	def exitCal(self):
		self.updateTime()
		eventList = self.eventList
		reminders = self.reminders
		libraryPath     = self.fileSaveInfo[0]
		libraryFilePath = self.fileSaveInfo[1]
		tempOutFilePath = self.fileSaveInfo[2]
		fout            = self.fileSaveInfo[3]

		stayInLoop = True
		exitFlag = True
		if self.unsavedChanges:
			while stayInLoop:
				print '\n***Calendar contains unsaved changes. Save before exiting?'
				saStr = raw_input('Enter "y" to save and exit, enter "n" to exit without saving, or "c" to cancel\n')
				if saStr == 'y':
					#Save
					eventList = self.eventList
					pickle.dump(eventList,fout)
					pickle.dump(reminders,fout)
					if os.path.isfile(libraryFilePath):
						os.remove(libraryFilePath)
					fout.close()
					os.rename(tempOutFilePath,libraryFilePath)
					stayInLoop = False
				elif saStr == 'n':
					os.remove(tempOutFilePath)
					stayInLoop = False
				elif saStr == 'c':
					stayInLoop = False
					exitFlag   = False
					print 'Action Cancelled'
				else:
					print 'Input string not recognized.'
		else:
			fout.close()
			os.remove(tempOutFilePath)
		
		if exitFlag:
			print 'Exiting program'
			self.frame.quit()
			self.mstk.destroy()

	def editEvent(self):
		print self.unsavedChanges
		print "Button does not work yet"
	def saveCal(self):
		self.updateTime()
		eventList = self.eventList
		reminders = self.reminders
		libraryPath     = self.fileSaveInfo[0]
		libraryFilePath = self.fileSaveInfo[1]
		tempOutFilePath = self.fileSaveInfo[2]
		fout            = self.fileSaveInfo[3]

		print "Save changes to Calendar?"
		saStr = raw_input('Enter "y" to save or "c" to cancel\n')
		if saStr == 'y':
			#Save
			eventList = self.eventList
			pickle.dump(eventList,fout)
			pickle.dump(reminders,fout)
			if os.path.isfile(libraryFilePath):
				os.remove(libraryFilePath)
			fout.close()
			os.rename(tempOutFilePath,libraryFilePath)
			fout = open(tempOutFilePath,'wb')
			self.fileSaveInfo[3] = fout
			stayInLoop = False
			print 'Calendar Saved!'
			self.unsavedChanges = False
		elif saStr == 'c':
			stayInLoop = False
			print 'Action Cancelled'
		else:
			print 'Input string not recognized.'


