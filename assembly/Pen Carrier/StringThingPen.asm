;***********************************************************************************************
;*
;* StringThingPen.asm - String Thing Prototype Main Source File
;*
;* Author	John A. Anderson
;*
;***********************************************************************************************
;*
;* Revision History
;*
;***********************************************************************************************
;* 
;* 2/11/2012 - initial version
;* 2/25/2012 - changed the serial command structure to three bytes
;*
;***********************************************************************************************

	#include <P16F688.INC>

;*	Constants

;* these four are new for version 2.0, and used to define states in the command structure
;* state machine and the value of the start byte in the command structure

#define WFStart	H'00'		; state value for first byte - start byte
#define CHKID	H'01'		; state value for second byte - address
#define CHKCMD	H'02'		; state value for third byte - command byte

#define STByte	H'80'		; the value of the start byte

#define	BoxAddr	H'00'		; EE location where box address is kept

#define	BANK1	banksel 0x80	;Select Bank 1
#define	BANK0	banksel	0x00	;Select Bank 0

#define ShortPulse	H'C1'
#define LongPulse 	H'83'

;*	Variables

	cblock	H'20'

		RCPulseLen			; this is the current coil status set to motor

		ExecuteCmd			; this is the command to execute (0 = none)
		CmdData				; this is the data to use for some commands
		ActiveAddr			; this is the box address used to listen for serial commands

;* In version 2.0 this was changed from active flag to state machine variable
;-		CmndActive			; this is a flag indicator the master is talking to us
		CURState			; this is the current state of the command state machine
		
		WTemp				; these are temp storage for the interrupt routine
		StatusTemp
		FSRTemp
		SerialTemp

	endc	

	code

;*	reset vector
	org 	H'0000'
	goto	Setup

;*	interupt handler
	org		H'0004'
Handler
	movwf 	WTemp			; store the W register
	movf 	STATUS,W
	movwf 	StatusTemp		; store the Status register
	movf	FSR, w
	movwf	FSRTemp			; store the FSR register

	banksel	PIR1
	btfsc	PIR1, TMR1IF	; test for timer one interrupt
	goto	timeroneint
	btfsc	PIR1, RCIF		; test for serial recv interrupt
	goto	serialint
	banksel	INTCON
	btfsc	INTCON, T0IF	; test for timer zero interrupt
	goto	timerzeroint
	goto	AllDone			; if it's none of these, give up

timeroneint
	banksel	TMR1L
	clrf	TMR1L
	movlw	H'B1'			; reset timer one for another 16ms
	banksel	TMR1H
	movwf	TMR1H
	BANK0
	movf	RCPulseLen, w	; set timer zero for the current pulse
	banksel	TMR0
	movwf	TMR0
	banksel	PIR1
	bcf		PIR1, TMR1IF	; clear the timer one interrupt
	banksel	INTCON
	bcf		INTCON,	TMR0IF	; and enable timer zero interrupt
	bsf		INTCON, TMR0IE
	banksel	PORTC
	bsf		PORTC, 0		; set the RC signal pin
	goto	AllDone

timerzeroint
	banksel	INTCON
	bcf		INTCON, T0IE	; clear the timer zero interrupt
	bcf		INTCON, T0IF	; and disable it
	banksel	PORTC
	bcf		PORTC, 0		; the clear the RC signal pin
	goto	AllDone

serialint
	Banksel	RCREG			; if this falls through, must be serial interrupt
	movf	RCREG, w		; get the data out to keep from over-flowing
	movwf	SerialTemp

;* in version 2.0 all this code is replaced with the state machine code
;*
;-	btfss	SerialTemp, 6	; if the 6 bit is set this is an address byte
;-	goto	TestCommand
;-
;-	btfsc	SerialTemp, 4	; if the 4 bit is set this is a set address command
;-	goto	MyCommand
;-
;-	movf	ActiveAddr, w	; get my address
;-	xorwf	SerialTemp, f
;-	movlw	H'0F'			; mask off the upper four bits
;-	andwf	SerialTemp, f
;-	btfss	STATUS, Z
;-	goto	NotMyCmnd		; if the addresses don't match - clear the active bit
;-	bsf		CmndActive, 0	; if the addresses do match - set the active bit
;-	clrf	ExecuteCmd		; so the next byte will come to us.
;-	goto	AllDone
;-
;-NotMyCmnd
;-	bcf		CmndActive, 0
;-	clrf	ExecuteCmd
;-	goto	AllDone
;-
;-TestCommand
;-	btfss	CmndActive, 0	; if the bit is set the command is for us
;-	goto	NotMyCmnd
;-
;-MyCommand
;-	movf	SerialTemp, w	; if I got to this point I know I'm the active box and
;-	movwf	ExecuteCmd		; I have received a valid command
;-	clrf	CmndActive

	BANK0
	movlw 	high StateJMP	; set high order byte of program
	movwf 	PCLATH 			; counter appropriately
	movf 	CURState, W 	; recall the character
	addlw 	low StateJMP	; add command variable to ROM address
	btfsc 	STATUS, C 		; beginning command Table
	incf 	PCLATH, F 		; overflows? yes, increment PCLATH
	movwf 	PCL 			; move computed goto value into PC

