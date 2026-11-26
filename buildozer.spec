[app]
title = Venom
package.name = venomapp
package.domain = org.venom
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Оставляем только одну архитектуру для стабильности и экономии памяти
android.archs = arm64-v8a

# Указываем совместимые версии
android.api = 30
android.minapi = 24
android.ndk = 25b

# Автоматическое принятие лицензий (чтобы не было ошибки Aidl not found)
android.accept_sdk_license = True

# Зависимости (cython зафиксирован для стабильности)
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,chardet,idna,cython==0.29.36
android.permissions = INTERNET, ACCESS_NETWORK_STATE

icon.filename = %(source.dir)s/venom.png
orientation = portrait

[buildozer]
# Уровень 2 нужен, чтобы увидеть ошибку, если она будет
log_level = 2
warn_on_root = 1
