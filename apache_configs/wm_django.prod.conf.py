###############################
# wm_django production
###############################

ServerRoot "/home/.../webapps/wm_django_production/apache2"

LoadModule authz_core_module modules/mod_authz_core.so
LoadModule dir_module        modules/mod_dir.so
LoadModule env_module        modules/mod_env.so
LoadModule log_config_module modules/mod_log_config.so
LoadModule mime_module       modules/mod_mime.so
LoadModule rewrite_module    modules/mod_rewrite.so
LoadModule setenvif_module   modules/mod_setenvif.so
LoadModule wsgi_module       modules/mod_wsgi.so
LoadModule unixd_module      modules/mod_unixd.so
LoadModule alias_module      modules/mod_alias.so
LoadModule headers_module    modules/mod_headers.so
LoadModule deflate_module    modules/mod_deflate.so

LogFormat "%{X-Forwarded-For}i %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
CustomLog /home/.../logs/user/access_wm_django_production.log combined
ErrorLog /home/.../logs/user/error_wm_django_production.log

Listen 21035
KeepAlive Off
SetEnvIf X-Forwarded-SSL on HTTPS=1
ServerLimit 1
StartServers 1
MaxRequestWorkers 3
MinSpareThreads 1
MaxSpareThreads 2
ThreadsPerChild 3

WSGIDaemonProcess wm_django_production processes=3 threads=3 python-path=/home/.../webapps/wm_django_production/venv/lib/python2.7/site-packages:/home/.../webapps/wm_django_production:/home/.../webapps/wm_django$
WSGIProcessGroup wm_django_production
WSGIRestrictEmbedded On
WSGILazyInitialization On
WSGIScriptAlias / /home/.../webapps/wm_django_production/wm_django_django/wm_django/wsgi/prod.py
WSGIPassAuthorization On

Alias   /s	/home/.../webapps/wm_django_production/wm_django_django/static_root
Alias   /m	/home/.../webapps/wm_django_production/wm_django_django/media_root

<FilesMatch "\.(ico|jpg|jpeg|png|gif|js|css|svg|woff|woff2|eot|ttf)$">
    Header set Cache-Control "max-age=290304000, public"
</FilesMatch>

<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
</IfModule>