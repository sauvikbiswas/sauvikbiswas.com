---
title: "Good guys always backup their data"
date: 2016-09-12
tags: 
  - "backup"
  - "digital-ocean"
  - "hfs"
  - "mac"
  - "ssd"
coverImage: "PICT_20160912_223637.jpg"
---

One of the caveats of running a website on a self-configured system is that the webmaster is in charge of all fail-safe, precautionary measures - not only for the data, but also for the server configuration - in case something strange happens. This is in stark contrast to the shared virtual hosting ethos where the webmaster is only required to take such precautionary measure for only the data and nothing else.

This is my strategy of backing up my server.

## Ditching the automatic backups

Digital Ocean offers a service for automatic backups. It carries a fixed cost of 20% of the VM charge. On the other hand, a manual snapshot of the installation costs 0.05 USD per GB per month. Since my VM cost is 5 USD per month, the former will make sense if my storage is close to 20 GB. Also, since there is no critical cost to failure, I am ready to sacrifice a tiny bit of redundancy for the sake of price.

As of now, the snapshot hasn't even touched 10 GB.

[![screenshot-2016-09-12-21-57-22](Screenshot-2016-09-12-21.57.22.png)](http://sauvikbiswas.com/wp-content/uploads/2016/09/Screenshot-2016-09-12-21.57.22.png)

I always ensure that there is at least one snapshot that I can use to re-instantiate the webserver and the data. This snapshot will allow me to resurrect the entire configuration. As of today, I have two websites running on this VM (or Droplets as Digital Ocean likes to call it).

## Never forget the local backup

This is a practice I had developed when I was administering my band's website. Unlike the quick, modern day CMS like Wordpress, all the eight incarnations of the website were hand crafted. I used to archive the content periodically. This was one of the reasons why I could spin out a new website when our first host [Go Daddy started to act funny](http://54uv1k.blogspot.in/2011/07/issues-with-go-daddy.html) (aka daddy issues).

Nowadays, there are only two things to take care of - dump the database schema and create a copy of the /var/www/html (or wherever you have configured your webserver root) file structure. It does take some time but that idle time is good enough for me to bury myself in a comic book.

{{< figure src="PICT_20160912_213844.jpg" caption="That's Filezilla dumping the entire website data onto my new HDD. I don't prefer installing an FTP server. SFTP over a standard SSH pipe is a much safer approach." >}}

This doesn't necessarily create a redundancy in the state of the webserver but is an important part of the job. In case I have to migrate the data to a different platform, this will come handy.

## Cleaned up my Mac, too

I had the earlier backup of my website on the internal SSD of my Mac. With only 128 GB of space, it was already struggling to keep all the photographs and the Python virtualenv's for each of the coding projects. (In case if you didn't know, virtualenv creates local site-packages for each project.)

After spending a few hours migrating the Photo and Video libraries to the external HDD and then setting up a manual backup on Time Machine, the storage bar chart of my Mac looks pretty neat.

{{< figure src="Screenshot-2016-09-12-22.18.38.png" caption="I do not know why I have 13 GB of audio files. I have a hunch that they might be Garageband instrument samples." >}}

There is a caveat to configuring an HDD for Time Machine. Mac formats it to journaled HFS+. Windows cannot natively read it although [some third party solutions exist](http://www.howtogeek.com/252111/how-to-read-a-mac-formatted-drive-on-a-windows-pc/). Linux [can read it but cannot write if it is journaled](http://askubuntu.com/questions/16811/how-well-is-the-hfs-filesystem-supported).
