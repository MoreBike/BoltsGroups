#!/bin/bash
START_DIR="./"
PYTHON_VENV=".venv"
DATE=$(date --date="tomorrow" +"%Y%m%d")
MAIL_SCRIPT="./mail_bolts.py"

# Usage info
show_help() {
cat << EOF
Usage: ${0##*/} [-h] [-t] [-s] [-x] [-d DATE]
Build rider groups for Bolts practices for a specifc day.  When no option is given it gets tomorrow's date.

    -h           display this help and exit
    -t           use test emails only
    -x           skip email
    -s           skip the teamapp download (only do this if you have a working .csv file)
    -d DATE      DATE should be in form YYYYMMDD
EOF
}

TEST_EMAILS=false
SKIP_EMAILS=false
DO_TEAMAPP=true
MAX_ITERATIONS=6
OPTIND=1 # Reset is necessary if getopts was used previously in the script.  It is a good idea to make this local in a function.
while getopts "htxsd:" opt; do
    case "$opt" in
        h)
            show_help
            exit 0
            ;;
        t)
            TEST_EMAILS=true
            ;;
        x)
            SKIP_EMAILS=true
            ;;
        s)
	    DO_TEAMAPP=false
            ;;
        d)  DATE=$OPTARG
            ;;
        '?')
            show_help >&2
            exit 1
            ;;
    esac
done
shift "$((OPTIND-1))" # Shift off the options and optional --.

# Gin up my mailing command
myMail() {
    if [ "$SKIP_EMAILS" = true ] ; then
        echo "Skipping email" 
    elif [ "$TEST_EMAILS" = true ] ; then
	# echo "test"
	${MAIL_SCRIPT} --to 'FILL_IN_TEST_EMAIL' --subject "Bolts Groups for ${DATE}"
    else
	# echo "real"
	${MAIL_SCRIPT} --to 'FILL_IN_COACH_EMAILS_SEPARATE_WITH_COMMAS' --subject "Bolts Groups for ${DATE}"    
    fi
}

# Move into our directory and load up the python venv
cd $START_DIR
source ${START_DIR}/${PYTHON_VENV}/bin/activate
LOGFILE=${DATE}/logfile.${DATE}
mkdir -p ${DATE}
rm $LOGFILE

if [ "$DO_TEAMAPP" = true ] ; then
    echo "Getting riders from TeamApp" >> $LOGFILE
    ./getRidersFromTeamApp.py --date ${DATE} >> $LOGFILE 2>&1
fi

if [ $? -eq 0 ]
then
    ./putInBoltsGroups.py --date ${DATE} ${DATE}/event_replies.json > ${DATE}/boltsGroups_${DATE}.txt 2>> $LOGFILE 
    cat ${DATE}/boltsGroups_${DATE}.txt | myMail
else
    echo "No Groups for ${DATE}" | myMail
fi

if [ "$SKIP_EMAILS" = false ] ; then
    cat  $LOGFILE | ./mail_bolts.py --to 'FILL_IN_COACH' --subject "Bolts Groups for ${DATE} - logfile"
fi

