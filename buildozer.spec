[app]
title = Whisp Shell
package.name = whispshell
package.domain = org.whisp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,requests,urllib3,charset-normalizer,idna,certifi,openssl

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,VIBRATE,WAKE_LOCK,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE,CAMERA,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS,ACCESS_COARSE_LOCATION,ACCESS_FINE_LOCATION,READ_CONTACTS

android.api = 33
android.minapi = 21
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