StateJMP

	goto	CheckForStart
	goto	CheckAddress
	goto	SetCommand

CheckForStart
	movlw	STByte			; get the value of the start byte
	xorwf	SerialTemp, w	; compare the value with the character received
	btfss	STATUS, Z		
	goto	AllDone			; if they're not equal quit
	movlw	CHKID			; if they are, we've received a start byte, so 
	movwf	CURState		; transition to the next state
	goto	AllDone

CheckAddress
	movf	ActiveAddr,w	; get the value of the active address
	xorwf	SerialTemp, w	; compare the value with the character received
	btfss	STATUS, Z		
	goto	NotForMe		; if they're not equal go back
	movlw	CHKCMD			; if they are, we've received our address, so 
	movwf	CURState		; transition to the next state
	goto	AllDone
NotForMe
	movlw	WFStart			; go back to looking for another start
	movwf	CURState
	goto	AllDone

SetCommand
	movf	SerialTemp, w	; this is the command byte
	andlw	H'07'			; this masks all but the command bits
	iorlw	H'80'			; set the command active bit
	movwf	ExecuteCmd		; and save it
	swapf 	SerialTemp, w	; get the command byte again to get the data
	andlw	H'07'			; this masks all but the data bits
	movwf	CmdData			; and save it

AllDone
	movf	FSRTemp, w		; restore the FSR Register
	movwf	FSR
	movf 	StatusTemp, W	; restore the STATUS Register
	movwf 	STATUS
	swapf 	WTemp, f		; restore the W Register 
	swapf 	WTemp, W		; without affecting STATUS
	retfie

;*	main code
Setup

	movlw	H'70'			; set up for 8MHz
	Banksel	OSCCON
	movwf	OSCCON

	movlw	H'3E'			; setup the four motor coil outputs
	Banksel	TRISC
	movwf	TRISC

	movlw	H'3F'			; set port A to all inputs
	Banksel	TRISA
	movwf	TRISA

	Banksel	ADCON0			; turn off the a/d converter
	bcf		ADCON0, ADON

	movlw	B'00000111'		; turn off the comparator and set i/o to digital
	Banksel	CMCON0
	movwf	CMCON0

	Banksel	ANSEL			; turn off all analog inputs
	clrf	ANSEL

	banksel	IOCA			; turn off all the interrupt on change
	clrf	IOCA

	movlw 	BoxAddr			; read the box address from EEPROM and save in RAM
	BANKSEL	EEADR
	movwf	EEADR 			; Data Memory Address to read
	Banksel	EECON1
	bcf 	EECON1, EEPGD 	; Point to DATA memory
	bsf 	EECON1, RD 		; Start the EE Read
	nop						; these two nops give the EE controler time to read
	nop
	Banksel	EEDAT
	movf 	EEDAT, w 		; get the box address after it's been read and
	BANK0
	andlw	H'0F'			; only lower nibble is significant
	movwf	ActiveAddr		; save it in ram for later use

	Banksel	BAUDCTL			; setup the baud rate on the eusart
	bcf		BAUDCTL, BRG16	; set 8-bit timer mode
	Banksel	TXSTA
	bsf		TXSTA, BRGH		; set high speed baud rate
	bcf		TXSTA, SYNC		; set ansych mode
	movlw	H'67'			; timer value for 4.8k baud
	Banksel	SPBRG
	movwf	SPBRG

	Banksel	RCSTA
	bcf		RCSTA, RX9		; set 8 bit data
	bsf		RCSTA, SPEN		; enable the receiver
	bsf		RCSTA, CREN		; enable continuous reception

	Banksel	TXSTA
	bcf		TXSTA, TX9		; set 8 bit data
	bsf		TXSTA, TXEN		; enable the transmitter

	banksel	TMR1L			; set up timer one for 10ms roll over
	clrf	TMR1L
	movlw	H'B1'
	banksel	TMR1H
	movwf	TMR1H
	movlw	H'05'
	banksel	T1CON
	movwf	T1CON

	movlw	ShortPulse		; set up timer zero for .5ms roll over
	BANK0
	movwf	RCPulseLen		; set up the variable
	banksel	TMR0
	movwf	TMR0			; then set up the timer
	movlw	H'84'
	banksel	OPTION_REG
	movwf	OPTION_REG

	banksel	PIE1
	bsf		PIE1, TMR1IE	; enable timer one interrupt
	bsf		PIE1, RCIE		; enable receiver interrupt
	banksel	INTCON
	bcf		INTCON, TMR0IE	; disable timer zero interrupts
	bsf		INTCON, PEIE	; enable periphreal interrupts
	bsf		INTCON, GIE		; enable global interrupts

