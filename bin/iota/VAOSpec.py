import seabreeze.spectrometers as sb 
import matplotlib.pyplot as plt
from datetime import datetime
import csv
import time
import os


class MayaSpectrometer:

    def __init__(self):
        self.spec = sb.Spectrometer(sb.list_devices()[0])
        self.devIntTime = 100000
        self.spec.integration_time_micros(self.devIntTime)
        self.wavelengths = self.spec.wavelengths()
        self.curSpec = []

    def getDev(self):
        return self.spec

    def setDevIntTime(self, secs):
        self.devIntTime = secs * 1000000
        self.spec.integration_time_micros(self.devIntTime)

    def multipleExposures(self, intTime):
        data = []
        if(intTime < (self.devIntTime / 1000000)):
            return "Device integration time is less than specified "\
                    "integration time. choose {0} secs or a multiple of {0}".format(self.devIntTime)
        for t in range((intTime * 1000000) / self.devIntTime):
            data.append(self.spec.intensities())

        summedData = [0 for x in range(len(data[0]))]
        for s in data:
            d = []
            for x, y in zip(summedData, s):
                d.append(x + y)
            summedData = d
        self.curSpec = [float(x) / len(data) for x in summedData]
        return self.curSpec

    def singleExposure(self):
        self.curSpec = self.spec.intensities()
        return self.curSpec

    def showLastSpec(self):
        plt.plot(self.wavelengths, self.curSpec)
        plt.axis([min(self.wavelengths), max(self.wavelengths),
                  min(self.curSpec), max(self.curSpec)])
        plt.show()

    def liveGraph(self, duration):
        X = self.wavelengths
        Y = self.spec.intensities()
        plt.ion()
        graph = plt.plot(X, Y)[0]
        plt.axis([min(X), max(X), min(Y), max(Y)])

        startTime = time.time()
        runTime = duration

        while(time.time() < (startTime + runTime)):
            Y = self.spec.intensities()
            self.curSpec = Y
            graph.set_ydata(Y)
            plt.axis([min(X), max(X), min(Y), max(Y)])
            plt.draw()

        plt.ioff()
        plt.close()

    def saveLastSpec(self, filepath, target):
        filename = "spec_%03d.csv" % (target)
        savepath = os.path.join(filepath, filename)
        with open(savepath, 'wb') as out:
            cwrite = csv.writer(out)
            for x, y in zip(self.wavelengths, self.curSpec):
                cwrite.writerow([x, y])

    def close(self):
        self.spec.close()

    def __exit__(self, type, value, traceback):
        self.close()


class mosaicPlotter:

    def __init__(self, row, col, wavelengths):
        self.row = row
        self.col = col
        self.wavelengths = wavelengths
        self.f, self.axarr = plt.subplots(row, col, sharex=True, sharey=True)
        self.intensixtrm = []
        plt.ion()
        plt.show()

    def addSpec(self, target, specData):
        self.intensixtrm = self.intensixtrm + [min(specData), max(specData)]
        self.axarr[((target - 1) / self.col),
                   ((target - 1) % self.row)].axis([min(self.wavelengths),
                                                    max(self.wavelengths),
                                                    min(self.intensixtrm),
                                                    max(self.intensixtrm)+1000]
                                                   )
        self.axarr[((target - 1) / self.col),
                   ((target - 1) %
                       self.row)].set_title("T: %d" % (target))
        self.axarr[((target - 1) / self.col), ((target - 1) %
                                               self.row)].plot(
                                               self.wavelengths, specData)
        plt.draw()

    def saveSpec(self, filepath):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
        filename = "spec_grid_%s.png" % (timestamp)
        savepath = os.path.join(filepath, filename)
        plt.savefig(savepath)
