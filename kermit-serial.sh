#! /usr/bin/kermit +
;
; copy this to ~/bin/kermit-serial and make executable!
;
set modem type none
set line /dev/ttyUSB0
set carrier-watch off
set speed 9600
if defined \%1 set speed \%1
set flow rts/cts
eightbit
; set parity none
set stop-bits 1
connect
