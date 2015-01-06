#!/bin/env bash


# TODO Move all output including pids files to OUTPUT_DIR
# For now this is now located within the APP_INS_DIR, so this should be added to to the $PATH in init_epi_env.sh

# TODO Add instance support, to allow this script to control multiple instances based on separated settings/config

# TODO update server output tail to handle 'exited with status' error



stopServer(){
  local server_type=$1
  checkServerHost $server_type
  local file_pid=$(getServerPID $server_type)

  if [ $file_pid ]; then
    local running_pid=$(isPIDrunning $file_pid)

    if [[ ! -z $(isPIDrunning $file_pid)  ]]; then

      if [[ ! $ACTION =~ ^(stop|restart)$ ]]; then
        echo "$server_type is already running, please specify 'restart' argument"
        exit 1
      fi

      echo "Stopping running $server_type with PID $file_pid"
      Execute kill $file_pid
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
  checkServerHost $server_type
  local out_file=${OUTPUT_DIR}/${server_type}.out
  local server_path=${APP_INS_DIR}/EpiExplorer/GDM/${server_type}.py
  echo ""
  [ $QUIET ] && echo -e "Starting $server_type..."

  if [ -e $out_file ]; then
    Execute mv $out_file ${ARCHIVE_DIR}/$(basename $out_file).$$
  fi


  #Execute this?
  (nohup python $server_path  2>&1; echo "$server_type PID $! exited with status $?" ) > $out_file &
  #This now captures STDOUT as sys.stdout is set to unbuffered
  IFS=''
  #To maintain leading white space in read

  tail -n 100 -f $out_file | while read line; do
    [ ! $QUIET ] && echo -e $line

    [[ "$line" == "Running $server_type ThreadedXMLRPCServer"* ]] && pkill -P $$ 'tail'
    #Also catch existed with status error here too and exit
    #will this just exit the while subshell or the whole script
    [[ "$line" == " exited with status "* ]] && exit 1
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


checkServerHost(){
  local server_type=$1
  local hostvar=$(eval "echo \$${server_type}_hostvar")
  local server_host=$(python -c "import settings; print settings.$hostvar")

  if [[ ! $server_host == $hname ]]; then
   echo "Running from $hname but $server_type control should be done on $server_host"
   exit 1
  fi
}

Execute(){
  $*
  local rtn=$?

  if [ $rtn != 0 ]; then
    echo -e "Failed to:\t$*"
    exit $rtn
  fi
}






#Don't really need this in a script, only in functions
OPTIND=1

CGSQ=
CGSS=
CGSD=
CASCADE=
ACTION=
STOP=
QUIET=
SCRIPT_DIR=$( cd "$( dirname "$0" )" && pwd )
#Resolves all links. Although this will not work if being sourced?
#This also does not handle -bash being returned from $0, but tha tonly affects testing
#on the command line. $0 should normally give a real path

APP_INS_DIR=${APP_INS_DIR:-"${SCRIPT_DIR}/../.."}
#Default APP_INS_DIR for OUTPUT_DIR inherited from the init_epi_env.sh
# environment or -O should specified as an option

#Attempt to get some defaults from settings.py
#PYTHONPATH should probably be handled in init_epi_env.sh
#but let's not rely on that
export PYTHONPATH="${APP_INS_DIR}/EpiExplorer/GDM/:$PYTHONPATH"
OUTPUT_DIR=$(python -c 'import settings; print settings.workingFolder')
CONFIG_DIR=$(python -c 'import settings; print settings.configFolder')

CGSServer_hostvar=forwardServerHost
CGSQueryServer_hostvar=queryServerHost
CGSDatasetServer_hostvar=datasetServerHost
hname=$(hostname -s)

usage="Usage:\tstartCGSServers.sh <OPTIONS>  ACTION (e.g. start, stop or restart)

  OPTIONS:
    -d (Control CGSDatasetServer)
    -q (Control CGSQueryServer)
    -s (Control CGSServer)
    -c (Cascade mode also affects dependant servers)
    -o (Output directory for logs etc. default = $OUTPUT_DIR)
    -Q (Quiet down now. Does not show server start up output)"

while getopts ":o:dqscQh" opt; do
  case $opt in
    o  ) OUTPUT_DIR=$OPTARG;;
    d  ) CGSD=1;;
    q  ) CGSQ=1;;
    s  ) CGSS=1;;
    c  ) CASCADE=1;;
    Q  ) QUIET=1;;
    h  ) echo -e "$usage"; exit 0;;
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
  echo -e "-O or settings.workingFolder is not a directory:\t$OUTPUT_DIR"
  exit 1
fi

if [[ ! -d $CONFIG_DIR ]]; then
  echo -e "settings.configFolder is not a directory:\t$CONFIG_DIR"
  exit 1
fi


ARCHIVE_DIR="${OUTPUT_DIR}/log_archive"

[ ! -d $ARCHIVE_DIR ] && mkdir $ARCHIVE_DIR


if [ $CGSD ]; then
  stopServer CGSDatasetServer
  [ $CASCADE ] && CGSQ=1;
fi

if [ $CGSQ ]; then
  stopServer CGSQueryServer
  [ $CASCADE ] && CGSS=1;
fi

[ $CGSS ] && stopServer CGSServer

#Archive log for full stack restart
if [[ $CGSD && $CGSQ && $CGSS ]]; then
  full_log=${OUTPUT_DIR}/CGS_full.log

  if [ -e $full_log ]; then
    Execute mv $full_log ${ARCHIVE_DIR}/$(basename $full_log).$$
  fi
fi

[ $CGSD ] && [[ $ACTION =~ .*start ]] && startServer CGSDatasetServer
[ $CGSQ ] && [[ $ACTION =~ .*start ]] && startServer CGSQueryServer
[ $CGSS ] && [[ $ACTION =~ .*start ]] && startServer CGSServer

exit

