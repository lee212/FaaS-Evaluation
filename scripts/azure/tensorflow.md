# Experiment on TensorFlow

As a part of tensorflow testing, we investigate Azure to run TensorFlow Imagenet.

The problems we found so far:

- python 3.5 or 3.6 required but azure supports only 2.7. (3.4 included in d:\Python34 though)
  - 3.5 or 3.6 is installable by extentions according to https://stackoverflow.com/questions/47208325/using-python-3-in-azure-functions
    - `python -m pip install virtualenv`
    - `d:\home\python364x86\Scripts\virtualenv.exe tensorflow`
    - `tensorflow\Scripts\Activate.bat`
    - `pip3 install --upgrade tensorflow`
    - Error:

```
(tensorflow) D:\home>(tensorflow) D:\home>pip3 install --upgrade tensorflow
Collecting tensorflow
  Could not find a version that satisfies the requirement tensorflow (from versions: )
	No matching distribution found for tensorflow
```

from https://tensorflow-functions.scm.azurewebsites.net/DebugConsole
