---
part: Part 1
title: "Motivations for Unlearning"
description: "Part 1 of Unlearning Data at Scale: Motivations for unlearning."
dek: "Discussion of motivations for machine unlearning, and how they lead to the definition of interest."
output: part-1-motivations-for-unlearning.html
---

## Introduction {#introduction}

Machine unlearning asks the following fundamental question: how does one remove training data from a machine learning model which has already been trained? 
Having such functionality would be extremely useful for a variety of applications. 
Unfortunately, the term "machine unlearning" is overloaded, and what it means can vary dramatically based on what specific application or use case one has in mind. 
We proceed to discuss some motivations, and then interpretations of what it means to perform machine unlearning.
As we will see, this may differ significantly depending on the particular motivation of interest. 

## Motivations {#motivations}

### Data Privacy {#privacy}

The most oft-stated motivation for machine unlearning is *data privacy*.
Indeed, this was the primary motivation stated in the 2015 work of Cao and Yang,[@CY15] which is generally credited with popularizing the study of machine unlearning. 

Machine learning models are frequently trained on datasets containing sensitive information that belongs to people. 
Consider, for example, a facial recognition model which is trained on pictures of people's faces. 
Or a predictive model used in healthcare, trained on patients' electronic health records (EHRs). 
Yet another example is large language models (LLMs), which are frequently trained on massive, uncurated online datasets, which may contain personal information of many individuals. 
In all these cases, privacy of the dataset and, in general, the downstream model, enters the picture. 

[as: Can we give any examples here?]

Privacy legislation in several jurisdictions controls what rights individuals have over their data, after it has been collected and used by an organization. 
Perhaps the most well-known privacy legislation is the European Union's General Data Protection Regulation (GDPR).[@gdpr]
Article 17 outlines the "Right to erasure ('right to be forgotten')":

> The data subject shall have the right to obtain from the controller the erasure of personal data concerning him or her without undue delay and the controller shall have the obligation to erase personal data without undue delay where one of the following grounds applies: ... 

The law goes on to enumerate several conditions under which data deletion is required, including when the data subject withdraws consent or if the data was unlawfully processed. 

The GDPR is the canonical example of privacy legislation mandating a right to be forgotten, but it is far from the only one. 
In the United States, 22 different states have signed privacy legislation into law, and another 17 have had privacy bills introduced.[@iapp]
Every single one of these laws and bills protects a "right to delete."

[as: Does it make sense to consider Aloni's paper here which argues what GDPR actually does? This one and others: https://arxiv.org/abs/1904.06009]

If an individual requests for their data to be deleted, what obligations does the organization have? 
At the very least, the organization is obligated to delete that individual's data from any database they may have. 
But the more interesting question is how this affects any models that have been trained on that individual's data. 

One 2021 case involves a California-based company, Everalbum, Inc., which non-consensually trained models on their users' photos and videos.[@ftc]
In a settlement with the Federal Trade Commission, they were ordered to delete *all face embeddings and facial recognition models derived from this data* (see also the related concept of *model disgorgement*). 

[as: Does it make sense to discuss what happened to this company afterwards? Did it go bankrupt? Got a lot of bad PR, etc? In particular, why can someone not ignore the laws and just pay the penalty here?]

Separately, the United Kingdom's Information Commissioner's Office advises that models may implicitly or explicitly encode personal data which they were trained upon.[@ico]
They suggest that obligation to remove this data from the trained model may vary depending on the circumstances, and recommend implementing a model deployment pipeline that enables rapid accommodation of removal requests. 
Indeed, retraining an entire model from scratch due to a removal request is a rather heavy-handed solution, and if individual datapoints could be excised (i.e., *unlearned*) much more quickly, that would be preferable. 


### Copyright {#copyright}

It is well-established that modern machine learning models, including both large language models[@CTWJHLRBSEOR21] and diffusion models,[@SSGGG23][@CHNJSTBIW23] are prone to outputting verbatim or near-verbatim copies of data from their training set.
This is problematic for multiple reasons when these models are trained on large amounts of lightly curated data, scraped from the public internet and proprietary data sources.
As already discussed, these datasets can contain significant amounts of personal information, giving rise to privacy concerns. 
But in addition, such datasets often contain copyrighted material, and reproduction of this material could be a violation of copyright law. 
Indeed, the legal implications of training on copyrighted material are currently being explored in several jurisdictions.[@Getty][@NYT]

Under United States copyright law, a plaintiff can prove that a defendant copied their work by showing that the defendant a) had *access* to the plaintiff's copyrighted work, and b) produced work with *substantial similarity* to the original elements of the plaintiff's work.[@9thCircuit]
If a model is discovered to have been trained on copyrighted material, machine unlearning could be employed to mitigate both of these factors, reducing both the model's access to the copyrighted work, as well as the likelihood that the model will produce an output which is substantially similar. 

