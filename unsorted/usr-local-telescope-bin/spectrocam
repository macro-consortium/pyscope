#!/usr/bin/perl

# script-level driver for a Talon ccdcamera interface
# that provides a bridge to Kevin Ivarsen's OceanOptics spectrometer driver

# get params from $TELHOME/archive/config/spectrocam.cfg
# send errors to $TELHOME/archive/logs/spectrocam.log
# see &usage() for command summary.

# defined in spectrocam.cfg:  $id, $channels, $deviceFile, $packetBytes, $elog

# get parameters
$TELHOME = $ENV{TELHOME};
do "$TELHOME/archive/config/spectrocam.cfg";

# set $traceon to 1 if want trace info
$traceon = 0;

# sync output
$| = 1;

# exposure notation on closed shutter images
$expStamp = 0;

# get command
$cmd = (@ARGV > 0 and $ARGV[0] =~ /^-[^h]/) ? $ARGV[0] : &usage();

# return current temp
if ($cmd eq "-T") {
    &errlog ("@ARGV") if @ARGV != 1;
    print "0\n"; # not used -- here for Talon compatibility only
    exit 0;
}

# return maxen
if ($cmd eq "-f") {
    &errlog ("@ARGV") if @ARGV != 1;
    #print "$imw $imh $maxbx $maxby\n";
    print "$channels 1 1 1\n";
    exit 0;
}

# -g: check exp args
if ($cmd eq "-g") {
    &errlog ("@ARGV") if @ARGV != 2;
    my ($x,$y,$w,$h,$bx,$by,$shtr) = split (/:/, $ARGV[1]);
    if ($x != 0 or $y != 0 or $w != $channels or $h != 1) {
	print ("Subframing is not supported\n");
	exit 1;
    }
    if ($bx != 1) {
	print ("X binning must be 1\n");
	exit 1;
    }
    if ($by != 1) {
	print ("Y binning must be 1\n");
	exit 1;
    }
    if ($shtr != 1) {
	print ("Shutter must be open (1)\n");
	exit 1;
    }
    exit 0;
}

# camera id string
if ($cmd eq "-i") {
    &errlog ("@ARGV") if @ARGV != 1;
    print "$id\n";
    exit 0;
}

# kill exposure.
if ($cmd eq "-k") {
    &errlog ("@ARGV") if @ARGV != 1;
    #print "Can not stop Vcam expose\n";
    # oh yeah?
	my @s = reverse split("/",$0);
	my $nm = @s[0];
    &trace("Killing $nm");
    system("killall $nm");
    exit 1;
}

# open or close shutter
if ($cmd eq "-s") {
    &errlog ("@ARGV") if @ARGV != 2;
    #&shutter ($ARGV[1]);
    exit 0;
}

# -x: start exp, hang around until get image, send 1 byte when see something,
# rest of file to stdout, then exit.
# N.B. any error messages should have extra leading char.
if ($cmd eq "-x") {
    &errlog ("@ARGV") if @ARGV != 2;
    my ($ms,$x,$y,$w,$h,$bx,$by,$shtr) = split (/:/, $ARGV[1]);

    # sanity check parameters
    if ($x != 0 or $y != 0 or $w != $channels or $h != 1) {
	print ("Subframing is not supported\n");
	exit 1;
   }
    if ($bx != 1 or $by != 1) {
	print ("Binning too high\n");
	exit 1;
    }
	
    # Send the exposure command to the driver
    open F, ">$deviceFile" or &errlog("$deviceFile: $!");
	print F "$ms"; # write the exposure time in milliseconds
	close F
	
	# wait for exposure to be done
	&mssleep($ms);

    print "\n";				# one dummy char to signal end of exp

    my $sz = $channels*2;
	my $tot = 0;
	my $nrd = 0;
	my $buf,$lsb,$msb;
		
    # read pixel data from the driver
    open F, "<$deviceFile" or &errlog("$deviceFile: $!");
    &trace ("sending pixels");
    while($tot < $sz) {
		# read a packet of LSB data
		$nrd = read(F, $lsb, $packetBytes);
		&errlog("$deviceFile: $!") if !defined($nrd);
		&errlog("$deviceFile read short @ $tot+$nrd/$sz") if ($nrd < $packetBytes);		
		$tot += $nrd;
		
#		&trace("read $nrd bytes of lsb data");
		
		# read a packet of MSB data
		$nrd = read(F, $msb, $packetBytes);
		&errlog("$deviceFile: $!") if !defined($nrd);
		&errlog("$deviceFile read short @ $tot+$nrd/$sz") if ($nrd < $packetBytes);		
		$tot += $nrd;
		
#		&trace("read $nrd bytes of msb data");
		
		
		# now output
		my $i = 0;
		for(; $i<$packetBytes; $i++) {
			print substr($msb,$i,1);
			print substr($lsb,$i,1);
		}
		
		&trace("processed $tot of $sz bytes");
	}
    close F;

    exit 0;
}

# print usage summary and exit
sub usage
{
    my $me = $0;
    $me =~ s#.*/##;
    print "Usage: $me {options}\n";
    print "Purpose: operate an OceanOptics spectrometer from Talon via share file interface\n";
    print "Interface takes parameters shown; spectrometer only responds to those it can intelligently\n";
    print "Uses $TELHOME/archive/config/spectrocam.cfg for configurable values\n";
    print "Options:\n";
    print " -g x:y:w:h:bx:by:shtr      test if given exp params are ok (MUST BE 0:0:$channels:1:1:1:1)\n";
    print " -x ms:x:y:w:h:bx:by:shtr   start the specified exposure\n";
    print "                            shtr: -1= Flat 0=Close 1=Open 2=OOCO 3=OOCOCO (MUST BE 1)\n";
    print " -k                         kill current exp, if any\n";
    print " -t temp                    set temp to given degrees C (NOT SUPPORTED)\n";
    print " -T                         current temp on stdout in C (RETURNS 0)\n";
    print " -s open                    immediate shutter open or close (IGNORED)\n";
    print " -i                         1-line camera id string on stdout\n";
    print " -f                         max `w h bx by' on stdout\n";

    exit 1;
}

# append $_[0] to STDOUT and timestamp + $_[0] to $elog and exit
sub errlog
{
	print " $_[0]";
	open EL, ">>$elog";
	$ts = `jd -t`;
	print EL "$ts: $_[0]\n";
	close EL;
	exit 1;
}

# if $trace: append $_[0] to $elog
sub trace
{
	return unless ($traceon);
	open TL, ">>$elog";
	$ts = `jd -t`;
	print TL "$ts: $_[0]\n";
	close TL;
}

# sleep
sub mssleep
{
	my $ms = $_[0];
	select (undef, undef, undef, $ms/1000.);
}

