# Export your Things 3 database to TaskPaper

Here's a simple App to export from [Things 3 (by Cultured Code)](https://culturedcode.com/things/) to [TaskPaper](https://www.taskpaper.com).

I created this because I discovered that Things is great for capturing ideas, planning my day and reminding me about all the stuff that I don't care about. but need to do anyway. However, for planning and excepting on all my projects, I found that I am much more effective using plain text TaskPaper files, and sometimes also OmniFocus (which imports and exports TaskPaper format). YMMV.
 
Currently, the exporter has the following features:

- export tasks, projects (including the inbox) and areas 
- headers, checklists, notes
- tags for tasks, projects and areas
- done and trashed items are excluded
- due dates, start dates, today and someday are added as tags to projects and tasks

Repeating tasks are currently not supported. The exporter was tested with Things 3.9

## Usage

Download the latest version of the app from the [releases page](https://github.com/bboc/things3-export/releases).

**Warning: Make sure to close Things before you run the app!!**

Run the app, you will see this screen:

![](app-screenshot.png)

1. **Select the correct database**: Click "Select File" to select your things database. The dialog should open the correct folder, so you just need to select the database.
2. **Select an output format**: all in one file, one file per area, or one file per project
3. (optional) **Enter name for the output** this will be used as a name of the export directory in your Downloads folder (or as a filename in case you want all in one file). If you enter nothing, the default is "Things 3 export"
4. **Click Export**: you will see some output in the output window

That's it. Go to your Downloads folder to see the export.


## Command line Tools

In addition to the GUI-Version, the exporter can also be run from the command line.

By default, the exporter will create a folder for each area that contains a TaskPaper file per project. One file per area and one file with everything is also possible. To see what the exporter can do, open the Terminal app and run 

`$ python3 export_things.py -h`


### Setup

The exporter is Python program run from the command line, download `export_things.py` and `t2tp.sh` to a directory on your Mac, and then navigate to that directory in the Terminal app. 


#### Installing Python 3

While the app comes bundled with a Python interpreter, you need to have Python 3 installed to run the command line version. 

If you don't have it installed, here's what you need to do:

    $ xcode-select --install
    $ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    $ brew install python3 

If you have Xcode or the Command Line Tools (CLT) for Xcode already installed, skip step 1. If you have [Homebrew](https://brew.sh) installed, skip step 2. If you have Python 3 already installed, why are you reading this anyway?


### Usage:


#### Work on the live database 

It's definitely a good idea to close things before you do that:

`$ source t2tp.sh`

You will find all your tasks in a folder called `export data`, one TaskPaper file per project, areas are grouped in subfolders.

If you prefer one TaskPaper file per area, you can add the option `--format area`, if you prefer one file with everything, just add `--format all`.


#### Work on a copy of the database

Copy the things database to the same folder where you downloaded the script:

`$ cp ~/Library/Containers/com.culturedcode.ThingsMac/Data/Library/Application\ Support/Cultured\ Code/Things/Things.sqlite3 .` 

then run the exporter:

`$ python3 export_things.py`


### Restore a database backup in Things 3

If you, like me, play around with your Things database and accidentally sync changes you don't want back to the Things cloud, [here's how to restore a backup database](https://support.culturedcode.com/customer/en/portal/articles/2803595-restoring-from-a-backup)
