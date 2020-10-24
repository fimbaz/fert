#
# Regular cron jobs for the ppmsens package
#
0 4	* * *	root	[ -x /usr/bin/ppmsens_maintenance ] && /usr/bin/ppmsens_maintenance
