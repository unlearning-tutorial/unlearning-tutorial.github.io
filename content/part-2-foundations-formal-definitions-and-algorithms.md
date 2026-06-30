---
part: Part 2
title: "Definitions and Algorithms"
description: "Part 2 of Unlearning Data at Scale: Definitions and algorithms."
dek: "TBD."
output: part-2-foundations-formal-definitions-and-algorithms.html
---

## Exact Unlearning {#exact}

We begin by describing what we consider to be the ideal form of machine unlearning: *exact unlearning*. 
Informally, this requires that the model after unlearning a set of datapoints is exactly the same as if those datapoints were not trained on in the first place. 
We set up a bit of notation to be more precise. 

Let $X$ be a training dataset of size $n$ and let $M$ be a training algorithm which takes in a training dataset and outputs a trained model. 
Furthermore, let $S \subseteq X$ be a dataset of size $k$ we wish to unlearn, and $U$ be an unlearning algorithm which takes in a trained model and a set of points we wish to unlearn. 
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

Retraining from scratch serves as an intuitive example to introduce many axes by which we judge unlearning procedures. 
* **Unlearning time**: Poor, retraining from scratch is the slowest possible baseline. 
* **Supported models**: Retrain-from-scratch works for absolutely any learning procedure and model, including both convex and non-convex settings. 
* **Effect of large unlearning set**: Retraining from scratch can handle unlearning sets $S$ of any size -- sufficiently large sets will actually reduce the time slightly. 
* **Utility**: Since retrain-from-scratch unlearning is exact, *and* the underlying model and training procedure didn't need to be changed, the model's utility will be as high as if unlearning were not a consideration. Other methods we see will compromise on one or both of these factors: either unlearning will be inexact, or the model will have to be changed to support unlearning. Utility can be lost due to either reason. 
* **Training overhead**: Retraining from scratch does not require any additional computation at training time. Of course, this comes at the cost of significant computation required at unlearning time. We will later see methods that incur training overhead to support faster unlearning. 
* **Supplemental information**: Besides the time required to perform an unlearning request, the supplemental information required is the biggest drawback of retraining from scratch. The supplemental information $Y$ must be equal to the entire training dataset $X$. Besides the storage required to keep the training dataset, which may be sizeable, this can also be an issue in terms of regulations related to data retention. 

### Unlearning in Classifiers with Structure {#CY}

Certain classes of classifiers inherently have some convenient structure, which can be exploited for efficient unlearning. 
We first illustrate this via a toy example of mean estimation, then subsequently via the naive Bayes classifier, following the example of Cao and Yang.[@CY15]

#### Mean estimation

Suppose we have a dataset $x_1, \dots, x_n \in \mathbb{R}^d$, and we want to compute their average. 
This is equivalent to finding the point that minimizes the average squared loss: 
$$
\mu = \arg \min_\theta \sum_{i=1}^n \|x_i - \theta\|^2.
$$
This quantity can easily be computed in $O(nd)$ time in the trivial way:
$$
\mu = \frac{1}{n} \sum_{i=1}^n x_i.
$$

Suppose we want to unlearn a single point -- without loss of generality, let that point be $x_n$. 
We could compute the new mean $\mu'$ naively in $O(nd)$ time via "retraining from scratch":
$$
\mu' = \frac{1}{n-1} \sum_{i=1}^{n-1} x_i.
$$
But a moment's thought reveals that $\mu'$ can be obtained by a simple transformation from $\mu$. 
Simply de-normalize, subtract out the point(s) to be unlearned, and renormalize:
$$
\mu'= \frac{1}{n-1}\left(n \mu - x_n\right).
$$
This method takes $O(d)$ time (or, for unlearning $k$ points, $O(kd)$ time), rather than the naive method, which required $O(nd)$ time. 
Though an extremely simplistic setting, it demonstrates that certain statistical tasks have sufficient structure to permit efficient unlearning. 

