# Server setting

## Apache2 Proxy
`/etc/apache2/sites-available/api.mandaty.cz.conf`

```
$ sudo a2enmod proxy_http
$ sudo a2ensite api.mandaty.cz
$ sudo service apache2 reload
```

## Let's encrypt
`sudo certbot --apache`

## Systemd
`/etc/systemd/system/datasette.service`

```
$ sudo systemctl daemon-reload
$ sudo systemctl enable datasette.service
$ sudo systemctl start datasette.service
```
