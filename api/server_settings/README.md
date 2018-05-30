# Server setting

## Apache2 Proxy
`/etc/apache2/sites-available/api.mandaty.cz.conf`

```bash
sudo a2enmod proxy_http
sudo a2ensite api.mandaty.cz
sudo service apache2 reload
```

## Let's encrypt
`sudo certbot --apache`

## Systemd
`/etc/systemd/system/datasette.service`

```bash
sudo systemctl daemon-reload
sudo systemctl enable datasette.service
sudo systemctl start datasette.service
```
## Sources:
Datasette:
- https://github.com/simonw/datasette

Systemd:
- https://www.digitalocean.com/community/questions/convert-run-at-startup-script-from-upstart-to-systemd-for-ubuntu-16
- https://serverfault.com/questions/785502/create-daemon-on-ubuntu-16-04
- https://github.com/lawlesst/baseballdb-datasette/blob/master/baseballdb.service
- further reading: https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units

Apache2:
- https://stackoverflow.com/questions/23931987/apache-proxy-no-protocol-handler-was-valid#26045183
- https://github.com/lawlesst/baseballdb-datasette
