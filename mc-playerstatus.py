#!/usr/bin/python3

#Author:    Jason Paul 
#Email:     jasonpa@gmail.com

# This is the mc-playerstatus main script.  Check to see how many users are on the server.  If there are 0 players for over 30 minutes, shut down the server.
# This script is intended to run from 12AM-8AM EST to save compute on GCP

# Uses mcstatus to query the remote server:  https://github.com/Dinnerbone/mcstatus
# This will need to be installed on the system and added to the default path

# SSH Keys will already need to be copied to the remote server so the script is able to log in using the public key - ssh-copy-id or other method.
# SSH passwords are not supported via this method.

import subprocess
import re
import os
import sys
import time
import math
from datetime import datetime
from mcstatus import MinecraftServer
import logging

#Edit these values
server_name = "minecraft.linuxtek.ca"                       #Minecraft server port to monitor
server_port = "25565"                                       #Query port for Minecraft server
server_username = "minecraft"                               #User to SSH into the server as
server_ssh_id_path = "/home/minecraft/.ssh/id_rsa"          #Path to SSH public key
shutdown_threshold = 10                                     #How many times the query finds 0 users on the Minecraft server before triggering shutdown
check_interval = 1                                          #How often to check player count, in minutes
start_hour = 13                                             #Hour the script is valid to run from
stop_hour = 23                                              #Hour the script is valid to run until
error_threshold = 10                                        #How many errors the script encounters on its loop before being shut down

