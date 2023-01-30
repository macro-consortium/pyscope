"""
Wrapper around iotalib.telrun_main that sets up logging and notifications,
and then runs the main program. This way, pretty much anything
that causes an exception (including module imports and
syntax errors) can get caught and a notification e-mail can be 
attempted. Of course, that doesn't include problems with the notification
system itself...
"""

import sys

import relimport # Set up our path so that iotalib can be found

def main():
    try:
        print("Setting up logging")
        import logging
        from iotalib import logutil
        logutil.setup_log("telrun.log")
    except Exception as ex:
        print("ERROR SETTING UP LOGGING. EXITING...")
        print()
        raise

    try:
        logging.info("Loading notification config")
        from iotalib import config_notification
        config_notification.read()
    except Exception as ex:
        logging.exception("UNABLE TO LOAD NOTIFICATION CONFIGURATION")
        logging.error("Refusing to start until we have valid notification settings")

        sys.exit(1)

    try:
        from iotalib import notification
    except Exception as ex:
        print("Unable to load notification module:")
        print(ex.message)
        print()
        print("Refusing to start until we are able to send notifications")

        sys.exit(1)

    try:
        # Run the main script
        from iotalib import telrun_main
        telrun_main.run()
    except Exception as ex:
        # Record the error and try to send a notification e-mail
        logging.exception("Fatal error in telrun")
        """try:
            notification.send_error("Telrun crash", "Fatal error in telrun: " + str(ex))
        except Exception as ex:
            logging.exception("NOTIFICATION EMAIL NOT SENT DUE TO A PROBLEM")""" # 6/22/21 WWG: disabled until permissions fixed

    logging.info("Telrun exiting")


    
if __name__ == "__main__":
    main()
