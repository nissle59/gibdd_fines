git pull
docker restart parser_gibdd_fines
curl -X POST -F 'chat_id=288772431' -F 'text=container GIBDD FINES restarted' https://api.telegram.org/bot7194357846:AAGfBntMhRcfEpoHPJ0JiVMdXN12FYQUQ4g/sendMessage