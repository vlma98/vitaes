git pull origin master
git submodule foreach git pull origin master
sudo `which docker-compose` down
sleep 10
sudo `which docker-compose` up --detach --build