#### Naive Bayes 
Now we turn our attention to naive Bayes classifiers. 
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

To summarize: 
* **Unlearning time**: Very efficient, linear in the size of the unlearn set. 
* **Supported models**: Highly limited, only restricted classes of models.  
* **Effect of large unlearning set**: Minimal, unlearning time scales linearly in size of the set. 
* **Utility**: Exact unlearning, so it suffers no loss in utility. However, if we have to change to a model that supports this type of unlearning, we may suffer significant utility loss.  
* **Training overhead**: Minimal, only needs to compute all the counters. 
* **Supplemental information**: Minimal, only needs to store all the counters. 


### SISA {#SISA}

SISA[@BCCJTZLP21] is a popular and flexible framework for machine unlearning.
In contrast to the previous example, it can be employed for any model class of interest (i.e., it is *model agnostic*), though it necessitates changes to the overall architecture (via ensembling) and has other drawbacks in terms of utility and unlearning time. 

SISA, which stands for Sharded, Isolated, Sliced, and Aggregated, is based on ideas from ensemble learning and distributed systems. 
The core idea is as follows: rather than training a single model on a dataset of size $n$, it partitions the data and trains $t$ models, each on a (disjoint) partition of $n/t$ data points.
To be concrete about potential values for $t$, the authors highlight 20 as an upper bound for the number of shards, beyond which losses in utility may be too severe. 
Outputs of these $t$ models are then aggregated in some way: for example, for classification tasks, one can consider a simple label-based majority vote. 

While this is not the full description of SISA, it already suffices to see why we can expect to have more efficient support for unlearning. 
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
However, once again, this decays as more points must be unlearned from a shard, since one must continue from the checkpoint before the earliest phase containing an unlearned point. 

Choosing the number of shards $t$ and the number of slices $r$ is a difficult balance. 
Increasing the number of shards $t$ will decrease the time needed to process an unlearning request, but decrease the model's utility (as is common for ensemble methods) and increase the requisite amount of storage. 
Increasing the number of slices $r$ also speeds up unlearning requests (up to a point), but also increases the required storage. 
Regardless, the speedup decays rapidly as we increase the number of points to be unlearned, making SISA most appropriate when we expect to be unlearning a relatively limited number of points. 

To summarize and discuss a few additional points:
* **Unlearning time**: Can be an order of magnitude speedup, depending on parameter choices. But improvement degrades quickly for larger unlearning sets.  
* **Supported models**: As already mentioned, SISA is an extremely flexible framework, supporting a broad range of classifiers. There are some mild restrictions to realize the benefits of slicing: any model trained with gradient descent is suitable, but, e.g., decision trees are not, since creating a decision tree requires inspecting the entire dataset, and we can not iteratively build the tree with only one slice at a time. 
* **Effect of large unlearning set**: As discussed before, if the unlearning set is too large, then SISA is no more computationally efficient than retraining from scratch. 
* **Utility**: Exact unlearning suffers no utility loss compared to retraining from scratch, but adopting the ensemble architecture required by SISA can be costly.   
* **Training overhead**: Training overhead for SISA is fairly minimal, though hyperparameter tuning can be more costly due to the more complex pipeline. 
* **Supplemental information**: This is another non-trivial overhead for SISA. In addition to storing the entire dataset, $r$ model checkpoints must be saved for each of the $t$ models in the ensemble. For suggested choices of these hyperparameters, this may incur storing more than $100$ times more weights than a single base model. 

#### Aside: Pitfalls in Adaptive Machine Unlearning

SISA allows us to illustrate an interesting pitfall of some exact unlearning methods: they implicitly assume the unlearning requests made are *independent* of the actual models published. 
This assumption is likely to be broken: for example, individuals may request for their data to be deleted if they don't like what the model reveals about them. 
We illustrate what can go wrong when unlearning requests are *adaptive*.[@GJNRSW21]

