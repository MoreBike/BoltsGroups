#!/bin/bash

TA_AUTH_TOKEN="FILL_IN_AS_EXPLAINED_IN_README"
TEAMNAME_AND_EVENT_URL="FILL_IN_WITH_TEAM_INFO"
EVENT_ID=""
FILE_OUT=""
OPTIND=1 # Reset is necessary if getopts was used previously in the script.  It is a good idea to make this local in a function.
while getopts "f:e:" opt; do
    case "$opt" in
        f)
	    FILE_OUT=$OPTARG
            ;;
        e)  EVENT_ID=$OPTARG
            ;;
    esac
done
shift "$((OPTIND-1))" # Shift off the options and optional --.
if [ "$FILE_OUT" = "" ] ; then
    echo "Need -f FILE"
    exit 0
elif [ "$EVENT_ID" = "" ] ; then
    echo "Need -f FILE" 
    exit 0
fi

curl "https://${TEAMNAME_AND_EVENT_URL}/events/${EVENT_ID}/replies.json?_csv_data=v2&show=yes" \
     -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
     -H 'accept-language: en-US,en;q=0.9' \
     -H 'cache-control: max-age=0' \
     -H "cookie: _ga=GA1.1.1104659133.1694488348; _ga_7WE6PX8M8E=GS1.1.1694659369.2.0.1694659369.60.0.0; _ga_2MNN4QHYYL=GS1.1.1694659369.2.0.1694659369.0.0.0; __stripe_mid=241869f4-3e16-43c8-91f9-eba5d9b02e570c7bff; cookieconsent_status=dismiss; ta_auth_token=${TA_AUTH_TOKEN} __stripe_sid=c40a3bbd-2ae7-4d79-a8a0-0cca1351098c288914;" \
     -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36' \
     -o ${FILE_OUT}
