---
title: "Getting Speech Recognition to work on Mac"
date: 2016-01-18
categories: 
  - "coding"
tags: 
  - "att"
  - "google"
  - "ibm"
  - "python"
  - "speech-recognition"
  - "speech-to-text"
  - "wit-ai"
---

One of my colleagues, Ravish Verma, handed me a link to speech recognition code. The parent GitHub repo is here: [https://github.com/Uberi/speech\_recognition.git](https://github.com/Uberi/speech_recognition.git). I thought that it had a speech processing algorithm of its own. That was not the case. It turned out that it is a wrapper for four online engines (Google, Wit.ai, IBM and AT&T) that process the audio and returns the deciphered text to the code.

## Getting the microphone to work

One of the coolest thing is that one can use the microphone to capture the audio stream and get it parsed. Although that is not strictly necessary as the code works with recorded wav files as well. It's not as fun as using a microphone.

**Installing PortAudio:** [This is the software](http://www.portaudio.com/) that takes care of the OS and creates a wrapper around the native audio APIs in order to expose a unified API. `$ brew install portaudio` In order to link PortAudio, some folders need to be given write permission. `/usr/local/include /usr/local/lib /usr/local/lib/pkgconfig` After this PortAudio can be linked `$ brew link portaudio`

**Installing PyAudio:** PyAudio is the Python bindings for PortAudio. PortAudio APIs are sadly in C. Hence, in order to use them, a Python wrapper is needed. PyAudio is like a wrapper to a wrapper. `$ sudo pip install pyaudio`

**Installing Flac:** This is necessary as the Google speech API v2 requires the content to be sent as flac data. Quoting [Amine Sehili](https://aminesehili.wordpress.com/2015/02/08/on-the-use-of-googles-speech-recognition-api-version-2/#UnderstandingGooglesSRv2),

> So to get a reply from Google, we have to send an audio file as an HTTP packet that requests this page: `http://www.google.com/speech-api/v2/recognize`
> 
> with the following GET key=value pairs: `**client=**chromium **lang=**language (where language is en_US for American English, fr_FR for French, de_DE for German, es_ES for Spanish etc.). **key=**a_developer_key`
> 
> and the following HTTP header: `**Content-Type:** audio/x-flac; rate=file_sampling_rate (where file_sampling_rate is the sampling rate of the file). 8000, 16000, 32000 and 44100 are all valid values but not the only possible ones).`

Please note the client and key values highlighted in red. I will get back to them.

On OS X, installing FLAC command line tools is a breeze with Homebrew. `$ brew install flac`

## Running a sample code

Thankfully, the folder contains a set of example files. I was able to quickly whiff up a derivative that would convert my random phrases to text until I said 'exit' or 'quit'. 

{{< iframe "//pastebin.com/embed_iframe/W1dLDAZD" "100%" >}}

This is a straight up derivative of the file microphone\_recognition.py included in the examples folder. It works.

## Speech to Text requires developer key

This is where free food party ends. Of the four services supported by the package, Google, IBM and Wit.ai allows some bit of free food. For [AT&T](http://developer.att.com/apis/speech), one must pay.

The package uses the reverse engineered Google's Speech to Text API, and identifies itself (falsely) as Chromium browser (marked in red). There are a few ways to obtain a dev key but it appears that Google has taken a note of it and [have raised a flag](http://www.chromium.org/developers/how-tos/api-keys). For the time being if you want to fiddle the default key should suffice. However, there may be quota associated with the key.

Previously, people had reverse engineered Google's Weather API. One fine day, Google decided to cease support of the API. You can read about the frustrations of developers [here](http://kevin-junghans.blogspot.in/2012/08/google-weather-api-is-dead.html) and [here](http://stackoverflow.com/questions/12139565/google-weather-api-returning-strange-new-error/12141675#12141675). The actual reason behind Google's actions was that [they had depreciated iGoogle](http://www.programmableweb.com/news/google-weather-api/2012/08/28). No matter what the reason, there is a fair chance that the free food from Google would eventually cease.

I may post an update once I have used [Wit.ai](https://wit.ai/docs/http/20141022).
