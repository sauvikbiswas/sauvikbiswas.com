---
title: "Server Migration for my websites"
date: 2019-05-27
categories: 
  - "coding"
tags: 
  - "digital-ocean"
  - "vps"
  - "website"
coverImage: "do-19.png"
---

I have been using DigitalOcean for the last three years. I am pretty happy with their service. Of late, I found that my website takes a tad too long to load.

## Reasons for migration

- My old server ran Ubuntu 14.04 LTS. It is no longer supported by Canonical
- The machine had only 0.5 GB of RAM (which might explain the slow response). DigitalOcean now provides 1 GB of RAM and an additional 5 GB of HDD space for the same price.
- I wanted to setup a cost-effective backup system. I was using snapshots to keep a hibernated copy of the machine.
- The server had a lot of test junk that occupied unnecessary space, which in turn got backed up and costed me money.

My backup system based on snapshots wasn't that good either.

- I created manual snapshots every now and then. At any given point of time, I had at least two snapshots to fall back on.
- Since snapshots are billed by their size, I was paying couple of dollars on the snapshots alone
- I would occasionally do a mysqldump of the databases to sql files.

## Current configuration and backup mechanism

- My current configuration is a 1 CPU-1 GB RAM-25 GB HDD virtual machine running Ubuntu 18.04.2 LTS. I am comfortable with LAMP on Ubuntu and saw no reason to change.
- There is a snapshot of an initial configuration with all the websites running. In case the machine misbehaves, I can always re-instantiate the machine
- I have bought a 10 GB block volume storage that is specifically dedicated to site backups.
- A daily cronjob dumps a gzipped archive of my site directories—including the codebase—and their corresponding mysqldumps.

{{< figure src="do-2016-19.png" caption="Smallest machine: 2016 vs 2019. This can host four low volume websites." >}}
