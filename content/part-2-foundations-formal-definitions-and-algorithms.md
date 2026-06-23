---
part: Part 2
title: "Definitions and Algorithms"
description: "Part 2 of Unlearning Data at Scale: Definitions and algorithms."
dek: "TBD."
output: part-2-foundations-formal-definitions-and-algorithms.html
---

## Exact Unlearning {#exact}

We begin with describing what we consider to be the ideal form of machine unlearning: *exact unlearning*. 
Informally, this requires that the model after unlearning a set of datapoints is exactly the same as if those datapoints were not trained on in the first place. 
We set up a bit of notation to be more precise. 

Let $X$ be a training dataset of size $n$ and let $M$ be a training algorithm which takes in a training dataset and outputs a trained model. 
Furthermore, let $S \subseteq X$ be a dataset of size $k$ we wish to unlearn, and $U$ be an unlearning algorithm which takes in a trained model and set of points we wish to unlearn. 
Then we say that $M$ and $U$ satisfy *exact unlearning* if, for any training dataset $X$ and unlearning dataset $S \subseteq X$, we have that
$$
M(X \setminus S) = U(M(X), S).
$$
The left-hand side of this equality corresponds to the universe in which the unlearning dataset $S$ was never trained on. 
The right-hand side corresponds to the universe where the entire training dataset $X$ was initially trained on, but $S$ was later unlearned. 
The models that result from both these processes should be exactly equal. 

While the above equality is useful for some intuition about our goal, it has some deficiencies. 
Most significantly, essentially all training algorithms $M$ involve some form of randomness, and thus saying the models are "equal" is not well defined.
The natural adaptation is to say that the distributions over models are equal. 
For reasons that will become clear later, we phrase this condition in a manner reminiscent of differential privacy.[@DMNS06]
$M$ and $U$ satisfy *exact unlearning* if, for any training dataset $X$, unlearning dataset $S \subseteq X$, and event $T \subseteq \mathrm{Range}(M)$ we have that
$$
\Pr[M(X \setminus S) \in T] = \Pr[U(M(X), S) \in T].
$$

As one last modification for the time being: at present, the unlearning algorithm $U$ has access only to the trained model $M(X)$ and the datapoints to be unlearned $S$. 
In general, the unlearning algorithm will need additional information to handle unlearning requests. 
We abstractly denote this *supplemental information* as $Y$, which is the third argument for the unlearning algorithm: $U(M(X), S, Y)$. 

## Exact Unlearning Algorithms {#exact-algorithms}

### Retrain from scratch {#RFS}

With exact unlearning defined, we start with the most obvious method for machine unlearning: retraining from scratch. 
As the name suggests, the unlearning procedure simply discards the existing model $M(X)$ and trains a model $M(X \setminus S)$ sans the unlearning dataset $S$. 
It is not hard to see that this satisfies exact unlearning. 

The biggest drawback is clearly the amount of time required to serve an unlearning request: even if only a *single point* is to be unlearned ($k=1$), the time required is roughly the same as training the model in the first place, $\Omega(n)$. 
Since modern machine learning models cost an immense amount of resources to train and unlearning requests may be frequent (consider, e.g., right-to-be-forgotten requests), this solution is prohibitively expensive. 
Hence, being able to serve unlearning requests *quickly and effectively* is the primary goal in machine unlearning. 

Retraining from scratch serves as an intuitive example to introduce several other important considerations, which we discuss briefly. 
* **Supported models**: Retrain-from-scratch works for absolutely any learning procedure and model, including both convex and non-convex settings. 
* **Utility**: Since retrain-from-scratch unlearning is exact, *and* the underlying model and training procedure didn't need to be changed, the model's utility will be as high as if unlearning were not a consideration. Other methods we see will compromise on one or both of these factors: either unlearning will be inexact, or the model will have to be changed to support unlearning. Utility can be lost due to either reason. 
* **Training overhead**: Retraining from scratch does not require any additional computation at training time. Of course, this comes at the cost of significant computation required at unlearning time. We will later see methods that incur training overhead to handle faster unlearning. 
* **Supplemental information**: Besides the time required to perform an unlearning request, the supplemental information required is the biggest drawback of retraining from scratch. The supplemental information $Y$ must be equal to the entire training dataset $X$. Besides the storage required to keep the training dataset, which may be sizeable, this can also be an issue in terms of regulation related to data retention. 

### Cao Yang {#CY}

### Ginart et al. {#Ginart}

### SISA {#SISA}

### Definitions {#definitions}

### Exact and Approximate Unlearning {#exact-unlearning}

Add your definitions here, including notation, assumptions, and how unlearning outputs are compared against retraining baselines.

For example, let the empirical risk over a dataset $D = \{(x_i, y_i)\}_{i=1}^n$ be

$$
R_D(\theta) = \frac{1}{n}\sum_{i=1}^n \ell(f_\theta(x_i), y_i).
$$

If a deletion request removes a subset $S \subset D$, an exact unlearning target is often described as producing parameters $\theta^{-S}$ that match retraining on the retained data:

$$
\theta^{-S} \approx \arg\min_\theta R_{D \setminus S}(\theta).
$$

### Evaluation Criteria {#evaluation}

Use this section for deletion guarantees, utility retention, computational efficiency, memory costs, and adversarial evaluation.

## Algorithmic Families {#algorithms}

Describe the main classes of methods here, such as retraining, sharding, influence-based updates, certified methods, or other techniques relevant to your tutorial.[@ref-2]

- Algorithm family one
- Algorithm family two
- Algorithm family three

## Discussion {#discussion}

This section can synthesize the formal landscape and explain which assumptions are mathematically convenient versus practically meaningful.

## References {#references}

1. {#DMNS06} Cynthia Dwork, Frank McSherry, Kobbi Nissim, Adam D. Smith. [Calibrating Noise to Sensitivity in Private Data Analysis](https://dl.acm.org/doi/10.1007/11681878_14). Proceedings of the Third Conference on Theory of Cryptography. 2006.

