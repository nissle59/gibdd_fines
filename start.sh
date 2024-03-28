pip install -r /var/www/html/requirements.txt > /dev/null 2>&1
#rm `$(docker inspect --format="{{.LogPath}}" parser_gibdd_fines)`
#chmod +x ./run_workers.sh
#./run_workers.sh &
uvicorn server:app --host 0.0.0.0 --port 5006 --workers 3
tail -f /dev/null