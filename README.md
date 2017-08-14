# newrealm
This file need to automate some routine settings of clients server installation.
Here install necessary version of Asterisk server and some additional software from Goantifraud service.

# sbo_online <br>
Sbo mean softswitch bandwith optimization (for country with low bandwith of channel and using SIP protocol with VoIP gateways). <br>
First this script going to central project database and takes necessary data like user_database, user_database_ip, user_server_name, user_server_ip etc using psycobg2. <br> After checking data correct creating sip_peer, iax_peer to connect server side and local server side(in user local network), dialplan of user Asterisk local server. <br>
Also using psycobg2 changing data from user (not central) database. <br>
Script execution with keys (sip/iax) mean creating one of configurations from local server side. <br>
