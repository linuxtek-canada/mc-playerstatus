#!/usr/bin/python3

# This is the mc-playerstatus main script.  Check to see how many users are on the server.  If there are 0 players for over 30 minutes, shut down the server.
# This script is intended to run from 12AM-8AM EST to save compute on GCP

# Uses mcstatus to query the remote server:  https://github.com/Dinnerbone/mcstatus

import mcstatus
import subprocess
import re
import time
import logging

#Edit these values
server_name = "minecraft.linuxtek.ca"   #Server to monitor
shutdown_threshold = 30                 #In Minutes
check_interval = 5                      #In Minutes

#Log Init - Adjust logging level if needed
logging.basicConfig(filename='mc-playerstatus.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

#Script Start
shutdown_count = 0
logging.info('Script Startup.  Shutdown Count = %s', shutdown_count)

mcstatus_ping = subprocess.run(['mcstatus', server_name, 'ping'], capture_output=True, encoding="utf-8")
ping_time = mcstatus_ping.stdout

if mcstatus_ping.returncode == 0: 
    logging.debug('The ping was successful')
    logging.info('The ping time was %s',ping_time)
    
    mcstatus_query = subprocess.run(['mcstatus', server_name, 'query'], capture_output=True, encoding="utf-8")
    if mcstatus_query.returncode == 0:
        logging.debug('The query was successful')
        player_count = re.search('players: (\d+)',mcstatus_query.stdout).group(1)
        logging.info('The Player Count Is %s', player_count.strip())
        
else:
    logging.warning('The ping was unsuccessful')

