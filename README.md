# things3-export

Export Script for Things 3 (by Cultured Code): Convert all tasks in all projects to TaskPaper files. Headers and checklists are preserved, tags are ignored (for now).

I created this because I found that things is great for capturing tasks and reminders for stuff to do, but I am much more effective when I plan projects in TaskPaper. YMMV.

## Usage:

Copy the things database from `~/Library/Containers/com.culturedcode.ThingsMac/Data/Library/Application Support/Cultured Code/Things/Things.sqlite3` to the location of the script, then run

`python3 export_things.py`

You will find all your tasks in a folder called `export data`, one TaskPaper file per project, areas are grouped in subfolders.

