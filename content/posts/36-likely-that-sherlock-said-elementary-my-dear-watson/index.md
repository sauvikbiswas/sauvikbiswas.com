---
title: "36% likely that Sherlock said, \"Elementary, my dear Watson\"!"
date: 2016-02-13
categories: 
  - "coding"
tags: 
  - "ai"
  - "n-gram"
  - "sherlock-holmes"
---

[![keep-calm-it-s-elementary-my-dear-watson](keep-calm-it-s-elementary-my-dear-watson-257x300.png)](http://sauvikbiswas.com/wp-content/uploads/2016/02/keep-calm-it-s-elementary-my-dear-watson.png)

I had built a crude N-Gram parser and resorted to the Sherlock Holmes books on Project Gutenberg as my training data set (training corpus). I was toying around with various phrases and the likelihood of their appearance in the books. One such phrase was "Elementary, my dear Watson".

"Elementary, my dear Watson" is technically a six word sentence, where even the start and the end of the sentence is taken into account. To the program, the sentence looks like this - \['&lt;s&gt;', 'elementary,', 'my', 'dear', 'watson', '&lt;/s&gt;'\]. I was using the Stupid Backoff model to compute my probabilities (Yes that's what the creators, Brants, et al., calls it. Here is a link to the [original paper](http://www.aclweb.org/anthology/D07-1090.pdf).)

The program returned me a value of 0.36. I had used a 6-gram model. There was no Markov approximation involved in analysing this 6-word sentence, which would just assume that in an n-gram only the nearest n-1 would matter. (In case of a 4-gram model, the program would give the same output even if it was 'elegant', 'extreme', 'au revoir' or 'exactly' instead of the word 'elementary').

A quick search through the n-grams showed that the phrase, "elementary, my dear watson", was not registered (the program reduces all inputs to lowercase). The closest phrase was "exactly, my dear watson". In fact the probability of that was shown to be 100%. That is hardly surprising, as it was in the training corpus.

Here is the truth. Sherlock Holmes never said the phrase, "Elementary, my dear Watson." I had no idea regarding the source of this misattributed quote. Hence, I searched online and stumbled upon a reliable answer.

[It was P.G. Wodehouse who wrote that](http://www.todayifoundout.com/index.php/2013/08/sherlock-holmes-never-said-elementary-dear-watson/)!
