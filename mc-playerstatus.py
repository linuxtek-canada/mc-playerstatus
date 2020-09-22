#!/usr/bin/python3

# This is the mc-playerstatus main script.  Check to see how many users are on the server.  If there are 0 players for over 30 minutes, shut down the server.
# This script is intended to run from 12AM-8AM EST to save compute on GCP

# Uses mcstatus to query the remote server:  https://github.com/Dinnerbone/mcstatus
# This will need to be installed on the system and added to the default path

# SSH Keys will already need to be copied to the remote server so the script is able to log in using the public key - ssh-copy-id or other method.
# SSH passwords are not supported via this method.

import mcstatus
import subprocess
import re
import time
import math
from datetime import datetime
import logging

#Edit these values
server_name = "minecraft.linuxtek.ca"                       #Server to monitor
server_username = "minecraft"                               #User to SSH into the server as.
server_ssh_id_path = "/home/minecraft/.ssh/id_rsa"      #Path to SSH Public Key
shutdown_threshold = 10                                     #In Minutes
check_interval = 1                                          #In Minutes
start_hour = 13                                             #Hour the script is valid to run from - Midnight
stop_hour = 23                                              #Hour the script is valid to run until - 8AM


#Log Init - Adjust logging level if needed
logging.basicConfig(filename='mc-playerstatus.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

#Script Start
shutdown_count = 0
error_count = 0
error_threshold = 10

logging.info('#####################################################')
logging.info('Script Startup.  Shutdown Count = %s.', shutdown_count)
logging.info('#####################################################')

this_hour = datetime.now().hour
logging.debug("The current hour is %s",this_hour)

while True:
    #Check if the script is running between the set hours.  If not, exit successfully
    if ((this_hour >= start_hour) and (this_hour <= stop_hour)):
        logging.debug("The script will run during this time.")
    else: 
        logging.info("The script should not be running.")
        logging.debug("Exiting with code 0 successful")
        exit(0)

    #Ping the server using mcstatus.
    mcstatus_ping = subprocess.run(['mcstatus', server_name, 'ping'], capture_output=True, encoding="utf-8")
    ping_time = mcstatus_ping.stdout

    if (mcstatus_ping.returncode == 0): 
        logging.debug('The ping was successful.')
        logging.info('The ping time was %s.',ping_time.strip())
          
        #If the ping is successful, query the server and parse out the number of players.
        mcstatus_query = subprocess.run(['mcstatus', server_name, 'query'], capture_output=True, encoding="utf-8")

        if (mcstatus_query.returncode == 0):
            logging.debug('The query was successful.')
            player_count = re.search('players: (\d+)',mcstatus_query.stdout).group(1)
            player_count = int(player_count.strip())
            
            player_count = 0 #DEBUG ONLY

            logging.info('The Player Count Is %s', player_count)
        else:
            logging.warning('The query was unsuccessful.  Server is offline or not responding to query.')
            error_count = error_count + 1
            logging.warning('Incrementing Error Count to %s.',error_count)
    
        #If there are no players on the server, increment the shutdown count.  If there are players, reset the shutdown count.
        if (player_count == 0):
            shutdown_count = shutdown_count + 1
            logging.debug('No players on the server.  Incrementing shutdown value to %s.',shutdown_count)
        elif (player_count >= 1):
            shutdown_count = 0
            logging.debug('%s players on the server.  Resetting shutdown value to %s.',player_count, shutdown_count)

        #Check if the script has encountered too many errors.  If so, exit.
        if (error_count > error_threshold):
            logging.warning('Too many errors.  Exiting script, reporting failure.')
            exit(1)

        #Check if the shutdown threshold has been reached - adjusted for check interval
        if (shutdown_count >= math.ceil(shutdown_threshold / check_interval)):
            logging.debug("Shutdown Count:  %s, Shutdown Threshold: %s",shutdown_count, shutdown_threshold)
            logging.info("Shutdown threshold has been reached.  Shutting down the server.")
            logging.debug("Attempting to run backup script.")

            #Run SSH command on Minecraft server to run backup script - this will need to be optional for anyone who doesn't run such a script.
            #This section may need to be commented out, or the COMMAND changed to something non-critical.  Leaving Hello World test command as an option.
            #COMMAND = "echo 'Hello World' >> /home/minecraft/test.txt"

            COMMAND = "/home/minecraft/mc-backup.sh"
            ssh = subprocess.Popen(['ssh', '-i', server_ssh_id_path, "{}@{}".format(server_username,server_name), COMMAND],shell=False,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            res = ssh.communicate()
            logging.debug("Subprocess Return Code: %s",ssh.returncode)
            logging.debug("Result: %s",res)
            logging.debug("Standard Error: %s",res[1])
            
            if ssh.returncode == 0:
                logging.info("The backup script was successfully run")
                exit(0)
            else:
                logging.warning("The backup script failed to run.  Server will not be shut down.")
                shutdown_count = 0
                logging.warning("Resetting Shutdown Count to %s",shutdown_count)
               
            #If the server

    else:
        #If the ping is unsuccessful, increment the error count.
        logging.warning("The ping was unsuccessful.  Server is offline or not responding to ping.")
        error_count = error_count + 1
        logging.warning("Incrementing Error Count to %s.", error_count)

    logging.debug("Sleeping for check interval - %s minutes", check_interval)
    
    time.sleep(1) #DEBUG ONLY
    #time.sleep(check_interval * 60)
