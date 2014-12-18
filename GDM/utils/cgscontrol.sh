#!/bin/env bash

# TODO Resolve pid_file issue. Currently uses default Config dir defined in settings.example.py
# but there is no way of picking up changes to this unless is is defined in the env
# and picked up by settings.py, but this would split the config. Can we use a python one liner to pick it up?

# TODO Move all output including pids files to OUTPUT_DIR

# For now this is now located within the APP_INS_DIR, so this should be added to to the $PATH in init_epi_env.sh
# TODO Add instance support, to allow this script to control multiple instances based on separated settings/config

stopServer(){
  local server_type=$1
  local file_pid=$(getServerPID $server_type)

  if [ $file_pid ]; then
    local running_pid=$(isPIDrunning $file_pid)

    if [[ ! -z $(isPIDrunning $file_pid)  ]]; then

      if [[ ! $ACTION =~ ^(stop|restart)$ ]]; then
        echo "$server_type is already running, please specify 'restart' argument"
        exit 1
      fi

      echo "Stopping running $server_type with PID $file_pid"
      kill $file_pid || exit 1
      #appears there is no way to capture or supress the 'Terminated'
      #using subshell or /dev/null
      #message here, so let's just make it appear in sequence
      sleep 1
      echo ""

    elif [[ $ACTION == stop ]]; then
      echo "$server_type is not currently running"
    fi
  elif [[ $ACTION == stop ]]; then
    echo "Failed to get $server_type PID from CGSServers.pid.txt"
  fi
}

startServer(){
  local server_type=$1
  local out_file=${OUTPUT_DIR}/${server_type}.out
  local server_path=${APP_INS_DIR}/EpiExplorer/GDM/${server_type}.py
  #echo -e "\nStarting $server_type..."
  echo ""

  if [ -e $out_file ]; then
    mv $out_file ${ARCHIVE_DIR}/$(basename $out_file).$$
  fi

  (nohup python $server_path  2>&1; echo "$server_type PID $! exited with status $?" ) > $out_file &
  #This now captures STDOUT as sys.stdout is set to unbuffered
  IFS=''
  #To maintain leading white space in read

  tail -n 100 -f $out_file | while read line; do
    echo -e $line
    [[ "$line" == "Running $server_type ThreadedXMLRPCServer"* ]] && pkill -P $$ 'tail'
  done

  #Check server is actually running in case it fell over before server forever
  local running_pid=$(getServerPID $server_type)

  if [ -z "$running_pid" ]; then
    echo -e "ABORTING:\tFailed to get running $server_type PID from CGSServers.pid.txt"
    exit 1
  elif [[ -z $(isPIDrunning $running_pid) ]]; then
    echo -e "ABORTING:\t$server_type PID $running_pid is not running"
    exit
  fi
}

isPIDrunning(){
  echo $(ps $1 | grep -vE '\s+PID')
}

getServerPID(){
  local server_type=$1
  local pid_file=${APP_INS_DIR}/EpiExplorer/Config/CGSServers.pid.txt
  local running_pid=$(grep $server_type $pid_file | cut -f 2)
  echo $running_pid
}

#Don't really need this in a script, only in functions
OPTIND=1

CGSQ=
CGSS=
CGSD=
ONLY_SERVER=
ACTION=
STOP=
SCRIPT_DIR=$( cd "$( dirname "$0" )" && pwd )
#Resolves all links. Although this will not work if being sourced?
#This also does not handle -bash being returned from $0, but tha tonly affects testing
#on the command line. $0 should normally give a real path

APP_INS_DIR=${APP_INS_DIR:-"${SCRIPT_DIR}/../../.."}
#Default APP_INS_DIR for OUTPUT_DIR inherited from the init_epi_env.sh
# environment or -O should specified as an option
OUTPUT_DIR="${APP_INS_DIR}/output/"
CONFIG_DIR="${SCRIPT_DIR}/../../Config"

usage="Usage:\tstartCGSServers.sh <OPTIONS>  ACTION (e.g. start, stop or restart)

  OPTIONS:
    -d (Control CGSDatasetServer)
    -q (Control CGSQueryServer)
    -s (Control CGSServer)
    -o (Start only the specified server, default controls all dependant servers)
    -O (Output directory for logs etc. default = $OUTPUT_DIR)
    -Q (Quiet down now. Does not tee server output)"

while getopts ":O:dqsoQh" opt; do
  case $opt in
    O  ) OUTPUT_DIR=$OPTARG;;
    d  ) CGSD=1;;
    q  ) CGSQ=1;;
    s  ) CGSS=1;;
    o  ) ONLY_SERVER=1;;
    Q  ) QUIET=1;;
    h  ) echo -e $usage; exit 0;;
    \? ) echo -e "Unrecognized option\n$usage"; exit 1;;
    -  ) shift; break;; #Standard argument separator
  esac
done

#Shift the options and their arguments to deal with remaining arguments
shift $((OPTIND-1))

#Skip standard argument separator
[ "$1" = "--" ] && shift

if [ ! $1 ]; then
  echo "Please specifiy a valid ACTION argument e.g. start, stop or restart"
  exit 1
fi

ACTION=$(echo $1 | tr A-Z a-z)

if [[ ! $ACTION =~ ^(start|restart|stop)$ ]]; then
  echo "ACTION argument $ACTION is not valid. Please specify start, stop or restart"
  exit 1
fi

if ! [[ "$CGSS" || "$CGSQ" || "$CGSD" ]]; then
  echo "Please specify at least one server to restart e.g. -d -q or s"
  exit 1
fi

if [[ ! -d $OUTPUT_DIR ]]; then
  echo -e "-O is not a directory:\t$OUTPUT_DIR"
  exit
fi

ARCHIVE_DIR="${OUTPUT_DIR}/log_archive"

[ ! -d $ARCHIVE_DIR ] && mkdir $ARCHIVE_DIR


if [ $CGSD ]; then
  stopServer CGSDatasetServer
  [ ! $ONLY_SERVER ] && CGSQ=1;
fi

if [ $CGSQ ]; then
  stopServer CGSQueryServer
  [ ! $ONLY_SERVER ] && CGSS=1;
fi

[ $CGSS ] && stopServer CGSServer

#Archive log for full stack restart
if [[ $CGSD && $CGSQ && $CGSS ]]; then
  full_log=${OUTPUT_DIR}/CGS_full.log

  if [ -e $full_log ]; then
    mv $full_log ${ARCHIVE_DIR}/$(basename $full_log).$$
  fi
fi

[ $CGSD ] && [[ $ACTION =~ .*start ]] && startServer CGSDatasetServer
[ $CGSQ ] && [[ $ACTION =~ .*start ]] && startServer CGSQueryServer
[ $CGSS ] && [[ $ACTION =~ .*start ]] && startServer CGSServer

exit

