    
import sys
import argparse    
from PySide2 import QtWidgets

from osu_diffcalc_gui.mainwindow import MainWindow

def main():
    parser = argparse.ArgumentParser("osu_test_map_gen")
    parser.add_argument("-c","--command_prefix",help="prepended to command before executing")
    parser.add_argument("-d","--directory", help="Working directory of command")
    parser.add_argument("-f", "--file", help="Name of output .osu file", default="test.osu")
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(args.command_prefix, args.directory, args.file)
    window.show()
    sys.exit(app.exec_())

main()