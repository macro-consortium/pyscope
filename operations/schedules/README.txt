Telrun files are stored here.

Lifecycle of a telrun file:

1. On the remote server, the "telsched" program produces "telrun.sls"

2. The syncfiles script running on the telescope computer copies the 
   remote "telrun.sls" (if one exists) to "telrun.incoming" on the 
   local machine.

3. After the file has been successfully copied, the syncfiles script renames
   "telrun.transferring" to "telrun.new". Renaming a file is usually an
   atomic operation, so the telrun program will only see fully-transferred
   files.

4. Additionally, the syncfiles script will rename "telrun.sls" to
   "telrun.sent" on the remote machine to indicate that this
   version of the .sls file has been fully transferred to the telescope computer.

5. When the telrun script sees a "telrun.new" file on the telescope computer,
   it renames the file to "telrun.sls" and starts scanning through that file.
   As the file is processed, the status codes for each scan in "telrun.sls"
   will be updated.

6. Periodically the syncfiles script will copy "telrun.sls" back to the 
   remote server. The remote file is named "telrun.now" and can be used
   by the server to report on the current status of the observing run
   (how many scans have succeeded, failed, etc.)

In summary:

   TELESCOPE COMPUTER    SERVER COMPUTER          Notes
   ------------------    ---------------          ------
1.                       telrun.sls               Produced by telsched
2. telrun.incoming       telrun.sls               Being copied by syncfiles
3. telrun.new            telrun.sls               Renamed by syncfiles after successful transfer
4. telrun.new            telrun.sent              Renamed by syncfiles after successful transfer
5. telrun.sls            telrun.sent              Renamed by telrun when picked up for processing
6. telrun.sls            telrun.now, telrun.sent  Copied by syncfiles


