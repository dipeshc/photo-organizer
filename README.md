# Photo Organizer

## What is it?
A quick and dirty script/application designed to allow my wife to quickly pre-process 10s of gigabytes of photos she found on some old hard drives. These drives had different organization patterns and many drives contained duplicates.

This script/application is not meant to take the place of any dedicated photo management system, but instead intended to help a human pre-process the files into some logical order before they come along and sort the photos into something more significant like events.

## What does it do?
Process a folder containing photos and vidoes and copies them into a new directory structure based on the year, month, and week the file was taken.

While processing the photos, it detects duplicates and marks them as such. The first file found is the original, any subsequent copies are marked as duplicates.

## How do you run it?
Firstly download the application from [Releases](https://github.com/dipeshc/photo-organizer/releases) onto your computer.

If your running on Windows, drag a folder onto the application. The application will create a new folder adjacent the one that was just dragged ontop but suffixed with "-organized". This folder will contain the organized files.

If your on Mac, double click the application, drag the folder onto the terminal that just opened and then hit return.

## How do I build it?
The below steps will create an executable application. Whichever platform (i.e. Windows, Mac, or Linux) is used, is the only place the application will run.


Be sure to alread have Python 3.3 or greater installed.

#### Mac and Linux
```bash
python3 -m venv env
source .\env\bin\activate
pip install -r requirements.txt
pyinstaller --onefile photoorganizer.py
```

#### Windows
```pwsh
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
pyinstaller --onefile photoorganizer.py
```