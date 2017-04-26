#!/bin/bash

service mysql start
/root/openair-cn/SCRIPTS/hss_db_create localhost root hurka root hurka oai_db
son-vm-server -c server.conf -v
