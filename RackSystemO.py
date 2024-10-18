import odrive
from odrive.enums import *
import time
import math

#Defines a function for pausing the code until the axis state is set back to IDLE
#Used for waiting for a command such as calibration to be completed
def Wait_For_Axis_IDLE():
    while my_drive.axis0.current_state != AXIS_STATE_IDLE:
        time.sleep(0.1)

#Defines a function that searches for a Odrive connected to USB port
def Find_Odrive():
	print("Finding ODrive...CTRL + C to Cancel....")
	my_drive = odrive.find_any()
	if my_drive != 0:
		print("Found")
	return my_drive

#Defines a function that will erase and reconfigure all the base settings for the Odrive controller
def Configure():
	try:
		my_drive.erase_configuration()
	except:
		my_drive = Find_Odrive()
		my_drive.axis0.motor.config.current_lim = 50
		my_drive.axis0.controller.config.vel_limit = 20
		my_drive.axis0.motor.config.calibration_current = 15
		my_drive.config.enable_brake_resistor = False
		my_drive.config.dc_max_negative_current = -60
		my_drive.axis0.motor.config.pole_pairs = 7
		my_drive.axis0.motor.config.torque_constant = 0.030629629629629
		my_drive.axis0.motor.config.motor_type = MOTOR_TYPE_HIGH_CURRENT
		my_drive.axis0.encoder.config.cpr = 8192
		my_drive.axis0.controller.config.vel_gain = 0.16
		my_drive.axis0.controller.config.pos_gain = 10
		my_drive.axis0.controller.config.vel_integrator_gain = 0.1
		my_drive.axis0.encoder.config.use_index = True
		my_drive.axis0.motor.config.pre_calibrated  = True
		Calibrate()
		try:
			my_drive.save_configuration()
		except:
			my_drive = Find_Odrive()
			print("Configured")

#Defines a function for calibrating the encoder and motor MUST BE RUN EVERYTIME THE CONTROLLER IS POWERED ON
#If run fails there could be an error check odrivetool dump_errors(odrv0)
#Calibration errors can come from loading of the motor under calibration,
#Incorrectly set configuration, and if the encoder is to slip on the motor shaft
def Calibrate():
	print("Starting Calibration....Remove All Mechanical Load From Motor...")
	my_drive.clear_errors()
	my_drive.axis0.requested_state = AXIS_STATE_MOTOR_CALIBRATION
	Wait_For_Axis_IDLE()
	my_drive.axis0.requested_state = AXIS_STATE_ENCODER_INDEX_SEARCH
	Wait_For_Axis_IDLE()
	my_drive.axis0.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
	Wait_For_Axis_IDLE()
	print("Calibration Completed")

#Defines a function for runing the motor in cycles
#Input parameters for velocity acceleration inertia and distance are in this section
def Run(cycles):
	print("Starting Movement")
	my_drive.axis0.trap_traj.config.vel_limit = V
	my_drive.axis0.trap_traj.config.accel_limit = A
	my_drive.axis0.trap_traj.config.decel_limit = A
	my_drive.axis0.controller.config.inertia = I
	my_drive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
	my_drive.axis0.controller.config.input_mode = INPUT_MODE_TRAP_TRAJ
	while cycles > 0:
		if (cycles % 2) == 0:
			my_drive.axis0.controller.move_incremental(-20, False)	
		else:
			my_drive.axis0.controller.move_incremental(20, False)
		Completed = my_drive.axis0.controller.trajectory_done
		while Completed == 0:
			time.sleep(.1)
			Completed = my_drive.axis0.controller.trajectory_done
		cycles = cycles - 1
	my_drive.axis0.requested_state = AXIS_STATE_IDLE
	print("movement complete")
#Changes The Parameters for the Run Command While the Code is Running
#Does NOT save user inputs resets to default EACH time the code is run
def RunParameters():
	TuneInput = input("\nThese changes will not be saved and will be reset when the code is run again...\n1:Acceleration Rotations/S Default:5 2:Velocity Rotations/S Default:.5 3:Inertia Default:.1 m:Main Menu q:Quit\n")
	if TuneInput == "1":
		global A
		A = input("\nAcceleration:")
		Tune()
	if TuneInput == "2":
		global V
		V = input("\nVelocity:")
		Tune()
	if TuneInput == "3":
		global I
		I = input("\nInertia:")
		Tune()
	if TuneInput == "m":
		Main()
	if TuneInput == "q":
		print("Quitting...")
#Defines the main function to take user inputs and run the other functions
def Main():
	MainInput = input("\nCalibrate Everytime Rack System is disconnected\n\n1:Run Mode 2:Calibration Mode 3:Configure Mode 4:Run Parameters Mode q:Quit\n") 
	if MainInput == "1":
		cycles = int(input("Number of Cycles Integer ONLY\n")) * 2 
		Run(cycles)
		Main()
	if MainInput == "2":
		Calibrate()
		Main()
	if MainInput == "3":
		Configure()
		Main()
	if MainInput == "4":
		RunParameters()
	if MainInput == "q":
		print("Quitting...")

my_drive = Find_Odrive()
I = .1
V = .5
A= 5
Main()
