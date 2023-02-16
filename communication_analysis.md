- [Communication Analysis](#communication-analysis)
- [Communication Results](#communication-results)
  - [State Machine](#state-machine)
    - [Communication: Send Input](#communication-send-input)
    - [Communication: Compute Next State](#communication-compute-next-state)
    - [Results](#results)
  - [Private State Machine: Naive Protocol](#private-state-machine-naive-protocol)
    - [Communication: Send Input](#communication-send-input-1)
    - [Communication: Compute Next State](#communication-compute-next-state-1)
      - [Communication cost of a multiplication](#communication-cost-of-a-multiplication)
    - [Results](#results-1)
  - [Private State Machine: Optimised Protocol](#private-state-machine-optimised-protocol)
    - [Communication: Send Input](#communication-send-input-2)
    - [Communication: Compute Next State](#communication-compute-next-state-2)
    - [Results](#results-2)

# Communication Analysis

For this analysis we will assume that the inputs will all be 8 bits long and there are 1024 different states the machine can be in. The following notation summaries these assumptions:

<!-- https://en.wikipedia.org/wiki/Finite-state_machine#Mathematical_model -->

- $\Sigma = \mathbb{F_{2^8}}$ (input alphabet is the set of all 8 bit strings)
- $S = \mathbb{F_{2^{10}}}$ (1024 states in the state machine)

# Communication Results

<!-- TODO: use compressed point function -->

| Communication Type | State Machine Bits | Naive Protocol Bits     | Optimised Protocol Bits |
| ------------------ | ------------------ | ----------------------- | ----------------------- |
| Send Input         | $8$                | $16$ (x2)               | $512$ (x64)             |
| Compute Next State | $0$                | $26214400$              | $156000$                |
| Total              | $8$                | $26214416$ (x3,276,802) | $156512$ (x19,564)      |

## State Machine

In this example we will be running a state machine on a remote server called Alice. The client called Charlie will send Alice his input and Alice will compute the next state locally. This is **not** a private state machine as Alice knows both the current state and Charlie's inputs.

### Communication: Send Input

Input is sent from Charlie to Alice in plaintext. Because the input is simply from the set $\Sigma$, the input will be $8$ bits long.

```
┌──────────────────┐
│ Charlie (client) │
└────────┬─────────┘
         │
         │
         │ Input Token
         │
         │
┌────────▼───────┐
│ Alice (server) │
└────────────────┘
```

### Communication: Compute Next State

In order to compute the next state Alice needs to know the current state and the input. Alice will then compute the next state locally. Because this computation is done locally, no communication is required.

```
┌──────────────────┐
│ Charlie (client) │
└──────────────────┘


NO COMMUNICATION FOR NEXT STATE COMPUTATION


┌────────────────┐
│ Alice (server) │
└────────────────┘
```

### Results

| Communication      | Bits        |
| ------------------ | ----------- |
| Send Input         | $8$         |
| Compute Next State | $0$         |
| Total              | $8 + 0 = 8$ |

## Private State Machine: Naive Protocol

In this example we will be running a state machine on remote servers called Alice and Bob. The client called Charlie will send Alice and Bob shares of his input. This **is** a private state machine as Alice and Bob will not know the current state or Charlie's inputs.

### Communication: Send Input

When sending the input token $a$ the servers, charlie will generate shares $a_0$ and $a_1$ such that $a = a_0 + a_1$. The share $a_0$ will be sent to Alice the share $a_1$ will be sent to Bob. Because the input shares are from is from the set $\Sigma$, the input shares will be $8$ bits long.

```
                     ┌──────────────────┐
              ┌──────┤ Charlie (client) ├──────┐
              │      └──────────────────┘      │
              │                                │
Input Share 0 │                                │ Input Share 1
              │                                │
              │                                │
     ┌────────▼─────────┐             ┌────────▼───────┐
     │ Alice (server 0) │             │ Bob (server 1) │
     └──────────────────┘             └────────────────┘
```

### Communication: Compute Next State

In order to compute the next state Alice and Bob must use their current state shares as well as Charlie's input shares. Alice and Bob use MPC to compute the multilinear polynomial. See [this notebook](./naive_private_state_machine.ipynb) for an example multilinear polynomial representing the transition function $f(a, s)$ (where $a$ is the input and $s$ is the current state). We will complete this MPC computation by using Beavers triples for multiplication. We will assume that these triples are supplied by a trusted third party.

To evaluate the next multilinear polynomial Alice and Bob must:

1. Receive precomputed triples from a trusted party
   ```
                     ┌───────────────────────┐
                 ┌───┤ Trent (trusted party) ├────┐
                 │   └───────────────────────┘    │
                 │                                │
   Beaver Triple │                                │  Beaver Triple
                 │                                │
        ┌────────▼─────────┐             ┌────────▼───────┐
        │ Alice (server 0) │             │ Bob (server 1) │
        └──────────────────┘             └────────────────┘
   ```
2. Compute the following powers of the current shared state $s$ using the triples (for this example we have to compute $1024$ powers):
   $$s^0 = 1$$
   $$s^{n+1} = s^n * s$$
3. Compute the following powers of the input share $a$ using the triples (for this example we have to compute $256$ powers):
   $$a^0 = 1$$
   $$a^{n+1} = a^n * a$$
4. Combine the powers of the input and state shares to form the multilinear polynomial. This multiplication is completed using triples once again. The following table shows how the powers of the input and state shares are combined.
   | | $a^0$ | $a^1$ | ... | $a^{254}$ | $a^{255}$ |
   | ---------- | ------------- | ------------- | --- | ----------------- | ----------------- |
   | $s^0$ | $a^0s^0$ | $a^1s^0$ | ... | $a^{254}s^0$ | $a^{255}s^0$ |
   | $s^1$ | $a^0s^1$ | $a^1s^1$ | ... | $a^{254}s^1$ | $a^{255}s^1$ |
   | ... | ... | ... | ... | ... | ... |
   | $s^{1022}$ | $a^0s^{1022}$ | $a^1s^{1022}$ | ... | $a^{254}s^{1022}$ | $a^{255}s^{1022}$ |
   | $s^{1023}$ | $a^0s^{1023}$ | $a^1s^{1023}$ | ... | $a^{254}s^{1023}$ | $a^{255}s^{1023}$ |
5. The multilinear polynomial is evaluated using the table above multiplied by the coefficients of all of the multilinear polynomial. The result will be the next state share. The diagram below shows the communication between Alice and Bob. When computing the next state share.
   ```
                      State + Input Share
            ┌────────────────────────────────┐
            │                                │
   ┌────────┴─────────┐             ┌────────▼───────┐
   │ Alice (server 0) │             │ Bob (server 1) │
   └────────▲─────────┘             └────────┬───────┘
            │                                │
            └────────────────────────────────┘
                      State + Input Share
   ```

#### Communication cost of a multiplication

The communication required to compute the next state share is:

- Sending the Beaver triples (2 integers in the field $S$ per multiplication):
  - To Alice
  - To Bob
- Sending each other a share of the current multiplication (1 integers in the field $S$ per multiplication)
  - To Alice
  - To Bob
- Sending intermediate multiplication values to another to recover $e$ and $f$ (2 integers in the field $S$ per multiplication):
  - To Alice
  - To Bob

Therefore for a single multiplication the communication is $2 * 2 + 2 * 1 + 2 * 2 = 10$ integers in the field $S$. Thus for this specific example the communication required to compute the next state share is $10 * 10 = 100$ bits over the wire. Because there are approximately $|\Sigma| * |S|$ multiplications that need to be completed (see table in step 4 above) the total communication required to compute the next state share is $|\Sigma| * |S| * 100$ bits which is $256 * 1024 * 100 = 26214400$ bits. This is approximately 3.28 megabytes for a single state transition.

### Results

| Action                     | Bits                                                                                       |
| -------------------------- | ------------------------------------------------------------------------------------------ |
| Send input to server       | $2\lceil\log_{2}{\|\Sigma\|}\rceil = 2 * 8 = 16$                                           |
| Inter-server communication | $\|\Sigma\| * \|S\| * \lceil\log_{2}{\|\Sigma\|}\rceil * 10 = 256 * 1024 * 100 = 26214400$ |
| Total                      | $16 + 26214400 = 26214416$                                                                 |

## Private State Machine: Optimised Protocol

Similar to the naive protocol, we will be running a state machine on remote servers called Alice and Bob. The client called Charlie will send Alice and Bob send [DPF](https://en.wikipedia.org/wiki/Distributed_point_function) keys of the inputs. This **is** a private state machine as Alice and Bob will not know the current state or Charlie's inputs.

### Communication: Send Input

Instead of sending a share of the input to each server, we will send a DPF key to each server where the input is the point at which the function is 1. See [this notebook](https://github.com/Blake-Haydon/Distributed-Point-Functions/blob/main/naive_DPF_single_bit.ipynb) for an example of a single bit DPF. The diagram below shows the communication between Charlie, Alice and Bob.

<!-- TODO: put DPF size here. The size is found in the paper "Distributed Point Functions and Their Applications"**** -->

```
                 ┌──────────────────┐
          ┌──────┤ Charlie (client) ├──────┐
          │      └──────────────────┘      │
DPF Key 0 │                                │ DPF Key 1
          │                                │
 ┌────────▼─────────┐             ┌────────▼───────┐
 │ Alice (server 0) │             │ Bob (server 1) │
 └──────────────────┘             └────────────────┘
```

### Communication: Compute Next State

In order to compute the next state Alice and Bob must use their current state shares as well as the DPF keys. Alice and Bob use MPC to compute the multilinear polynomial. See [this notebook](./optimised_private_state_machine.ipynb) for an example multilinear polynomial representing the transition function $f_a(s)$ (where $a$ is the input and $s$ is the current state). We will complete this MPC computation by using Beavers triples for multiplication. We will assume that these triples are supplied by a trusted third party.

1. Receive precomputed triples from a trusted party
   ```
                     ┌───────────────────────┐
                 ┌───┤ Trent (trusted party) ├────┐
                 │   └───────────────────────┘    │
                 │                                │
   Beaver Triple │                                │  Beaver Triple
                 │                                │
        ┌────────▼─────────┐             ┌────────▼───────┐
        │ Alice (server 0) │             │ Bob (server 1) │
        └──────────────────┘             └────────────────┘
   ```
2. Compute the following powers of the current shared state $s$ using the triples (for this example we have to compute $1024$ powers):
   $$s^0 = 1$$
   $$s^{n+1} = s^n * s$$
3. Using the powers of $s$ shares from the previous step, we will compute $f_a(s)$ for all $a$ values. In this example we will be evaluating $256$ polynomial functions. Because we are multiplying by constants and doing addition on terms, this step requires no communication between servers.
4. For each polynomial function we must compute $f_a(s) * DPF.Eval(k, a)$, where k is the DPF key and $a$ is the input. Because Alice and Bob both have DPF keys, we have to complete two MPC multiplications. We will use the triples from the previous step to compute these multiplications. Therefore Alice and Bob must compute (where Alice holds the DPF key $k_0$ and Bob holds the DPF key $k_1$):
   $$\sum_{a=0}^{255}{f_a(s) * DPF.Eval(k_0, a)} + \sum_{a=0}^{255}{f_a(s) * DPF.Eval(k_1, a)}$$

Using the previous analysis on the [communication cost of a multiplication](#communication-cost-of-a-multiplication) we are assuming 100 bits are sent over the wire for every multiplication. Therefore the total communication required to compute the next state share is just the number of multiplications to compute the powers of $s$ and evaluate the DPF. To compute powers of $s$ we have $|S|$ multiplications, thus communication cost is $|S| * 100 = 104800$. To evaluate the DPF we have $2 * |\Sigma|$ multiplications, thus communication cost is $2 * |\Sigma| * 100 = 51200$. Therefore the total communication cost is $104800 + 51200 = 156000$ bits which is approximately 0.0195 megabytes.

### Results

| Action                     | Bits                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------- |
| Send input to server       | $2\|\Sigma\| = 2 * 256 = 512$ **(TODO: THIS IS NAIVE, CHANGE TO OPTIMISED DPF KEYS)** |
| Inter-server communication | $\|S\| + 2\|\Sigma\| = 156000$                                                        |
| Total                      | $512 + 156000 = 156512$                                                               |
