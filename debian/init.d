#! /bin/sh
### BEGIN INIT INFO
# Provides:          analytics-server
# Required-Start:    mysql
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Analytics Server Daemon
# Description:       Collects analytics information.
# X-Start-Before:
# X-Stop-After:
### END INIT INFO

# Author: M.Angel Juan <m.angel.juan@gmail.com>

PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="analytics server daemon"
NAME=analyticsd
DAEMON=/usr/sbin/"$NAME"
PIDFILE=/var/run/"$NAME".pid
SCRIPTNAME=/etc/init.d/lliurex-analytics-server
LOCK_FILE=/var/run/"$NAME".lock

# Exit if the package is not installed
[ -x "$DAEMON" ] || exit 0

# Define LSB log_* functions.
. /lib/lsb/init-functions

remove_locks()
{
    if [ -f "${LOCK_FILE}" ]; then
        log_success_msg "Removing lockfile ${LOCK_FILE}"
        rm -f ${LOCK_FILE}
    fi
}
#
# Function that starts the daemon/service
#
do_start()
{
	# Return
	#   0 if daemon has been started
	#   1 if daemon was already running
	#   2 if daemon could not be started
	start-stop-daemon --start -N -1 --quiet --pidfile "$PIDFILE" --startas "$DAEMON" -- \
		$EXTRAOPTIONS \
		|| return 2
}

#
# Function that stops the daemon/service
#
do_stop()
{
	# Return
	#   0 if daemon has been stopped
	#   1 if daemon was already stopped
	#   2 if daemon could not be stopped
	#   other if a failure occurred
	start-stop-daemon --stop --quiet --retry=INT/15/TERM/15 --pidfile "$PIDFILE"
	RETVAL="$?"
	[ "$RETVAL" = 2 ] && \
	start-stop-daemon --stop --quiet --oknodo --retry=TERM/15/KILL/15 --pidfile "$PIDFILE"
	[ "$?" = 2 ] && return 2
	# Many daemons don't delete their pidfiles when they exit.
	rm -f "$PIDFILE"
	remove_locks
	return "$RETVAL"
}

#
# Function that sends a SIGHUP to the daemon/service
#
do_reload() {
	do_stop
	do_start
	return 0
}

case "$1" in
  start)
	log_daemon_msg "Starting $DESC" "$NAME"
	do_start
	case "$?" in
		0|1) log_end_msg 0 ;;
		2) log_end_msg 1 ;;
	esac
	;;
  stop)
	log_daemon_msg "Stopping $DESC" "$NAME"
	do_stop
	case "$?" in
		0|1) log_end_msg 0 ;;
		2) log_end_msg 1 ;;
	esac
	;;
  reload|force-reload)
	log_daemon_msg "Reloading $DESC" "$NAME"
	do_reload
	log_end_msg $?
	;;
  restart)
	log_daemon_msg "Restarting $DESC" "$NAME"
	do_stop
	case "$?" in
	  0|1)
		do_start
		case "$?" in
			0) log_end_msg 0 ;;
			1) log_end_msg 1 ;; # Old process is still running
			*) log_end_msg 1 ;; # Failed to start
		esac
		;;
	  *)
		# Failed to stop
		log_end_msg 1
		;;
	esac
	;;
  status)
	pidofproc -p "$PIDFILE" "$DAEMON" >/dev/null
	status=$?
	if [ $status -eq 0 ]; then
		log_success_msg "$NAME is running."
	else
		log_failure_msg "$NAME is not running."
	fi
	exit $status
	;;
  *)
	echo "Usage: $SCRIPTNAME {start|stop|restart|reload|force-reload|status}" >&2
	exit 3
	;;
esac

:
