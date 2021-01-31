Date: January 30, 2021
Tags: linux
Summary: Fix wifi connection drops on Dell XPS 13 (9300) with Linux.

# Wifi Connection Drops on Dell XPS 13 (9300) with Linux

I purchased a Dell XPS 9300 Developer Edition laptop in August 2020. It shipped with Ubuntu 20.04, but I replaced it with Arch Linux. This was a return to Linux for me since switching all my machines to MacOS in 2005.

Overall the quality of the machine has been superb. I got the 4k screen and HiDPI support in GNOME has been great. The bezel-less design also makes it feel like a laptop from the future.

The only issue I've had so far has been the occasional wifi connection drops. The XPS 9300 -- and it's successor the 9310 -- both ship with the [Killer Wifi AX1650](https://www.killernetworking.com/products/killer-ax1650/) card. With a Linux 5.4+ kernel, the card works out of the box utilizing `iwlwifi`. While on battery power, though, I would experience a connection drop every few hours. The only thing that would fix it would be to either 1) plug in a power cable or 2) toggle the connect in NetworkManager. Neither have been ideal and I have always suspected some sort of power save setting. I think the combination of having older Airport Extreme routers that don't support power saving and athe Killer Wifi card was the source of the problems.

# The Fix

I tried various fixes from forums around the web, but nothing seemed to help. There were also a lot of other recommendations for disabling hardware encryption and some antenna aggregation tweaks that I was hoping to avoid if possible. Based on user reports, these settings could help connection stability, but at the cost of wifi performance.

Thanks to the [Arch Linux Wiki](https://wiki.archlinux.org/index.php/Power_management#Intel_wireless_cards_(iwlwifi)), I noticed a setting I had not yet tried. Here is what my `/etc/modprobe.d/iwlwifi.conf` file looks like:

```
options iwlwifi power_save=0 d0i3_disable=0 uapsd_disable=0
options iwlmvm power_scheme=3
```

If this file doesn't exist, go ahead and create it. The missing line for me was line 2. There are two variants for `iwlwifi` cards, and you can find out which variant with this command:

```
lsmod | grep '^iwl.vm'
```

This will return either `iwlmvm` or `iwldvm`. For me it was the former. If yours is the latter, replace line 2 with:

```
options iwldvm force_cam=0
```

And that's it! You'll want to reboot your system after you make these changes, but hopefully that fixes your connection drops without sacrificing your wifi performance.
