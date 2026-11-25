[app]
title = Venom App
package.name = venomapp
package.domain = org.venom
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,requests,urllib3
android.permissions = INTERNET
icon.filename = %(source.dir)s/venom.png
orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1
