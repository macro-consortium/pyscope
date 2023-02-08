from .AvantesController import as5216
import time


def main():
    ava = as5216.AvantesDriver()
    ava.AVS_Init()
    ava.AVS_GetList()
    ava.AVS_Activate()
    ava.AVS_GetNumPixels()
    ava.AVS_SetPrescanMode()
    ava.AVS_PrepareMeasure()

    starttime = time.time()
    ava.AVS_Measure()
    while(starttime + 20 > time.time()):
        time.sleep(0.01)
        if ava.AVS_PollScan():
            print("Got some spectra")
            break
    ava.AVS_StopMeasure()
    print(ava.AVS_GetScopeData())


if __name__ == "__main__":
    main()
