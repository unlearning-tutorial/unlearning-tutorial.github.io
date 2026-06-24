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

We can see that exact unlearning requests can be processed quite quickly, in just $O(d)$ time for unlearning a single sample, or $O(kd)$ time for $k$ samples. 
This also imposes minimal training overhead: no new quantities need to be computed, and we just need to store all these counters, which takes $O(d)$ additional space. 
The largest drawback of this method is clearly that it only applies for very restrictive models. 
Cao and Yang showed similar techniques work for other simple models, such as certain types of SVMs and decision trees, but this leaves much to be desired for more complex models employed today. 


### SISA {#SISA}

SISA[@BCCJTZLP21] is a popular and flexible framework for machine unlearning.
In constrast to the previous example, it can be employed for any model class of interest (i.e., it is *model agnostic*), though it necessitates changes to the overall architecture (via ensembling) and has other drawbacks in terms of utility and unlearning time. 

SISA, which stands for Sharded, Isolated, Sliced, and Aggregated, is based on ideas from ensemble learning and distributed systems. 
The core ideas is as follows: rather than training a single model on a dataset of size $n$, it partitions the data and trains $t$ models, each on a (disjoint) partition of $n/t$ data points.
To be concrete about potential values for $t$, the authors highlight 20 as an upper bound for the number of shards, beyond which losses in utility may be too severe. 
Outputs of these $t$ models are then aggregated in some way: for example, for classification tasks, one can consider a simple label-based majority vote. 

While this is is not the full description of SISA, it already suffices to see why we can expect to have more efficient support for unlearning. 
Suppose we wish to unlearn one training data point. 
A simple approach is to retrain from scratch, but exclusively on the shard containing the point to be unlearned. 
Thus, rather than retraining a model on all $n$ data points, we only retrain a model on $n/t$ data points -- if training time is linear in the dataset size, then this saves a factor of $t$ in the running time. 
Recalling that $t$ may be on the order of $10$ to $20$, this might be an order of magnitude speedup for an unlearning request. 
However, this advantage can quickly disappear if there are many points to be unlearned, as the amount of computation scales linearly in the number of unique shards the points requested to be unlearned fall into. 
Therefore, if the number of points to unlearn $k \gg t$, then it is likely that the unlearning request will amount to a full retrain from scratch.

The final pertinent technique in SISA is *slicing*.
This applies a similar idea as sharding, but within the training process of each shard. 
Within each shard, we randomly partition the data into $r$ disjoint slices. 
We first train exclusively on the first slice within the shard.
We then continue training on the combined first and second slice within the shard.
In general, we go through $r$ phases, and during the $i$th phase, we train on the first $i$ slices of the shard. 
A model checkpoint is saved at the end of each phase.

Unlearning requests are again handled by only redoing computation where the points to be unlearned were employed. 
Again, suppose we wish to unlearn one training data point. 
As an extreme case, if the point falls into the last slice in a shard, then the first $r-1$ phases are unaffected.
We can load the second-last model checkpoint and only re-run the last phase of training. 
In this best-case scenario, this saves a factor of $\frac{r+1}{2}$ in the computation versus retraining the shard from scratch -- though, since we assume that the slices were partitioned uniformly at random, this event happens with probability only $1/r$. 
On average, the point to be unlearned will fall into a slice somewhere in the middle. 
In this case, the savings are more modest since we have to re-run several phases: with enough shards, the expected speedup is around $1.5\times$ when unlearning a single point. 
However, once again, this decays as more points must be unlearned from a shard, since one must continue from the checkpoint before to the earliest phase containing an unlearned point. 

Choosing the number of shards $t$ and the number of slices $r$ is a difficult balance. 
Increasing the number of shards $t$ will decrease the time needed to process an unlearning request, but decrease the model's utility (as is common for ensemble methods) and increase the requisite amount of storage. 
Increasing the number of slices $r$ also speeds up unlearning requests (up to a point), but also increases the required storage. 
Regardless, the speedup decays rapidly as we increase the number of points to be unlearned, making SISA most appropriate when we expect to be unlearning a relatively limited number of points. 

A few additional comments are in order: 
* **Supported models**: As already mentioned, SISA is an extremely flexible framework, supporting a broad range of classifiers. There are some mild restrictions to realize the benefits of slicing: any model trained with gradient descent is suitable, but, e.g., decision trees are not, since creating a decision tree requires inspecting the entire dataset, and we can not iteratively build the tree with only one slice at a time. 
* **Training overhead**: Training overhead for SISA is fairly minimal, though hyperparameter tuning can be more costly due to the more complex pipeline. 
* **Supplemental Information**: This is another non-trivial overhead for SISA. In addition to storing the entire dataset, $r$ model checkpoints must be saved for each of the $t$ models in the ensemble. For suggested choices of these hyperparameters, this may incur storing more than $100$ times more weights than a single base model. 






## TODO 
* Heuristic methods
* Evaluating heuristic methods
* Heuristic methods don't really work

* Provable methods
* DP baseline
* Gradient descent methods
* Descent-to-delete
* Influence functions


1. {#DMNS06} Cynthia Dwork, Frank McSherry, Kobbi Nissim, Adam D. Smith. [Calibrating Noise to Sensitivity in Private Data Analysis](https://dl.acm.org/doi/10.1007/11681878_14). Proceedings of the Third Conference on Theory of Cryptography. 2006.
2. {#CY15} Yinzhi Cao and Junfeng Yang. [*Towards Making Systems Forget with Machine Unlearning*](https://ieeexplore.ieee.org/document/7163042). 2015 IEEE Symposium on Security and Privacy. 2015.
3. {#BCCJTZLP21} Lucas Bourtoule, Varun Chandrasekaran, Christopher A. Choquette-Choo, Hengrui Jia, Adelin Travers, Baiwu Zhang, David Lie, Nicolas Papernot. [*Machine Unlearning*](https://arxiv.org/abs/1912.03817). 2021 IEEE Symposium on Security and Privacy. 2021. 
