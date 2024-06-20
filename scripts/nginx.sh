
#!/usr/bin/bash

sudo systemctl daemon-reload
sudo rm -f /etc/nginx/sites-enabled/default

sudo cp /home/ubuntu/Biblioteck/nginx/nginx.conf /etc/nginx/sites-available/Bibliotech
sudo ln -s /etc/nginx/sites-available/Bibliotech /etc/nginx/sites-enabled/
#sudo ln -s /etc/nginx/sites-available/Bibliotech /etc/nginx/sites-enabled
#sudo nginx -t
sudo gpasswd -a www-data ubuntu
sudo systemctl restart nginx

sudo certbot --nginx -d 3.26.191.43
sudo systemctl restart nginx