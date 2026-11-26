[app]
title = Venom
package.name = venomapp
package.domain = org.venom
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3,kivy==2.3.0,requests,urllib3,certifi,chardet,idna,cython==0.29.36
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.ndk = 25b

# ВАЖНО: эта строка заставляет Buildozer автоматически принять лицензии SDK
android.accept_sdk_license = True

icon.filename = %(source.dir)s/venom.png
orientation = portrait

[buildozer]
log_level = 1
warn_on_root = 1
