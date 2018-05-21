# newrealm
This file need to automate some routine settings of clients server installation.
Here install necessary version of Asterisk server and some additional software from Goantifraud service.

# sbo_online <br>
Sbo mean softswitch bandwith optimization (for country with low bandwith of channel and using SIP protocol with VoIP gateways). <br>
First this script takes access to central project database and receives necessary data like user_database, user_database_ip, user_server_name, user_server_ip etc using psycobg2. <br> After checking data for correctness script is creating sip_peer, iax_peer to connect to server side and local server side(in user local network), dialplan of user Asterisk local server configuring. <br>
Also using psycobg2 script is changing data from user (not central) database. <br>
Script execution with keys (sip/iax) mean creating one of configurations from local server side. <br>