def script_startup():

    #Initialize Logging
    logging.basicConfig(filename='mc-playerstatus.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    #Initialize Variables
    global shutdown_count
    global error_count

    shutdown_count = 0
    error_count = 0 


    #Initialize PIDFile 
    pid = str(os.getpid())
    global pidfile 
    pidfile = "/tmp/mc-playerstatus.pid"

    logging.info('#####################################################')
    logging.info('Script Starting with PID %s.  Shutdown Count = %s.', pid, shutdown_count)
    logging.info('#####################################################')

    #Check if PID File already exists.
    if os.path.isfile(pidfile):
        logging.debug("PID File %s already exists.  Script is already running.  Exiting.", pidfile)
        script_shutdown(1);

    else:
        open(pidfile, 'w').write(pid)
        logging.debug("PID File %s written.", pidfile)

def time_check():
    this_hour = datetime.now().hour
    logging.debug("The current hour is %s",this_hour)

    #Check if the script is running between the set hours.  If not, exit successfully.
    if ((this_hour >= start_hour) and (this_hour <= stop_hour)):
        logging.info("The script will run during this time.")
    else: 
        logging.warning("The script should not be running.")
        script_shutdown(1);

def script_shutdown(exitcode):
    
    logging.info("Script shutting down.  Removing PID file.")
    os.remove(pidfile)

    if exitcode == 0:
        logging.info("Shutting down script without errors, Exitcode = %s", exitcode)
        exit(0)

    elif exitcode == 1:
        logging.info("Shutting down script with errors, Exit Code = %s.", exitcode)
        exit(1)
    return

def mcstatus_ping():
    global server
    server = MinecraftServer(server_name,server_port)
    latency = server.ping()
    
    if (latency.returncode == 0):
        logging.debug('The ping was successful.')
        logging.info('The ping time was %s ms.',latency)
        return 0
    else:
        #If the ping is unsuccessful, increment the error count.
        logging.warning("The ping was unsuccessful.  Server is offline or not responding to ping.")
        error_count = error_count + 1
        logging.warning("Incrementing Error Count to %s.", error_count)
        return 1

def mcstatus_query():
    status = server.status()
    if (status.returncode == 0):
        logging.debug("The query was successful.")
        players = int(status.players.online)
        logging.info("The player count is %s.",players)
        return players
    else:
        #If the query is unsuccessful, increment the error count.
        logging.warning("The query was unsuccessful.  Server is offline or not able to be queried.  Check the query port.")
        error_count = error_count + 1
        logging.warning("Incrementing Error Count to %s.", error_count)
        return 0

def check_thresholds():

    #Check if the script has encountered too many errors.  If so, exit.
    if (error_count > error_threshold):
        logging.warning('Too many errors.  Exiting script, reporting failure.')
        script_shutdown(1)

    #Check if the shutdown threshold has been reached - adjusted for check interval
    if (shutdown_count >= math.ceil(shutdown_threshold / check_interval)):
        logging.debug("Shutdown Count:  %s, Shutdown Threshold: %s",shutdown_count, shutdown_threshold)
        logging.info("Server shutdown threshold has been reached.  Shutting down the server.")
        logging.debug("Attempting to run backup script.")

        #Run SSH command on Minecraft server to run backup script - this will need to be optional for anyone who doesn't run such a script.
        #This section may need to be commented out, or the COMMAND changed to something non-critical.  Leaving Hello World test command as an option.
        #command_text = "bash /home/minecraft/mc-backup.sh"

command_text = "echo 'Hello World' >> /home/minecraft/test.txt"  #DEBUG ONLY
        if SSHCommand(command_text) == 0:
        






def SSHCommand(command):
    ssh = subprocess.Popen(['ssh', '-i', server_ssh_id_path, "{}@{}".format(server_username,server_name), command],shell=False,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res = ssh.communicate()
    return res 

script_startup();
 
while True:

    time_check();

    if (mcstatus_ping(),0):
        player_count = mcstatus_query()
        if (player_count == 0):
            #If there are no players on the server, increment the shutdown count.  If there are players, reset the shutdown count.
            shutdown_count = shutdown_count + 1
            logging.info('No players on the server.  Incrementing shutdown value to %s.',shutdown_count, player_count)
        else:
            shutdown_count = 0
            logging.info('%s player(s) on the server.  Resetting shutdown value to %s.')

        check_thresholds()

            #Run SSH command on Minecraft server to run backup script - this will need to be optional for anyone who doesn't run such a script.
            #This section may need to be commented out, or the COMMAND changed to something non-critical.  Leaving Hello World test command as an option.
           
           #COMMAND = "bash /home/minecraft/mc-backup.sh"
            COMMAND = "echo 'Hello World' >> /home/minecraft/test.txt"  #DEBUG ONLY


            ssh = subprocess.Popen(['ssh', '-i', server_ssh_id_path, "{}@{}".format(server_username,server_name), COMMAND],shell=False,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            res = ssh.communicate()
            logging.debug("Subprocess Return Code: %s",ssh.returncode)

            #Note:  The below debug lines will pull all of the script console information in the log unformatted.  Only use if you must debug the backup script.  Better to do this locally.
            #logging.debug("Result: %s",res)
            #logging.debug("Standard Error: %s",res[1])
            
            if ssh.returncode == 0:
                logging.info("The backup script was successfully run")
            else:
                logging.warning("The backup script failed to run.  Server will not be shut down.")
                shutdown_count = 0
                logging.warning("Resetting Shutdown Count to %s",shutdown_count)
               
            #If the backup succeeds, proceed to shutdown the server.
            logging.info("Attempting to shut down the server...")
            #COMMAND = "sudo shutdown -h now"
            COMMAND = 'echo "Hello World" >> test.txt'  #DEBUG ONLY

            ssh = subprocess.Popen(['ssh', '-i', server_ssh_id_path, "{}@{}".format(server_username,server_name), COMMAND],shell=False,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            res = ssh.communicate()
            logging.debug("Subprocess Return Code: %s",ssh.returncode)
            
            if ssh.returncode == 0:
                logging.info("Server %s shut down successfully",server_name)
                os.remove(pidfile)
                exit(0)
            else:
                logging.warning("Server shutdown was unsuccessful.")
                logging.debug("Incrementing Error Count to %s.",error_count)
                error_count = error_count + 1
    else:
        #If the ping is unsuccessful, increment the error count.
        logging.warning("The ping was unsuccessful.  Server is offline or not responding to ping.")
        error_count = error_count + 1
        logging.warning("Incrementing Error Count to %s.", error_count)

    logging.debug("Sleeping for check interval - %s minutes", check_interval)
    
    time.sleep(1) #DEBUG ONLY
    #time.sleep(check_interval * 60)
