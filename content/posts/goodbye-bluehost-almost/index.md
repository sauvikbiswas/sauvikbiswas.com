---
title: "Goodbye Bluehost, almost"
date: 2016-08-31
categories: 
  - "coding"
tags: 
  - "bluehost"
  - "digital-ocean"
  - "godaddy"
  - "vps"
  - "website"
coverImage: "Screenshot-2016-08-31-19.37.15.png"
---

Incase you are wondering how to sing that line, [you can use this song as a reference](https://www.youtube.com/watch?v=MJUuDoRZpyU).

## Me and Bluehost: A history lesson

About three years ago, I wanted to migrate my anime blog (Line of Flow, later merged with my personal blog) from the shared Wordpress.com servers. I wanted to do so because I wanted more control over the customisations. Previously, I had maintained the website of my (now defunct) band Dark Project. I had used free servers like cjb.net before moving on to paid services from GoDaddy.

{{< figure src="Back.jpg" caption="This is the back cover of our oldest release. On the left side, the earliest URL of our webspace is still visible: darkproject.cjb.net" >}}

My experience with GoDaddy was one of the worst. That piece of history has been aptly logged in my erstwhile blogspace on Blogger. You can read about it here: [http://54uv1k.blogspot.in/2011/07/issues-with-go-daddy.html](http://54uv1k.blogspot.in/2011/07/issues-with-go-daddy.html). Long story short, I moved the entire data to Hostgator.

So, when it came to spawning my own Wordpress.org based site, I did not think twice before opting for Bluehost, a sister company of Hostgator. Also, the reviews said that they gave one of the best services when it came to Wordpress hosting.

I was pretty happy with them for an year or so, until one fine day I realised that my website took too long to load. I wasn't bothered too much about that. My visitors aren't that many. Also, since I write mostly longform entries, I assumed that whoever they were, would have enough patience to wait a few extra seconds.

{{< figure src="Screenshot-2016-08-31-18.57.53.png" caption="Google Now card still lists Bluehost as one of the best. I don't know how that's even possible." >}}

Sometime during January / February this year, my website became inaccessible. If anyone has ever tried to contact Bluehost support via mail, you'd know how frustrating it is.

Here is one of the umpteen chats I had with their support staff back in January.

> `[Initial Question] Provider: Bluehost - My Domain is: "sauvikbiswas.com" The site is down. (5:23) [Tejus] Hello, thank you for contacting support, sorry for the wait time and thank you for your patience. Could I get the last 4 characters of the cPanel password to verify ownership of the account? _[edited]_ (5:25) [Sauvik] This is third time in a row. (5:25) [Sauvik] What is the problem with your servers? (5:25) [Tejus] Thank you for validating. (5:25) [Sauvik] It is incredibly frustrating.. It had just recovered from a 16 hr outage and now again!!!!!!!! (5:26) [Tejus] http://sauvikbiswas.com/ is loading fine, Sauvik (5:27) [Sauvik] Not on my side (5:28) [Sauvik] http://www.isitdownrightnow.com/sauvikbiswas.com.html even shows that it is down for everyonw (5:28) [Tejus] Do you get any error? (5:29) [Sauvik] Let me clear browser cache and retry. (5:29) [Tejus] ok (5:30) [Sauvik] https://www.uptrends.com/tools/uptime shows that the website is not accessible from many of their servers including New Delhi (5:31) [Tejus] https://www.whatsmydns.net/#NS/sauvikbiswas.com (5:31) [Tejus] Seems like there is an propagation issue (5:31) [Sauvik] Ok. How would it get resolved? (5:33) [Tejus] I have pinged our specialists, it will be resolved in couple of hours. (5:34) [Tejus] Sauvik, Was there anything else I could help with for now? **(5:34) [Sauvik] The other part I had serious concern was that I never get replies to the tickets I raise.** (5:35) [Sauvik] I have to wait for 30 mins to get an opportunity to a "chat" (5:35) [Tejus] I am sorry for the trouble you have been having, Sauvik (5:35) [Sauvik] Again when you say couple of hours, how long should I expect for that. (5:36) [Tejus] Around 7-8 hours (5:36) [Sauvik] See it's not about you saying sorry. Clearly, your ticketing system is a mess. (5:36) [Sauvik] It might be a joke as well. (5:37) [Tejus] Please check it after 8 hours, Sauvik (5:37) [Sauvik] Do I have to wait for another "chat session" after 7-8 hours? or is there a better way to contact support? (5:38) [Tejus] No. You can contact us via phone (5:39) [Sauvik] That will be costly. Or is there a toll (5:39) [Sauvik] free no. (5:39) [Tejus] US (toll-free): 888-401-4678 (5:40) [Sauvik] I am not in US. That doesn't help my case. Only if you guys replied via tickets / mails (5:41) [Sauvik] But as I said, your ticketing system is a joke. (5:41) [Sauvik] Anyway, I don't think you could help me much. Thanks for your time. **(5:41) [Tejus] You'll get reply. But there might be a delay, Sauvik**`

And for sure, I got a reply. There was a delay.

{{< figure src="Screenshot-2016-08-31-19.05.06.png" caption="That's one month between escalation and reply." >}}

It was at this point that I had decided to migrate away from Bluehost. I still had some 8 months of subscription left.

## Searching for a solution

I wasn't ready to fork out some hefty money for hosting my website. My requirements aren't that intense. I looked around and read blogs that smelt ad-infused-fishy and looked like 'Top 10 Wordpress hosting companies', 'Why ABC is the best Wordpress hosting service', etc.

I asked Nandy what could I do. He suggested that I move my data and hosting to a VPS. He had used [Linode](https://www.linode.com/) for his business for years. It was only due to the load that they migrated to AWS. Linode itself was quite costly. I wasn't ready to shell out 10 USD per month. Luckily for me, [Digital Ocean](https://www.digitalocean.com/) had a VPS configuration that was slightly underpowered than the least powerful Linode VPS for half its cost. It was fine for me. I did not need so much power in the first place.

{{< figure src="Screenshot-2016-08-31-19.37.14.png" caption="Left: Digital Ocean, Right: Linode. 512 MB RAM and 1TB transfer is overkill." >}}

I asked Nandy about the config and he replied that it is good enough to run four concurrent websites. Right now I have two - one being this and the other being [Vapour Sea](http://vapoursea.com), an electronica / rock project I have been trying to bootstrap with Sudipto after the demise of [Dark Project](http://darkproject.bandcamp.com).

## It's not over yet

I still have my domain name registered with Bluehost. This means that I will still have to bear with them till next February until my registration expires.

{{< figure src="IMG_20160819_130922.jpg" caption="Enough of this rant. Here is the surreal image of the day." >}}
