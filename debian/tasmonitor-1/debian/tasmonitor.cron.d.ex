#
# Regular cron jobs for the co2sens package
#
0 4	* * *	root	[ -x /usr/bin/co2sens_maintenance ] && /usr/bin/co2sens_maintenance
