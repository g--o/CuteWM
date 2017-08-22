#!/bin/bash

gnome-settings-deamon &
nautilus -n &
dbus-launch docky &
exit
