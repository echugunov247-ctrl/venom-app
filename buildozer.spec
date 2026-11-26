[app]
title = Venom
package.name = venomapp
package.domain = org.venom
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Оставляем только одну архитектуру
android.archs = arm64-v8a

# Совместимые версии
android.api = 30
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True

# Убрали requests, чтобы не было ошибки сборки
requirements = python3,kivy==2.3.0,urllib3,certifi,cython==0.29.36
android.permissions = INTERNET, ACCESS_NETWORK_STATE

icon.filename = %(source.dir)s/venom.png
orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1
