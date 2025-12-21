---
title: "Hums of Dithering: An Example"
date: 2014-04-07
categories: 
  - "music"
tags: 
  - "audio"
  - "mixing"
---

This was a real problem, as in "What the hell is going on?" kind of problem.

I was mixing a song for our forthcoming album. The source tracks were pristine, barring the usual noise from amp that we all have heard a zillion times in all classic records. Reaper, my DAW of choice, and Yamaha HS 50Ms, my monitors of choice did not give out any signals that would be distracting to ears. However, every time I rendered to 160kbps, 44.1kHz mp3, I got this unnatural high pitched hum.

\[audio mp3="http://sauvikbiswas.com/wp-content/uploads/2014/04/441k.mp3"\]\[/audio\]

I was surprised. I tried various hi-resolution formats, but they came with little remedy. I tried bouncing the track to the original sample rate of 48kHz and magically, the hum disappeared!

\[audio mp3="http://sauvikbiswas.com/wp-content/uploads/2014/04/48k.mp3"\]\[/audio\]

I have used dithering before. We all have. But never earlier had I come across an additive noise profile that creates such a distracting hum.

Note: Dithering is the action of adding white noise to a signal before downsampling. [This page](http://www.djtechtools.com/2012/09/26/a-djs-guide-to-audio-files-and-bitrates/) has a nice example (see the portrait below). Audio dithering is technically no different from image dithering.

{{< figure src="dithering-explained-1024x556.png" caption="Effect of additive noise for dithering in images. The noise helps retention of the profile better at lower bit depths." >}}

This doesn't matter much. For the master render, I would be using 48kHz sampling rate anyways. I can then use a better resampling + dither algorithm to get a pleasing master track.

[![Audio-bit-reduction-from-24-bit-to-8-bit-with-and-without-dithering-CC-BY-SA-3.0](Audio-bit-reduction-from-24-bit-to-8-bit-with-and-without-dithering-CC-BY-SA-3.0.png)](http://sauvikbiswas.com/wp-content/uploads/2014/04/Audio-bit-reduction-from-24-bit-to-8-bit-with-and-without-dithering-CC-BY-SA-3.0.png)
