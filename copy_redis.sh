# copy redis data
mkdir -p /home/ubuntu/redis_data/prod
rm -rf /home/ubuntu/redis_data/prod/* || true
scp -o StrictHostKeyChecking=no -i /home/ubuntu/sss-recsys.pem ubuntu@103.195.237.216:~/redis_data/prod/* /home/ubuntu/redis_data/prod
