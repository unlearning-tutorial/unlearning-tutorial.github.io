---
part: Part 1
title: "Motivations for Unlearning"
description: "Part 1 of Unlearning Data at Scale: Motivations for unlearning."
dek: "TODO"
output: part-1-motivations-for-unlearning.html
---

## Introduction {#introduction}

Machine unlearning asks the following fundamental question: how does one remove training data from a machine learning model which has already been trained? 
Having such functionality would be extremely useful for a variety of applications. 
Unfortunately, the term "machine unlearning" is overloaded, and what it means can vary dramatically based on what specific application or use case one has in mind. 
We proceed to discuss some motivations, and then interpretations of what it means to perform machine unlearning.
As we will see, this may differ significantly depending on the particular motivation of interest. 

## Motivations

### Data Privacy {#privacy}

The most oft-stated motivation for machine unlearning is *data privacy*.
Machine learning models are frequently trained on datasets containing sensitive information that belongs to people. 
Consider, for example, a facial recognition model which is trained on pictures of peoples' faces. 
Or a predictive model used in healthcare, trained on patients' electronic health records (EHRs). 
Yet another example is large language models (LLMs), which are frequently trained on massive, uncurated online datasets, which may contain personal information of many individuals. 
In all these cases, privacy of the dataset and, in general, the downstream model, enters the picture. 

Privacy legislation in several jurisdictions controls what rights individuals have over their data, after it has been collected and used by an organization. 
Perhaps the most well-known privacy legislation is the European Union's General Data Protection Regulation (GDPR).[@ref-1]
Article 17 outlines the "Right to erasure ('right to be forgotten')":

> The data subject shall have the right to obtain from the controller the erasure of personal data concerning him or her without undue delay and the controller shall have the obligation to erase personal data without undue delay where one of the following grounds applies: ... 

The law goes on to enumerate several conditions under which data deletion is required, including when the data subject withdraws consent or if the data was unlawfully processed. 

The GDPR is the canonical example of privacy legislation mandating a right to be forgotten, but it is far from the only one. 
In the United States, 22 different states have signed privacy legislation into law, and another 17 have had privacy bills introduced.[@ref-2]
Every single one of these laws and bills protects a "right to delete."

If an indvidual requests for their data to be deleted, what obligations does the organization have? 
At the very least, the organization is obligated to delete that individual's data from any database they may have. 
But the more interesting question is how this affects any models that have been trained on that individual's data. 

One 2021 case involves a California-based company, Everalbum, Inc., which non-consensually trained models on their users' photos and videos.[@ref-3]
In a settlement with the Federal Trade Commission, they were ordered to delete *all face embeddings and facial recognition models derived from this data* (see also the related concept of *model disgorgement*). 

Separately, the United Kingdom's Information Commissioner's Office advises that models may implicitly or explicitly encode personal data which they were trained upon.[@ref-4]
They suggest that obligation to remove this data from the trained model may vary depending the circumstances, and recommend implementing a model deployment pipeline that enables rapid accommodation of removal requests. 
Indeed, r-training an entire model from scratch due to a removal request is a rather heavy-handed solution, and if individual datapoints could be excised (i.e., *unlearned*) much more quickly, that would be preferrable. 





### Copyright {#copyright}


### Safety {#safety}

Contain data poisoning in here too

### Model Utility


### Leave-one-out

One of the oldest instances of machine unlearning appears in a 2000 paper of Cauwenberghs and Poggio.[@ref-??]

## Gautam's Notes

Each of these has their own nuances (some of Aloni's comments, also link Cooper's survey). 

Will we talk about individual unlearning or concept unlearning? 

## Key Takeaways {#takeaways}


## References {#references}

1. {#ref-1} [*General Data Protection Regulation*](https://gdpr-info.eu/).
2. {#ref-2} [*US State Privacy Legislation Tracker 2026*](https://iapp.org/resources/article/us-state-privacy-legislation-tracker)
3. {#ref-3} [*California Company Settles FTC Allegations It Deceived Consumers about use of Facial Recognition in Photo Storage App*](https://www.ftc.gov/news-events/news/press-releases/2021/01/california-company-settles-ftc-allegations-it-deceived-consumers-about-use-facial-recognition-photo). 
4. {#ref-4} [*How do we ensure individual rights in our AI systems?*](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/how-do-we-ensure-individual-rights-in-our-ai-systems/).

