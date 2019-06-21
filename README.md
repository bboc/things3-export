# Export your Things 3 database to TaskPaper

Here's a simple tool to export from [Things 3 (by Cultured Code)](https://culturedcode.com/things/) to [TaskPaper](https://www.taskpaper.com).

I created this because I found that Things is great for capturing tasks and reminders for stuff to do, but I am much more effective when I plan larger projects in TaskPaper or OmniFocus (where one can import TaskPaper files). YMMV.
 
Currently, the exporter has the following features:

- export tasks, projects (including the inbox) and areas 
- headers, checklists, notes
- tags for tasks, projects and areas
- done and trashed items are excluded
- due dates, start dates, today and someday are added as tags to projects and tasks

Repeating tasks are currently not supported.

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




