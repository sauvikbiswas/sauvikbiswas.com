---
title: "How useful can an app made in 3 days be?"
date: 2017-02-08
categories: 
  - "coding"
tags: 
  - "flask"
  - "ninjin"
  - "python"
---

## Some background

A few weeks ago, [I was fooling around with Flask framework](/posts/experimenting-with-flask-micro-framework/). I loved it. As a consequence, I had this strange itch of creating something useful using the framework. My goal was not to write a production ready, industrial level software, but something that would give me some experience in dabbling with a modern toolkit for writing webapps. I had also [mentioned in an earlier blog](/posts/experimenting-with-flask-micro-framework/) that the last time I had tried building any form of webapp was nine years ago, for Dark Project's website and in PHP. (Can't believe how archaic that language even sounds!)

Mogit was also interested in exploring the framework. Together, we decided to write a simple discussion board with an inherent to-do functionality. The core idea being that any discussion thread can become a to-do entry and any to-do entry can become a discussion thread. I can see a lot of real world application for such a webapp.

## A long weekend is a good time to fool around

I crashed at Mogit's place on 26th of January. I had plans to cycle towards the south of Bangalore during the long weekend. ([I eventually went to Hosur](/posts/a-day-off-and-a-ride-to-tvs-plant/).) Needless to say, my non-cycling time involved writing some piece of code for an hour and then taking a half an hour break to have some tea. (And sleeping long hours at night.) I lost count of the number of cups of tea I had.

I should mention that we weren't trying to build anything that even remotely resembled a product or a solution. A simple invite-only registration system, a no-frills login (with indefinite persistence of login related cookies), a simple discussion segment list (or analogous to folders in the traditional forum), a discussion thread page inside each of those segments, and a thread page that formats and displays markdown text.

We ended up inserting a few forms, too. Stuff that could help us add a segment, a thread or a to-do.

{{< figure src="Screenshot-2017-02-08-22.38.41-768x437.png" caption="This is how one of the segment page with all the discussion threads looked like." >}}

{{< figure src="Screenshot-2017-02-08-22.53.25-768x419.png" caption="And this is how a single discussion thread looked like. We even put up things that were causing errors." >}}

I think I spend just short of 36 hours in building this prototype. It was more like a self-created hackathon. If I work for another 30-40 hours, I can have a production ready, small-scale implementation of the webapp.

The name is just a placeholder. I just picked it up from [one of the One Piece characters](http://onepiece.wikia.com/wiki/Ninjin). By the way, it means **carrot** in Japanese.