For methods like SISA, the main problem is that the randomness of partitioning the data is performed only once, at the initial training time.
An adversary can request points to be unlearned based on this randomness, which invalidates the exact unlearning guarantees. 

We demonstrate with a toy example. 
Consider first a model class akin to a lookup table. 
Suppose a model $f$ is given a training dataset $\mathcal{D}$. 
On a test example $x$, it outputs the label $y$ if $(x, y)$ is a point in $\mathcal{D}$, and $\bot$ otherwise. 

Now, we consider a dataset of $2n$ points $\{(x_i, y_i)\}_{i=1}^{2n}$, where there are exactly two copies of each distinct training example. 
Randomly partition this dataset into three shards, train a model $f$ on each of them, and predict the majority vote of the three models.
It is easy to see that this ensemble will be correct on exactly the points where the duplicates fell into different shards. 
The resulting accuracy of the training set will be roughly $2/3$. 

However, consider what happens when the model receives an unlearning request. 
An adversary could ask for every correctly classified point to be deleted. 
At this point, all remaining points would have duplicates falling into the same shard, and thus be predicted incorrectly: the resulting accuracy would be $0$. 
This is very different than what would happen if the model was retrained from scratch, since the re-randomization into new shards would result in accuracy being roughly $2/3$ for every remaining point again. 

While this example is for a very simplistic case, effective attacks have been demonstrated for more realistic applications of SISA.[@GJNRSW21]
The authors also use differential privacy to show how to mitigate such attacks. 
However, the bigger point here is that extra care is needed to deal with messiness of unlearning requests that may arise in the real world. 


## (Certified) Approximate Unlearning

Exact unlearning is an extremely stringent requirement.
While we have seen it can be achieved in some cases, it often comes with significant drawbacks, including only working for certain model classes, decreased utility, support for unlearning only a limited number of data points, and more. 
To address these drawbacks, researchers have relaxed the requirement of exactness, asking only for *approximate* unlearning. 
There are many ways one could relax exactness, we focus primarily on the most popular relaxation, which we first introduce informally. 

$M$ and $U$ satisfy *approximate unlearning* if, for any training dataset $X$, unlearning dataset $S \subseteq X$, and event $T \subseteq \mathrm{Range}(M)$ we have that
$$
\Pr[M(X \setminus S) \in T] \approx \Pr[U(M(X), S, Y) \in T].
$$

This is the same as the definition of *exact unlearning* we introduced before, the only difference being that the $=$ is now an $\approx$. 
That is, we should *approximately* preserve the probability of any model being output, between the two cases that a) the model is trained from scratch on $X \setminus S$ and b) the model is first trained on $X$ and then $S$ is unlearned. 

The remaining question is how to define $\approx$ in this setting. 
Borrowing from the differential privacy literature,[@DMNS06] several works[@GGVZ19][@GGHM20][@NRS21][@SAKS21] have defined approximate unlearning as follows.  

$M$ and $U$ satisfy *$(\varepsilon, \delta)$-approximate unlearning* if, for any training dataset $X$, unlearning dataset $S \subseteq X$, and event $T \subseteq \mathrm{Range}(M)$ we have that
$$
\begin{aligned}
\Pr[M(X \setminus S) \in T] &\leq e^{\varepsilon}\Pr[U(M(X), S, Y) \in T] + \delta, \\
\Pr[U(M(X), S, Y) \in T] &\leq e^{\varepsilon}\Pr[M(X \setminus S) \in T] + \delta.
\end{aligned}
$$
To interpret this, the probability of each event should be preserved up to a multiplicative $e^\varepsilon$ (which, for small epsilon, could be thought of as roughly $1+\varepsilon$), with an additive slack of $\delta$. 
Generally, we think of $\varepsilon$ as being a single-digit constant (e.g., $\varepsilon = 1$), while $\delta$ (which allows for probabilities of catastrophic failure of unlearning) is generally taken to be much smaller (e.g., $\delta < 10^{-5}$). 
While this definition can be a bit of a mouthful, operationally, it suffices to know that it's generally accepted as a strong notion of approximation: if you perform unlearning, the model's behavior is very similar to as if you retrained from scratch. 

