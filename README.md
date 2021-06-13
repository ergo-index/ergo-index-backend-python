<details open>
<summary>Running the Project</summary>

```bash
# To update and restart the API:
cd ~; rm -rf ergo-index-fund-backend; git clone https://<github_user>:<access_token>@github.com/ergo-index/ergo-index-fund-backend ergo-index-fund-backend; cd ~/ergo-index-fund-backend; cp ~/ergo_index_fund_backend_data/project_settings.env .env; docker-compose -f docker-compose.yml down && docker-compose -f docker-compose.yml up -d --build

# To view logs for debugging:
docker logs ergo_index_fund_backend_container
```
</details>

<details>
<summary>Setting Up the Project</summary>

First, set up an Ubuntu machine with Docker and a user named ```ergo-index-fund-user```:
```bash
# Create 'ergo-index-fund-user' user.
sudo adduser ergo-index-fund-user
sudo adduser ergo-index-fund-user sudo
exit

# USING NEWLY-CREATED USER, uninstall old docker versions.
sudo apt-get remove docker docker-engine docker.io containerd runc docker-compose

# Add the docker repo.
sudo apt update
sudo apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  
# Install docker engine.
sudo apt install docker-ce docker-ce-cli containerd.io

# Install docker-compose.
sudo curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Give the user docker permissions.
sudo groupadd docker
sudo usermod -aG docker ergo-index-fund-user

# Logout and reconnect the ssh session.
```

Next, you will need to create the persistent data directory and upload the settings file:
```bash
# Create the data directory and settings file.
cd ~
mkdir ergo_index_fund_backend_data
sudo touch ergo_index_fund_backend_data
sudo apt install nano

# Copy project settings onto the machine.
sudo nano ergo_index_fund_backend_data/project_settings.env
# ...<copy & paste text from project_settings.env file located in the project root dir>.
# ...use this file to set your passwords.
```
    
 To obtain SSL certificates, run the following commands (will only work if the domain points to the machine's ip):
 ```bash
# Install certbot.
sudo apt install snapd
sudo snap install core && sudo snap refresh core
sudo apt remove certbot
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Create the certificates (this opens a temporary webserver on port 80).
sudo rm -R /etc/letsencrypt/live/ergo-index.fund
sudo certbot -v certonly --standalone
# ...when prompted, enter domain name 'ergo-index.fund'.

# NOTE: If the domain changes from 'ergo-index.fund', the docker volume path for 'ergo_index_fund_nginx_container'
#       will need to be updated accordingly, in docker-compose.yml.

# ALSO NOTE: We might need a post-hook to restart the nginx container when the certificate renews.
```

To secure the redis database with a firewall, execute the following commands:
```bash
sudo iptables -I DOCKER-USER -p tcp ! -s <machine_ip> --dport 6479 -j REJECT
sudo apt install iptables-persistent
sudo apt install netfilter-persistent
sudo netfilter-persistent save
sudo netfilter-persistent start
```
 
Finally, you will need to create an access token for a GitHub user with read access to the repo.
Use these credentials to initialize the API admin user (this only needs to be done once):
```bash

# Update and restart the API.
cd ~; rm -rf ergo-index-fund-backend; git clone https://<github_user>:<access_token>@github.com/ergo-index/ergo-index-fund-backend ergo-index-fund-backend; cd ~/ergo-index-fund-backend; cp ~/ergo_index_fund_backend_data/project_settings.env .env; docker-compose -f docker-compose.yml down && docker-compose -f docker-compose.yml up -d --build
  
# Enter into the docker container for Django.
docker exec -it ergo_index_fund_backend_container /bin/bash
  
# Create admin user in the SQL database.
python manage.py migrate auth; python manage.py createadminuser; python manage.py makemigrations
exit
```
</details>
