#!/usr/bin/bash 

sed -i 's/\[]/\["54.144.250.113"]/' /home/ubuntu/Biblioteck/Bibliotech/settings.py

python manage.py migrate 
python manage.py makemigrations     
python manage.py collectstatic
sudo service gunicorn restart
sudo service nginx restart

sudo chmod 777 /home/ubuntu/Biblioteck/db.sqlite3
sudo chown -R www-data:www-data /home/ubuntu/Biblioteck
#sudo tail -f /var/log/nginx/error.log
#sudo systemctl reload nginx
#sudo tail -f /var/log/nginx/error.log
#sudo nginx -t
#sudo systemctl restart gunicorn
#sudo systemctl status gunicorn
#sudo systemctl status nginx
# Check the status
#systemctl status gunicorn
# Restart:
#systemctl restart gunicorn
#sudo systemctl status nginx
