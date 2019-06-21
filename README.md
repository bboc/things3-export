# things3-export

Export Script for Things 3 (by Cultured Code): Convert all tasks in all projects to TaskPaper files. Headers, checklists, notes and tags are preserved.

I created this because I found that things is great for capturing tasks and reminders for stuff to do, but I am much more effective when I plan projects in TaskPaper. YMMV.

## Usage:

### Work on the live database 

It's definitely a good idea to close things before you do that:

`$ source t2tp.sh`

### Work on a copy of the database


Copy the things database to the same folder where you downloaded the script:

`$ cp ~/Library/Containers/com.culturedcode.ThingsMac/Data/Library/Application\ Support/Cultured\ Code/Things/Things.sqlite3 .` 
to the location of the script, then run

`$ python3 export_things.py`

You will find all your tasks in a folder called `export data`, one TaskPaper file per project, areas are grouped in subfolders.

If you prefer one TaskPaper file per area, you can add the option `--combine`, if you prefer one file with everything, just add `--stdout` and capture in a file, e.g.

`$ source t2tp.sh --stdout >all-my-tasks.taskpaper`

## Restore a database backup in Things 3

If you, like me, play around with your Things database and accidentally sync a lot of changes to the Things cloud, [here's how to restore a backup database](https://support.culturedcode.com/customer/en/portal/articles/2803595-restoring-from-a-backup)




