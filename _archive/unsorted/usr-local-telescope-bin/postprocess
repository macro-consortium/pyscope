#!/bin/csh -f
# this script is run by telrun after each new raw image has been created.
# usage:
#   postprocess fullpath cal scale
#
# 1) if cal > 0, apply image corrections, add wcs and fwhm to file
# 2) if scale > 0 fcompress file, rename to .fth, discard .fts file
# 3) inform camera of new file

if ($#argv != 3 ) then
	if ($#argv != 4) then	
	    jd -t; echo " Bad args"": " $argv
	    jd -t; echo " $0"": " 'fullpath corrections scale ["extcmd"]' 
	    exit 1
	endif
endif

set file = "$argv[1]"
set filet = "$file:t"":"
set cal = "$argv[2]"
set scale = "$argv[3]"
if ($#argv == 4) then
	set extcmd = "$argv[4]"
endif

# RBI Flush code -- clear out residual camera image (in background) while doing postprocess
# Calling rbiflush should have no ill-effect on non-RBI enabled cameras (currently only supported for FLI)
# However, it may be superfluous and will emit to log.  
# Therefore, this implementation does not call rbiflush directly. Rather, it calls upon an optional
# script, pp_rbi.sh, which may also be edited for optimal flush time settings.
# If this script is not present, there is no effect.
if (-e $TELHOME/bin/rbiflush) then
    if (-e $TELHOME/bin/pp_rbi.sh) then
        jd -t; echo " Performing RBI Flush"
        $TELHOME/bin/pp_rbi.sh &
    endif
endif

# (sso) save raw image first
if (-e $TELHOME/bin/pp_save_raw.sh) then
    jd -t; echo " $filet Saving raw image"
    $TELHOME/bin/pp_save_raw.sh $file 
endif

echo ""
jd -t; echo " $filet Starting postprocessing"

# (extcmd processing) pass off to external program/script for processing external commands
if ($#argv == 4) then
	if (-e $TELHOME/bin/extcmd) then
		jd -t; echo " $filet Handling external command: $extcmd "
		$TELHOME/bin/extcmd $file "$extcmd"
	endif
endif

# 1) if cal > 0, apply image corrections, add wcs and fwhm to file
if ("$cal" > 0) then
    jd -t; echo " $filet Applying image corrections"
    calimage -C $file
    jd -t; echo " $filet Adding WCS headers"
    wcs -wu .3 $file
    jd -t; echo " $filet Adding FWHM headers"
    fwhm -w $file
else
    jd -t; echo " $filet No image corrections requested"
endif

# 2) if scale > 0 fcompress file, rename to .fth, discard .fts file
if ("$scale" > 0) then
    jd -t; echo " $filet Compressing with scale $scale"
    # fcompress -r adds HCOMSTAT and HCOMSCAL fits headers and removes the .fts.
    # it also refuses to overwrite an existing .fth file which can happen for
    # repeats.
    set cmp_fn = "$file:r".fth
    rm -f $cmp_fn
    fcompress -s $scale -r $file 
    set file = $cmp_fn
endif

jd -t; echo " $filet Postprocessing complete"

# 3) inform camera of new file
if (! $?TELHOME) setenv TELHOME /usr/local/telescope
set camfifo = $TELHOME/comm/CameraFilename
if (-w $camfifo && -p $camfifo) then
    jd -t; echo " $filet Informing Camera (if any)"
    # N.B. echo hangs if there is no camera running with the fifo open
    (echo $file >> $camfifo & sleep 5; kill %1) >& /dev/null
endif

# 4) (SSO) Perform background transfer of new images to FTP server
if (-e $TELHOME/bin/xfer_queue_sso.sh) then
    set lfn = `date -u +%d-%B-%y`
    jd -t; echo " $filet executing sso xfer script for $lfn"
    mkdir -p $TELHOME/archive/logs/sso_xfer
    $TELHOME/bin/xfer_queue_sso.sh $file >> $TELHOME/archive/logs/sso_xfer/$lfn.log & 
endif
exit 0

