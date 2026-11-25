[app]
title = Venom App
package.name = venomapp
package.domain = org.venom
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3==3.11.5,kivy==2.3.0,requests,urllib3,certifi,chardet,idna
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.ndk = 25b

icon.filename = %(source.dir)s/venom.png
orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1
