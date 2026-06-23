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
As the name suggests, the unlearning procedure $U(M(X), S, Y)$ simply discards the existing model $M(X)$ and trains a model $M(X \setminus S)$ sans the unlearning dataset $S$. 
It is not hard to see that this satisfies exact unlearning. 

The biggest drawback is clearly the amount of time required to serve an unlearning request: even if only a *single point* is to be unlearned ($k=1$), the time required is roughly the same as training the model in the first place, $\Omega(n)$. 
Since modern machine learning models cost an immense amount of resources to train and unlearning requests may be frequent (consider, e.g., right-to-be-forgotten requests), this solution is prohibitively expensive. 
Hence, being able to serve unlearning requests *quickly and effectively* is the primary goal in machine unlearning. 

Retraining from scratch serves as an intuitive example to introduce several other important considerations. 
* **Supported models**: Retrain-from-scratch works for absolutely any learning procedure and model, including both convex and non-convex settings. 
* **Utility**: Since retrain-from-scratch unlearning is exact, *and* the underlying model and training procedure didn't need to be changed, the model's utility will be as high as if unlearning were not a consideration. Other methods we see will compromise on one or both of these factors: either unlearning will be inexact, or the model will have to be changed to support unlearning. Utility can be lost due to either reason. 
* **Training overhead**: Retraining from scratch does not require any additional computation at training time. Of course, this comes at the cost of significant computation required at unlearning time. We will later see methods that incur training overhead to support faster unlearning. 
* **Supplemental information**: Besides the time required to perform an unlearning request, the supplemental information required is the biggest drawback of retraining from scratch. The supplemental information $Y$ must be equal to the entire training dataset $X$. Besides the storage required to keep the training dataset, which may be sizeable, this can also be an issue in terms of regulations related to data retention. 

### Unlearning in Classifiers with Structure {#CY}

Certain classes of classifiers inherently have some convenient structure, which can be exploited for efficient unlearning. 
Following Cao and Yang,[@CY15] we demonstrate this using the naive Bayes classifier as an illustrative example.

Our training dataset will consist of $n$ datapoints, $\{(x^{(i)}, y^{(i)})\}_{i=1}^n$. 
For simplicity, we assume the feature vectors $x \in \{0,1\}^d$ are $d$-dimensional binary vectors, and the labels $y \in \{0,1\}$ are binary. 

To recall, Bayes' theorem implies that 
$$
\Pr[Y = y | X = x] = \frac{\Pr[Y = y] \Pr[X = x | Y= y]}{\Pr[X = x]}.
$$

The naive Bayes classifier further makes the assumption that the features are conditionally independent:
$$
\Pr[X = x | Y= y] = \prod_{j=1}^d \Pr[X_j = x_j | Y = y].
$$

And thus, substituting this into the above, 
$$
\begin{aligned}
\Pr[Y = y | X = x] &= \frac{\Pr[Y = y] \prod_{j=1}^d \Pr[X_j = x_j | Y = y]}{\Pr[X = x]} \\ &\propto \Pr[Y = y] \prod_{j=1}^d \Pr[X_j = x_j | Y = y].
\end{aligned}
$$

The naive Bayes classifier predicts 
$$
\hat{y} = \arg\max_{y} \Pr[Y = y] \prod_{j=1}^d \Pr[X_j = x_j | Y = y].
$$

The key quantities, $\Pr[Y = y]$ and $\Pr[X_j = x_j | Y = y]$, are empirically estimated from the training data. Specifically,
$$
\Pr[Y = y] = \frac{n_y}{n},\ \ \Pr[X_j = 1 | Y = y] = \frac{n_{j,y}}{n_y},
$$
where $n$ is the total number of samples, $n_y$ is the number of samples with label $y$, and $n_{j,y}$ is the number of samples where the $j$-th feature $x_j = 1$ and the label is $y$.
Note that $\Pr[X_j = 0 | Y = y]$ is easy to compute as $1 - \Pr[X_j = 1 | Y = y]$.
The $2 + 2d$ quantities specified above are easy to compute at training time, simply by aggregating the relevant statistics. 

This structure also makes updating these quantities after an unlearning request very efficient. 
Suppose we wish to unlearn a point $(x, y)$. 
Then we can update $d + 2$ counters as follows:
$$
n \gets n - 1,\ \ n_y \gets n_y - 1,\ \ n_{j,y} \gets n_{j,y} - x_j \ \mathrm{for\ all} \ j \in [d],
$$
followed by recomputing all $\Pr[Y = y]$ and $\Pr[X_j = x_j |Y = y]$ as above. 

We can see that exact unlearning requests can be processed quite quickly, in just $O(d)$ time. 
This also imposes minimal training overhead: no new quantities need to be computed, and we just need to store all these counters, which takes $O(d)$ additional space. 
The largest drawback of this method is clearly that it only applies for very restrictive models. 
Cao and Yang showed similar techniques work for other simple models, such as certain types of SVMs and decision trees, but this leaves much to be desired for more complex models employed today. 

### Ginart et al. {#Ginart}

### SISA {#SISA}

### Definitions {#definitions}

### Exact and Approximate Unlearning {#exact-unlearning}


## References {#references}

1. {#DMNS06} Cynthia Dwork, Frank McSherry, Kobbi Nissim, Adam D. Smith. [Calibrating Noise to Sensitivity in Private Data Analysis](https://dl.acm.org/doi/10.1007/11681878_14). Proceedings of the Third Conference on Theory of Cryptography. 2006.
2. {#CY15} Yinzhi Cao and Junfeng Yang. [*Towards Making Systems Forget with Machine Unlearning*](https://ieeexplore.ieee.org/document/7163042). 2015 IEEE Symposium on Security and Privacy. 2015.