Loop
;	movf	ExecuteCmd, w
;	andlw	H'FF'
;	btfsc	STATUS, Z
;	goto 	Loop			; if the ExecuteCmd is zero wait
;	
;	btfsc	ExecuteCmd, 4	; if this bit is set this is a set address command
;	goto	SetAddress
;	btfsc	ExecuteCmd, 0	; if the 0 bit of the command is set long pulse
;	goto	GetLong
;	movlw	ShortPulse			; short pulse code
;	movwf	RCPulseLen
;	clrf	ExecuteCmd
;	goto	Loop
;GetLong
;	movlw	LongPulse			; long pulse code
;	movwf	RCPulseLen
;	clrf	ExecuteCmd
;	goto	Loop

	BANK0
	btfss	ExecuteCmd, 7	; if there's an active command this will be set
	goto	Loop
	movlw 	high Commands	; set high order byte of program
	movwf 	PCLATH 			; counter appropriately
	movf 	ExecuteCmd, W 	; recall the command
	andlw	H'07'			; ensure the command is valid
	addlw 	low Commands	; add command variable to ROM address
	btfsc 	STATUS, C 		; beginning command Table
	incf 	PCLATH, F 		; overflows? yes, increment PCLATH
	movwf 	PCL 			; move computed goto value into PC

Commands
	goto	MotorOn
	goto	MotorOff
	goto	StepIn
	goto	StepOut
	goto	SetAddress
	goto	CmdDone
	goto	CmdDone
	goto	CmdDone

MotorOn
	goto	CmdDone

MotorOff
	goto	CmdDone

StepIn
	movlw	ShortPulse			; short pulse code
	movwf	RCPulseLen
	goto	CmdDone

StepOut
	movlw	LongPulse			; long pulse code
	movwf	RCPulseLen
	goto	CmdDone

SetAddress
	MOVLW 	BoxAddr
	BANKSEL	EEADR
	MOVWF 	EEADR 			; Data Memory Address to write
	BANK0
	movf	CmdData, w
	andlw	H'07'			; mask the bits to get the address
	movwf	ActiveAddr
	Banksel	EEDAT
	MOVWF 	EEDAT 			; Data Memory Value to write
	Banksel	EECON1
	BCF 	EECON1, EEPGD 	; Point to DATA memory
	BSF 	EECON1, WREN 	; Enable writes
	Banksel	INTCON
CheckDisable
	bcf		INTCON, GIE		; disable interrupts to start write cycle
	BTFSC 	INTCON, GIE 	; SEE AN576
	GOTO 	CheckDisable
	Banksel	EECON2
	MOVLW 	H'55'
	MOVWF 	EECON2 			;Write 55h
	MOVLW 	H'AA'
	MOVWF 	EECON2 			;Write AAh
	BSF 	EECON1, WR 		;Set WR bit to begin write
	Banksel	INTCON
	bsf		INTCON, GIE		; reenable interrrupts
WaitForWrite
	Banksel	EECON1
	btfsc	EECON1, WR
	goto	WaitForWrite
	BCF 	EECON1, WREN 	;Disable writes

CmdDone
	BANK0
	clrf	ExecuteCmd		; get rid of the old command
	movlw	WFStart			; reset the state machine
	movwf	CURState
	goto	Loop			; and start over

	end