from requests import get

public_ip = get('https://api.ipify.org').text

with open("deployment/conf/ecommerce_happy_nginx.conf", "r") as nginx:
    data = nginx.read()
    data = data.replace("{public_ip}", public_ip)
    with open("deployment/conf/ecommerce_happy_nginx.conf", "w") as nginx_update:
        nginx_update.write(data)
