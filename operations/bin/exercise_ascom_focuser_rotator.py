from datetime import datetime
import random
import sys
import time
from win32com.client import Dispatch

# Repeatedly move an ASCOM focuser and/or rotator to target positions to
# exercise the driver and hardware. Can exercise devices individually
# or in parallel.


#### SETTINGS #####################

EXERCISE_FOCUSER = True
EXERCISE_ROTATOR = False

USE_RANDOM_FOCUS_TARGETS = False # True: randomly generate targets between RANDOM_FOCUS_POS_MIN and RANDOM_FOCUS_POS_MAX
                                 # False: repeatedly iterate through SEQUENTIAL_FOCUS_TARGETS
RANDOM_FOCUS_POS_MIN = 5000
RANDOM_FOCUS_POS_MAX = 14000
SEQUENTIAL_FOCUS_TARGETS = [6300, 7200, 21561]

USE_RANDOM_ROTATE_TARGETS = True # True: randomly generate targets between RANDOM_ROTATE_POS_MIN and RANDOM_ROTATE_POS_MAX
                                  # False: repeatedly iterate through SEQUENTIAL_ROTATE_TARGETS
RANDOM_ROTATE_POS_MIN = 180
RANDOM_ROTATE_POS_MAX = 220
SEQUENTIAL_ROTATE_TARGETS = list(range(180, 220, 10))

MAX_FOCUSER_ERROR = 2
MAX_ROTATOR_ERROR = 0.01

SLEEP_BETWEEN_ITERATION_SECONDS = 3

#### END SETTINGS #################



startTime = time.time() # Used for logging
logIndent = 0
lastLogWasSameLine = False

def main():
    global logIndent

    if EXERCISE_FOCUSER:
        log("Opening ASCOM focuser...")
        focus = Dispatch("ASCOM.PWI3.Focuser")
        focus.Connected = True

    if EXERCISE_ROTATOR:
        log("Opening ASCOM rotator...")
        rotate = Dispatch("ASCOM.PWI3.Rotator")
        rotate.Connected = True

    iterationCount = 1
    while True:
        log("Test %d" % iterationCount)
        logIndent += 2

        if USE_RANDOM_FOCUS_TARGETS:
            focusTarget = random.randint(RANDOM_FOCUS_POS_MIN, RANDOM_FOCUS_POS_MAX)
        else:
            seqTargetIndex = (iterationCount-1) % len(SEQUENTIAL_FOCUS_TARGETS)
            focusTarget = SEQUENTIAL_FOCUS_TARGETS[seqTargetIndex]

        if USE_RANDOM_ROTATE_TARGETS:
            rotateTarget = random.randint(RANDOM_ROTATE_POS_MIN, RANDOM_ROTATE_POS_MAX)
        else:
            seqTargetIndex = (iterationCount-1) % len(SEQUENTIAL_ROTATE_TARGETS)
            rotateTarget = SEQUENTIAL_ROTATE_TARGETS[seqTargetIndex]


        focusGotoSent = False
        rotateGotoSent = False
        focusGotoDelay = 0
        rotateGotoDelay = 0

        if EXERCISE_FOCUSER and EXERCISE_ROTATOR:
            orderCase = random.randint(0, 3) # 0 = focuser first, rotator delayed
                                             # 1 = rotator first, focuser delayed
                                             # 2 = focuser, then rotator immediately
                                             # 3 = rotator, then focuser immediately
            if orderCase == 0:
                rotateGotoDelay = random.random()*5
                log("Focuser, then delayed rotator by %.2f sec" % rotateGotoDelay)

            elif orderCase == 1:
                focusGotoDelay = random.random()*5
                log("Rotator, then delayed focuser by %.2f sec" % focusGotoDelay)

            elif orderCase == 2:
                log("Focuser, then immediate rotator")

                log("Focus goto %d" % focusTarget)
                focus.Move(focusTarget)
                log("Rotate goto %d" % rotateTarget)
                rotate.MoveAbsolute(rotateTarget)
                focusGotoSent = True
                rotateGotoSent = True

            elif orderCase == 3:
                log("Rotator, then immediate focuser")

                log("Rotate goto %d" % rotateTarget)
                rotate.MoveAbsolute(rotateTarget)
                log("Focus goto %d" % focusTarget)
                focus.Move(focusTarget)
                focusGotoSent = True
                rotateGotoSent = True

        gotoDelayStartTime = time.time()

        if EXERCISE_FOCUSER:
            focusIsComplete = False
        else:
            focusIsComplete = True

        if EXERCISE_ROTATOR:
            rotateIsComplete = False
        else:
            rotateIsComplete = True

        while True:
            if EXERCISE_FOCUSER and not focusGotoSent and time.time()-gotoDelayStartTime >= focusGotoDelay:
                log("Focus goto %d" % focusTarget)
                focus.Move(focusTarget)
                focusGotoSent = True

            if EXERCISE_ROTATOR and not rotateGotoSent and time.time()-gotoDelayStartTime >= rotateGotoDelay:
                log("Rotate goto %d" % rotateTarget)
                rotate.MoveAbsolute(rotateTarget)
                rotateGotoSent = True

            focusStatus = ""
            rotateStatus = ""
            if EXERCISE_FOCUSER:
                focusStatus = "Focuser %s/%s" % (focus.Position, focus.IsMoving)
            if EXERCISE_ROTATOR:
                rotateStatus = "Rotator %s/%s" % (rotate.Position, rotate.IsMoving)

            logSameLine(focusStatus + "  " + rotateStatus)

            if not focusIsComplete:
                if focusGotoSent and not focus.IsMoving:
                    posError = focus.Position - focusTarget
                    if abs(posError) > MAX_FOCUSER_ERROR:
                        log("FOCUS POSITION ERROR: target = %f, pos = %f" % (focusTarget, focus.Position))
                    log("Focus goto complete")
                    focusIsComplete = True

            if not rotateIsComplete:
                if rotateGotoSent and not rotate.IsMoving:
                    posError = rotate.Position - rotateTarget
                    if abs(posError) > MAX_ROTATOR_ERROR:
                        log("ROTATE POSITION ERROR: target = %f, pos = %f" % (rotateTarget, rotate.Position))
                    log("Rotate goto complete")
                    rotateIsComplete = True


            if focusIsComplete and rotateIsComplete:
                break

        logIndent -= 2
        iterationCount += 1


        log("Sleeping for %d seconds" % SLEEP_BETWEEN_ITERATION_SECONDS)
        time.sleep(SLEEP_BETWEEN_ITERATION_SECONDS)

def log(txt):
    global lastLogWasSameLine

    f = open("exercise_ascom_focus_rotator_log.txt", "a")

    indentSpace = " "*logIndent
    if lastLogWasSameLine:
        print()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "%s %.2f: %s%s" % (timestamp, time.time()-startTime, indentSpace, txt)
    print(line)
    print(line, file=f)
    f.close()
    lastLogWasSameLine = False

def logSameLine(txt):
    global lastLogWasSameLine

    indentSpace = " "*logIndent
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sys.stdout.write("%s %.2f: %s%s" % (timestamp, time.time()-startTime, indentSpace, txt))
    sys.stdout.write("\r")
    lastLogWasSameLine = True

if __name__ == "__main__":
    main()

