---
title: "Kick and Snare processing using side-chained noise gates"
date: 2015-06-11
categories: 
  - "music"
tags: 
  - "kick-drum"
  - "reaper"
  - "snare"
---

I was working on mixing our (I don't know what this new project will be named) new song. This time around, I wanted a very open palette - very much like a well ventilated soundfield where instrument separation was of prime importance. This meant that I couldn't use much of my go-to reverb designs. That would hamper the purity of tomes and lead to clutter. One of the problems I faced was to get a thick Kick sound without the boom and a sharp snare without making it nasal.

## The process in four steps

I came across a nifty trick to trigger a pure tone along with the kick and give it a very controlled ring.

{{< figure src="reaper-sidechain.jpg" caption="Click on the image to see a large version in a new window.The numbers correspond to the steps described below." >}}

Here is a four step process to do it.

1. Create an empty track (named here as Kick\_thick) and set the number of channels to 4.
2. Create a send from your original Kick track to Kick\_thick. Make sure that the send of channel 1+2 is fed into channel 3+4 of Kick\_thick.
3. Using any tone generator, generate a pure tone. Here I wanted a D and so I have set it to 146.83 Hz. Set it to whatever note you want. [Here is a chart](http://www.phy.mtu.edu/~suits/notefreqs.html). You will get a constant "annoying" sine wave.
4. This sound should only be audible when the Kick hits. for that I have used Reaper's default gate, ReaGate. Using the Auxiliary L+R (3+4 channel - as in step 2) as trigger, the threshold is set. Now you can play around with the attack, hold and release.

I did a similar trick with the snare. Only this time, instead of a tone generator, I have used pink noise. The output of this channel was fed into a nice, short ping-pong delay. An extreme case of this would actually lead me back to the 80's hair metal snare sound. Metaphorically, I stopped right at the mid-90s.

Here are the before and after samples (some loss has occurred due to compression - but you can still make out with decent listening equipment):

**Before:**

\[audio ogg="http://sauvikbiswas.com/wp-content/uploads/2015/06/baseline.ogg"\]\[/audio\]

**After:**

\[audio ogg="http://sauvikbiswas.com/wp-content/uploads/2015/06/modified.ogg"\]\[/audio\]

**In context of the mix:**

\[audio ogg="http://sauvikbiswas.com/wp-content/uploads/2015/06/mix-sample.ogg"\]\[/audio\]

It might appear to have been lost, but reality is far from that. At higher volumes, the thickness of kick doesn't produce boom and the snare doesn't expose nasal tone even though they are meatier and sharper respectively.

## Bonus: How the engineers achieved the 80s snare sound

Why not hear it from Dave Pensado himself?

\[embed\]https://www.youtube.com/watch?v=yYZrjOJoisE\[/embed\]
