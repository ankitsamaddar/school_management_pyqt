## 1. Create Python Enviroment
   `python -m venv pyenv`
   `.\pyenv\Scripts\activate`
## 2. Install the tools
   `pip cache remove * `    # remove all cache

   `pip install pyqt6 pyqt6-tools>=6.4`

   > 6.4 was the [latest](https://github.com/altendky/pyqt-tools#installation)

If you want to view the generated code from within Designer, you can run
`Scripts/pyqt6-tools.exe installuic` and it will copy `pyuic6.exe` such that Designer will use it and show you generated Python code.

Note that this will enable viewing using the C++ menu item while the Python menu item will be broken.

Without having made this adjustment, the C++ option shows C++ code while the Python option shows PySide2 code. pyqt6 must already be installed or this script will be unable to find the original pyuic6.exe to copy.

## 3. Run QTDesigner
> `pyenv/Scripts/pyqt6-tools.exe designer`