With this definition in place, we turn our attention to how to guarantee approximate unlearning. 
Perhaps surprisingly, there exist methods to *mathematically prove* (or *certify*) that an unlearning procedure satisfies approximate unlearning. 
While these can be heavy or limited in the situations in which they apply, the ability to give mathematical guarantees of approximate unlearning is very strong. 

### Differential Privacy

Differential privacy (DP)[@DMNS06] is a rigorous notion of data privacy, employed in practice by many organizations, including Google, Apple, Microsoft, and the US Census Bureau. 
As mentioned before, the most popular definition of approximate machine unlearning arises from DP.
In fact, as we will see shortly, DP immediately implies machine unlearning, though it is not without its drawbacks. 

First, we note the definition: we say an algorithm $M$ is $(\varepsilon, \delta)$-DP if, for any datasets $X$ and $X'$ that differ in exactly one element, and any event $T \subseteq \mathrm{Range}(M)$, we have that
$$
\Pr[M(X) \in T] \leq e^\varepsilon \Pr[M(X') \in T] + \delta. 
$$

Observe the similarity to the approximate machine unlearning definition. 
In particular, suppose we let the learning algorithm $M$ be $(\varepsilon, \delta)$-DP, and the unlearning algorithm $U$ simply returns the same model, i.e., $U(M(X), S, Y) = M(X)$. 
Then we have that, for any $S$ of size $1$,
$$
\Pr[U(M(X), S, Y) \in T] = \Pr[M(X) \in T] \\ \leq e^\varepsilon \Pr[M(X') \in T] + \delta = e^\varepsilon \Pr[M(X \setminus S) \in T] + \delta.
$$
The first equality is from how we defined the unlearning algorithm $U$. The inequality is due to the definition of DP. The second equality is due to the fact that $X \setminus S$ can be written as some neighboring dataset $X'$.
To interpret what this means, it says that a differentially private algorithm has *automatically unlearned* every set of size $1$, without doing anything at all at unlearning time! 
This can be a bit counterintuitive: *simultaneously* unlearning every point is a very strong guarantee, especially without having to do anything to process an unlearn request. 
Nonetheless, it can be verified that it satisfies the stated definition. 

As stated, DP only guarantees unlearning for unlearning sets $S$ of size $1$. 
Fortunately, a property known as group privacy allows the guarantees to degrade gracefully for unlearning sets $S$ of size $k$, though unfortunately, at too great a cost to handle large $k$. 
Specifically, group privacy says that an $(\varepsilon,\delta)$-DP algorithm satisfies the following guarantees for any datasets $X$ and $X'$ which differ in exactly $k$ entries: 
$$
\Pr[M(X) \in T] \leq e^{k\varepsilon} \Pr[M(X') \in T] + ke^{(k-1)\varepsilon}\delta. 
$$
As we can see, the guarantees degrade exponentially in the size of the unlearning set $k$, which gives very weak unlearning for sets of larger size. 
This is the principal downside of using DP directly for machine unlearning. 

On the bright side, we have fairly general algorithms for training models with DP. 
Differentially Private Stochastic Gradient Descent (DPSGD)[@SCS13][@BST14][@ACGMMTZ16] serves as a drop-in private replacement for SGD, differing in that individual gradients are clipped and noise is added to their aggregate at each step. 
Any model trained with DPSGD will be DP. 
With significant work on DP machine learning, training overhead is relatively minor, and utility loss can be modest to significant, depending on whether or not there is public data to help the model form a strong prior[@DBHSB22] -- in the setting of machine unlearning, public data serves as data that cannot be unlearned. 

As stated above, using DP for unlearning can be overkill: it unlearns *every* set of size $1$ simultaneously. 
But when we want to do unlearning, we only require unlearning a particular set of interest.
Consequently, algorithms that are tailored to the unlearning set $S$ can perform significantly better than generic DP methods, in particular, bypassing lower bounds for DP. 

To summarize: 
* **Unlearning time**: DP allows instant unlearning, as the model remains unchanged. 
* **Effect of large unlearning set**: Unlearning guarantees weaken significantly as the unlearning set size $k$ increases. 
* **Supported models**: DPSGD works for essentially any model trained with gradient descent, there exist DP algorithms for other settings as well. 
* **Utility**: DP can cause a modest to significant drop in the model utility, depending on the exact setting. 
* **Training overhead**: Modern DPSGD pipelines have minimal training time overhead. 
* **Supplemental information**: None required. 

### Influence Functions

Influence functions are a classic technique from robust statistics.[@Hampel74]
They have recently been popularized in machine learning, for understanding the influence of individual training data points.[@KL17]
Consequently, they are at the heart of a key method for approximate machine unlearning.[@GGVZ19][@GAS20][@SAKS21][@SW22]

The influence function is meant to answer the following question: if we changed the weight of a single training data point by an infinitesimal amount, how much would the parameters of a model trained on that dataset change? 
In more detail, suppose we have a training dataset $\{z_i\}_{i=1}^n$, and a strongly convex loss function $\ell$. 
The empirical risk minimization (ERM) problem asks to solve
$$
\hat \theta \triangleq \arg\min_\theta \frac{1}{n} \sum_{i=1}^n \ell(z_i, \theta).
$$
Consider increasing the weight of one point $z_j$ by a small amount $\gamma$, and define $\hat \theta_{\gamma,j}$ to be the new ERM solution:
$$
\hat \theta_{\gamma,j} \triangleq \arg\min_\theta \frac{1}{n} \sum_{i=1}^n \ell(z_i, \theta) + \gamma \ell(z_j, \theta). 
$$

A classic result of Cook and Weisberg[@CW82] gives us the following derivative for the parameter vector:
$$
\mathcal{I}(z_j) \triangleq \left. \frac{d\hat{\theta}_{\gamma,j}}{d\gamma} \right|_{\gamma=0} = -H_{\hat{\theta}}^{-1} \nabla_{\theta} \ell(z_j, \hat{\theta}),
$$
where $H_{\hat \theta} \triangleq \frac{1}{n}\sum_{i=1}^n \nabla_\theta^2 \ell(z_i, \hat \theta)$ is the Hessian matrix of the loss at the solution $\hat \theta$. 

What does such a derivative get us? If we have $\hat \theta$, and we can compute $\mathcal{I}(z_j)$, this allows us to form the approximation
$$
\hat \theta_{\gamma,j} \approx \hat \theta + \gamma \mathcal{I}(z_j).
$$
For our setting of unlearning, $\hat \theta_{-1/n, j}$ corresponds to the ERM solution after unlearning point $z_j$, and thus we can approximate
$$
\hat \theta_{-1/n,j} \approx \hat \theta - \frac{1}{n}\mathcal{I}(z_j) = \hat \theta + \frac{1}{n} H_{\hat{\theta}}^{-1} \nabla_{\theta} \ell(z_j, \hat{\theta}). 
$$

What did we do here? This took a quadratic approximation for the empirical risk around the original solution $\hat \theta$. 
The resulting update corresponds to a Newton step on the point to be unlearned. 
Note that it is straightforward to unlearn a batch of points, instead of just one: simply sum the influence functions, corresponding to taking a Newton step on the entire set of points to be unlearned. 

What is the cost of this procedure? 
The most expensive part is computing, storing, and inverting the Hessian. 
Fortunately, this can be done at initialization, taking $O(nd^2)$ time to compute the Hessian, followed by $O(d^3)$ time to invert. 
Subsequently, processing an unlearning request takes just $O(kd + d^2)$ time, to compute the gradients of the unlearn points, followed by the matrix-vector product to compute the update. 

Note that influence functions only allow us to *approximate* the value of the *parameter vector* as if we retrained from scratch.
In order to give the stronger guarantee as required by approximate unlearning, we must add Gaussian noise to the parameter vector in order to mask the difference; analysis is similar to the Gaussian mechanism from differential privacy.[@DKMMN06]

The most significant drawback of this approach is that it gives certifiable machine unlearning only for convex models. 
This is because we have to bound the error of the approximation due to influence functions, which can only be done for convex settings. 
Nonetheless, there is some evidence that this method can be reasonably effective in non-convex settings.[@MTBRPMG26]

In summary:  
* **Unlearning time**: Influence functions allow for $O(d^2)$ time unlearning, independent of $n$. 
* **Effect of large unlearning set**: Minimal, as running time scales slowly in the size of the unlearn set. However, as many requests are processed, the quality of the influence function approximation might degrade. 
* **Supported models**: Only convex models can give certifiable machine unlearning guarantees. 
* **Utility**: The noise addition and approximation error can give a modest decrease in utility.  
* **Training overhead**: Can be significant, as computing and inverting the Hessian is an expensive operation. 
* **Supplemental information**: Requires storing the inverse Hessian matrix. 

## Discussion

In this part, we saw definitions and a variety of methods for machine unlearning.
While all of them provide strong provable guarantees, they each have their own deficiencies. 
Drawbacks range from significant time to perform an unlearning request, capacity for only a small number of unlearning requests, big hits to utility, or restriction to only simple (e.g., convex) models. 
In the next part, we will see more methods for machine unlearning, which address some of these concerns by eschewing the need for certifiable unlearning. 
As we will see, this leads to a number of other challenges, such as how to *evaluate* machine unlearning. 


1. {#DMNS06} Cynthia Dwork, Frank McSherry, Kobbi Nissim, Adam D. Smith. [Calibrating Noise to Sensitivity in Private Data Analysis](https://dl.acm.org/doi/10.1007/11681878_14). Proceedings of the Third Conference on Theory of Cryptography. 2006.
2. {#CY15} Yinzhi Cao and Junfeng Yang. [*Towards Making Systems Forget with Machine Unlearning*](https://ieeexplore.ieee.org/document/7163042). 2015 IEEE Symposium on Security and Privacy. 2015.
3. {#BCCJTZLP21} Lucas Bourtoule, Varun Chandrasekaran, Christopher A. Choquette-Choo, Hengrui Jia, Adelin Travers, Baiwu Zhang, David Lie, Nicolas Papernot. [*Machine Unlearning*](https://arxiv.org/abs/1912.03817). 2021 IEEE Symposium on Security and Privacy. 2021. 
4. {#GJNRSW21} Varun Gupta, Christopher Jung, Seth Neel, Aaron Roth, Saeed Sharifi-Malvajerdi, Chris Waites. [*Adaptive Machine Unlearning*](https://arxiv.org/abs/2106.04378). Advances in Neural Information Processing Systems 34. 2021. 
5. {#GGVZ19} Chuan Guo, Tom Goldstein, Awni Hannun, Laurens van der Maaten. [*Certified Data Removal from Machine Learning Models*](https://arxiv.org/abs/1911.03030). Proceedings of the 37th International Conference on Machine Learning. 2020.
6. {#GGHM20} Antonio Ginart, Melody Y. Guan, Gregory Valiant, James Zou. [*Making AI Forget You: Data Deletion in Machine Learning*](https://arxiv.org/abs/1907.05012). Advances in Neural Information Processing Systems 32. 2019.
7. {#NRS21} Seth Neel, Aaron Roth, Saeed Sharifi-Malvajerdi. [*Descent-to-Delete: Gradient-Based Methods for Machine Unlearning*](https://arxiv.org/abs/2007.02923). Proceedings of the 32nd International Conference on Algorithmic Learning Theory. 2021. 
8. {#SAKS21} Ayush Sekhari, Jayadev Acharya, Gautam Kamath, Ananda Theertha Suresh. [*Remember What You Want to Forget: Algorithms for Machine Unlearning*](https://arxiv.org/abs/2103.03279). Advances in Neural Information Processing Systems 34. 2021. 
9. {#SCS13} Shuang Song, Kamalika Chaudhuri, Anand Sarwate. [*Stochastic Gradient Descent with Differentially Private Updates*](https://ieeexplore.ieee.org/document/6736861). Proceedings of the 2013 IEEE Global Conference on Signal and Information Processing. 2013. 
10. {#BST14} Raef Bassily, Adam Smith, Abhradeep Thakurta. [*Private Empirical Risk Minimization: Efficient Algorithms and Tight Error Bounds*](https://arxiv.org/abs/1405.7085). Proceedings of the 55th Annual Symposium on Foundations of Computer Science. 2014. 
11. {#ACGMMTZ16} Martín Abadi, Andy Chu, Ian Goodfellow, H. Brendan McMahan, Ilya Mironov, Kunal Talwar, Li Zhang. [*Deep Learning with Differential Privacy*](https://arxiv.org/abs/1607.00133). Proceedings of the 2016 ACM SIGSAC Conference on Computer and Communications Security. 2016.
12. {#DBHSB22} Soham De, Leonard Berrada, Jamie Hayes, Samuel L. Smith, Borja Balle. [*Unlocking High-Accuracy Differentially Private Image Classification through Scale*](https://arxiv.org/abs/2204.13650). arXiv:2204.13650. 2022. 
13. {#SW22} Vinith M. Suriyakumar, Ashia C. Wilson. [*Algorithms that Approximate Data Removal: New Results and Limitations*](https://arxiv.org/abs/2209.12269). Advances in Neural Information Processing Systems 35. 2022. 
14. {#GAS20} Aditya Golatkar, Alessandro Achille, Stefano Soatto. [*Eternal Sunshine of the Spotless Net: Selective Forgetting in Deep Networks*](https://arxiv.org/abs/1911.04933). Proceedings of the 2020 IEEE/CVF Conference on Computer Vision and Pattern Recognition. 2020. 
15. {#MTBRPMG26} Lev McKinney, Anvith Thudi, Juhan Bae, Tara Rezaei, Nicolas Papernot, Sheila A. McIlraith, Roger Grosse. [*Gauss-Newton Unlearning for the LLM Era*](https://arxiv.org/abs/2602.10568). Proceedings of the 4th IEEE Conference on Secure and Trustworthy Machine Learning. 2026. 
16. {#KL17} Pang Wei Koh, Percy Liang. [*Understanding Black-box Predictions via Influence Functions*](https://arxiv.org/abs/1703.04730). Proceedings of the 34th International Conference on Machine Learning. 2017. 
17. {#Hampel74} Frank R. Hampel. [*The Influence Curve and Its Role in Robust Estimation*](https://www.jstor.org/stable/2285666). Journal of the American Statistical Association, Vol. 69, No. 346. 1974. 
18. {#DKMMN06} Cynthia Dwork, Krishnaram Kenthapadi, Frank McSherry, Ilya Mironov, Moni Naor. [*Our Data, Ourselves: Privacy Via Distributed Noise Generation*](https://link.springer.com/chapter/10.1007/11761679_29). Annual International Conference on the Theory and Applications of Cryptographic Techniques. 2006.
19. {#CW82} Dennis R. Cook and Sanford Weisberg. [*Residuals and Influence in Regression*](https://conservancy.umn.edu/items/128d305b-746c-4f3d-be1b-d0e37e7ff6e9). Chapman and Hall. 1982.  
