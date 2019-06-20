# things3-export

Export Script for Things 3 (by Cultured Code): Convert all tasks in all projects to TaskPaper files. Headers and checklists are preserved, tags are ignored (for now).

I created this because I found that things is great for capturing tasks and reminders for stuff to do, but I am much more effective when I plan projects in TaskPaper. YMMV.

## Usage:

### Work on the live database 

It's probably a good idea to close things before you do that:

`$ source t2tp.sh`

### Work on a copy of the database


Copy the things database to the same folder where you downloaded the script:

`$ cp ~/Library/Containers/com.culturedcode.ThingsMac/Data/Library/Application\ Support/Cultured\ Code/Things/Things.sqlite3 .` 
to the location of the script, then run

`$ python3 export_things.py`

You will find all your tasks in a folder called `export data`, one TaskPaper file per project, areas are grouped in subfolders.

If you prefer one TaskPaper file per area, you can add the option `--combine`




