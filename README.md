# disciple
### Personal scheduling app.  Intended to simplify scheduling so that it is done consistently.

## Use

To run, change the "libraryPath" variable in "schedulingApp" to a valid path on your computer.  The app will create a data file in that location. Then, run the "schedulingApp" code.

Right now the app is usable, but implementing the following changes will simplify it.

## Planned features 
### Ordered by ease of implementation and importance:
1.  Compile code into windows executable file
    - Allow the program to be run by double-clicking an icon rather than from the command prompt
    - An executable can also be tied to Windows start-up, so the schedule opens whenver the user turns on his computer
    - Executable and schedule data can be stored in a Dropbox folder, so the schedule can be synchronized between devices
    - It seems there are programs for this purpose: http://www.pyinstaller.org/
2. Edit events
    - Sounds dumb, but right not there isn't an option to edit events that are entered.  Instead events must be deleted and recreated.
    - This option can borrow a lot of code from the event entry feature.
    - Creating a different class for recurring events may make this easier.   
3. Graphical prompts
    - Right now, the code takes input from the command prompt.  This is a little clunky, because it forces the user to fill out all of the fields in a prescribed order.  A well-designed GUI could be easier to use, because it can pre-fill default values and allow the user to ignore non-essential fields.
4. Deadlines
    - Find a way to show when a deadline is approaching... add a countdown?  Visualize on the calendar with a bold red line?  Right now it isn't obvious how to fit deadlines into the present events/reminders framework.
    - Presently I use the "Reminders" section to keep track of deadlines, but this clutters up this space, and doesn't call my attention to deadlines that are approaching
5. Follow-up
    - After an event passes, ask the user whether he actually did what he planned to or not.  Store the feedback, and allow the user to see how well he is following through on the committments he is making
    - May need to be optional; this could be annoying if the app asks you to follow-up every time the app is opened
6. Add conflict handling
    - Detect when the user attempts to schedule two events at the same time
      - Can rely on some of the code used in the "schedule events from present" feature
    - Prompt the user to modify the schedule accordingly
      - Developing an intuitive way to prompt the user will be challenging, but this could be a very powerful feature
        - E.g., Allow the user to push events back / forward, shorten one event to resolve the conflict, etc.
      - Creating a different class for recurring events may be necessary
    


## Fixes 
### No particular order:
1. Delete old events
    - The code stores all old events; they don't take up a lot of space, but it isn't necessary.  Deleting old events could be incorporated with the follow-up feature
2.  Ensure prompts are clear, readable, and consistent
    - I wrote them quickly and they probably aren't
3.  Add a simple way to visualize event details
    - Right now, event description is printed on the calendar, and the full event description can be seen by hitting the "List 48 hours button"
    - Potential improvements:
      - Make a callout with full event details that appears when you mouse over the box
      - Edit the "List 48 hours" button to list a variable number of hours
      - Add a "location" attribute to events?  This could be annoying to fill out every time, because it is not always applicable.
4.  Clean and organize the code
    - When isn't this an issue?  Hopefully it is easy to follow, but I know it is disorganized
5.  Fix the "calendar update" mechanism
    - In certain situations the calendar will simply draw another copy over itself when it is edited. 
    - Rather than redrawing the calendar, it would be better to store attributes of the elements, and change them when appropriate.  The "current time" bar feature works this way, in that its position in the calendar space is altered whenever the time is updated
6. Prep the code for 2018
    - Right now events can only be scheduled for 2017, because it would be annoying to enter the year every time that an event is entered.  
    - Introducing graphical prompts is the long-term solution for this, because a default value can be pre-filled 
    - Short-term, it may be best to just add a "year" prompt to the command line routine, or just default the year to the current time and let the user change it in the "edit event" routine


-Adam