Diffusion models are remarkably data-efficient when it comes to mimicking the *style* of an artist, requiring only a few examples before they are able to produce more images in the same style.
Note that under United States law,[@17USC102] style is not generally considered to be protectable by copyright. 
Nonetheless, copying the style of many contemporary artists is considered to be very inappropriate by those in the community and a violation of social norms. 
Unlearning all training data points which belong to a particular artist may remove that model's ability to produce outputs in their style. 

[as: Should we add any discussion at all on probabilistic techniques to protect copyright, e.g. from Boaz and Sham, etc and why they are not sufficient? Why do we need unlearning if we have these techniques?]


### Safety {#safety}

A large focus in AI safety centers around ensuring that models are not able to provide dangerous or harmful information, including, e.g., how to create a bomb or a bioweapon. 
Again, such information may be present on the vast expanses of the internet and enter the model's knowledge through the training procedure. 
While one approach to preventing such capabilities involves building guardrails around them, another approach ensures that the underlying information is not contained in the model in the first place. 
If one identifies all training datapoints that contain such information, they could be removed from the model with machine unlearning techniques. 
Which datapoints ought to be removed can be ambiguous and thus difficult to answer.  
For example, with sufficient knowledge of chemistry and reasoning capabilities, a model may be able to deduce how to create a bomb, but removing knowledge of chemistry would be detrimental to the model's utility in non-harmful scientific domains. 

A related risk concerns models producing images of harmful content, including pornography or violence.
Defining such concepts and determining which training datapoints comprise them is even more difficult, as the line for obscenity is hard to draw even for humans.[@Jacobellis]
Nonetheless, unlearning may be a useful tool in modifying model behaviour to avoid these concepts. 

[as: MINOR AND USELESS: should we change pornography to child pornography. I think many people may debate why "pornography" is good vs bad.]

Finally, an adjacent topic in AI safety involves protection against data poisoning attacks.
In a data poisoning attack, a malicious adversary injects a small number of training datapoints to detrimentally affect the final model. 
If the model owner becomes aware of said poisoned datapoints, they may be able to efficiently mitigate their effect using machine unlearning. 


### Model Utility {#model-utility}

Over the course of a model's deployment, concepts and distributions are likely to shift over time. 
For example, data stating "Justin Trudeau is the Prime Minister of Canada" was no longer accurate after March 14, 2025. 
Models trained on older code might refer to deprecated API calls that no longer work. 
Sometimes, the change is not so abrupt, but still significant. 
Older texts using the word "awful" may employ an archaic definition, meaning "worthy of awe," which is very different from the modern (strictly negative) connotation. 
Accounting for these types of stale data, potentially through machine unlearning or other post-hoc model editing techniques, is essential to making sure a model stays accurate and useful. 



### Understanding Model Properties {#understanding-model-properties}

One of the oldest instances of machine unlearning appears in a 2000 paper of Cauwenberghs and Poggio.[@CP00]
They propose an online algorithm for incrementally training a Support Vector Machine (SVM): given a trained SVM, how can one quickly modify the solution so that it accounts for one more training point? 
They further observe that this procedure can be reversed for the purpose of "decremental 'unlearning,'" which they motivate by the fact that one can quickly evaluate leave-one-out (LOO) performance, a classic measure used to understand model generalization. 

[as: I think this technique can also be used for data attribution, anti-distillation, etc.]

## Discussion {#discussion}

All of these motivations deserve much more nuance than we provide in this tutorial, with considerations particular to the details of each application. 
For example, Cohen, Smith, Swanberg, and Vasudevan[@CSSV23] argue that if one takes a *deletion-as-control* perspective on the right to be forgotten, then training a model once with differential privacy may suffice.
Cooper et al.[@CCBKJFLCHHTKMMJGSDSTBVBCKDLHSBBNWCLPL25] explore considerations for copyright, privacy, and safety in much greater depth. 

Cooper et al. delineate between *targeted removal* and *targeted suppression*, which is an important distinction to make. 
In short, removal is concerned with eliminating the influence of individual training data points on the model, whereas suppression tries to prevent the model from producing certain outputs. 
Confusingly, machine unlearning is often used interchangeably for both concepts, and more. 
Clearly, there is some relationship between removal and suppression. 
For example, if one wishes to suppress verbatim copies of a particular training datapoint from being output, then removing all copies of that training datapoint is likely to suffice. 
But, returning in particular to the *suppression* safety examples above (i.e., providing information on how to build a bomb, or producing violent or pornographic output images), as discussed, removal is neither necessary nor sufficient for these use cases -- assuming that one could even identify which datapoints must be removed in the first place!

Throughout this tutorial, we focus entirely on machine unlearning in the sense of removing specific individual datapoints (or collections thereof). 
Suppression may come as a natural downstream consequence. 
But as we will see in the next part, this notion of unlearning will allow us to reason about the behaviour we would like to enforce: roughly speaking, if points are unlearned from a model, it should behave as if it had never been trained on those points to begin with. 


