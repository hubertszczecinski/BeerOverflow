## how to make certbot get real certs

```shell
docker compose up -d # start everything+frontend nginx so it can resolve the challenge
docker compose run --rm --entrypoint "certbot" certbot certonly --webroot --webroot-path=/var/www/certbot -d example.com
docker compose restart frontend # make nginx use the new certs
```
i essa