## References {#references}

1. {#gdpr} [*General Data Protection Regulation*](https://gdpr-info.eu/).
2. {#iapp} [*US State Privacy Legislation Tracker 2026*](https://iapp.org/resources/article/us-state-privacy-legislation-tracker).
3. {#ftc} [*California Company Settles FTC Allegations It Deceived Consumers about use of Facial Recognition in Photo Storage App*](https://www.ftc.gov/news-events/news/press-releases/2021/01/california-company-settles-ftc-allegations-it-deceived-consumers-about-use-facial-recognition-photo). 
4. {#ico} [*How do we ensure individual rights in our AI systems?*](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/how-do-we-ensure-individual-rights-in-our-ai-systems/).
5. {#CP00} Gert Cauwenberghs and Tomaso Poggio. [*Incremental and Decremental Support Vector Machine Learning*](https://papers.nips.cc/paper_files/paper/2000/hash/155fa09596c7e18e50b58eb7e0c6ccb4-Abstract.html). Advances in Neural Information Processing Systems 13. 2000.
6. {#CY15} Yinzhi Cao and Junfeng Yang. [*Towards Making Systems Forget with Machine Unlearning*](https://ieeexplore.ieee.org/document/7163042). 2015 IEEE Symposium on Security and Privacy. 2015.
7. {#CTWJHLRBSEOR21} Nicholas Carlini, Florian Tramer, Eric Wallace, Matthew Jagielski, Ariel Herbert-Voss, Katherine Lee, Adam Roberts, Tom Brown, Dawn Song, Ulfar Erlingsson, Alina Oprea, Colin Raffel. [*Extracting Training Data from Large Language Models*](https://arxiv.org/abs/2012.07805). Proceedings of the 30th USENIX Security Symposium. 2021. 
8. {#CHNJSTBIW23} Nicholas Carlini, Jamie Hayes, Milad Nasr, Matthew Jagielski, Vikash Sehwag, Florian Tramèr, Borja Balle, Daphne Ippolito, Eric Wallace. [*Extracting Training Data from Diffusion Models*](https://arxiv.org/abs/2301.13188). Proceedings of the 32nd USENIX Security Symposium. 2023. 
9. {#Getty} [*Getty Images v. Stability AI*](https://www.judiciary.uk/wp-content/uploads/2025/11/Getty-Images-v-Stability-AI.pdf).
10. {#NYT} [*The New York Times Company v. Microsoft Corporation et al*](https://nytco-assets.nytimes.com/2023/12/NYT_Complaint_Dec2023.pdf).
11. {#9thCircuit} [*17.17 Copying—Access and Substantial Similarity*](https://www3.ce9.uscourts.gov/jury-instructions/node/274). Manual of Model Civil Jury Instructions, the United States Court of Appeals for the Ninth Circuit.
12. {#SSGGG23} Gowthami Somepalli, Vasu Singla, Micah Goldblum, Jonas Geiping, Tom Goldstein. [*Diffusion Art or Digital Forgery? Investigating Data Replication in Diffusion Models*](https://arxiv.org/abs/2212.03860). Proceedings of the 2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition. 2023. 
13. {#Jacobellis} [*Jacobellis v. Ohio*](https://tile.loc.gov/storage-services/service/ll/usrep/usrep378/usrep378184/usrep378184.pdf). 
14. {#CSSV23} Aloni Cohen, Adam Smith, Marika Swanberg, Prashant Nalini Vasudevan. [*Control, Confidentiality, and the Right to be Forgotten*](https://arxiv.org/abs/2210.07876). Proceedings of the 30th ACM Conference on Computer and Communications Security. 2023.
15. {#CCBKJFLCHHTKMMJGSDSTBVBCKDLHSBBNWCLPL25} A. Feder Cooper, Christopher A. Choquette-Choo, Miranda Bogen, Kevin Klyman, Matthew Jagielski, Katja Filippova, Ken Liu, Alexandra Chouldechova, Jamie Hayes, Yangsibo Huang, Eleni Triantafillou, Peter Kairouz, Nicole Elyse Mitchell, Niloofar Mireshghallah, Abigail Z. Jacobs, James Grimmelmann, Vitaly Shmatikov, Christopher De Sa, Ilia Shumailov, Andreas Terzis, Solon Barocas, Jennifer Wortman Vaughan, danah boyd, Yejin Choi, Sanmi Koyejo, Fernando Delgado, Percy Liang, Daniel E. Ho, Pamela Samuelson, Miles Brundage, David Bau, Seth Neel, Hanna Wallach, Amy B. Cyphert, Mark A. Lemley, Nicolas Papernot, Katherine Lee. [*Machine Unlearning Doesn't Do What You Think: Lessons for Generative AI Policy and Research*](https://arxiv.org/abs/2412.06966). Advances in Neural Information Processing Systems 38. 2025.
