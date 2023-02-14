# Communication Analysis

For this analysis we will assume that the inputs will all be 8 bits long and there are 1024 different states the machine can be in. The following notation summaries these assumptions:

<!-- https://en.wikipedia.org/wiki/Finite-state_machine#Mathematical_model -->

- $\Sigma = \mathbb{F_{2^8}}$ (input alphabet is the set of all 8 bit strings)
- $S = \mathbb{F_{2^{10}}}$ (1024 states in the state machine)

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

Therefore the communication required to compute the next state share is:

- Sending the Beaver triples (2 integers in the field $S$ per multiplication):
  - To Alice
  - To Bob
- Sending each other a share of the current multiplication (1 integers in the field $S$ per multiplication)
  - To Alice
  - To Bob
- Sending intermediate multiplication values to another to recover $e$ and $f$ (2 integers in the field $S$ per multiplication):
  - To Alice
  - To Bob

Therefore for a single multiplication the communication is $2 * 2 + 2*1+ 2*2 = 10$ integers in the field $S$. Thus for this specific example the communication required to compute the next state share is $10 * 10 = 100$ bits over the wire. Because there are approximately $|\Sigma| * |S|$ multiplications that need to be completed (see table in step 4 above) the total communication required to compute the next state share is $|\Sigma| * |S| * 100$ bits which is $256 * 1024 * 100 = 26214400$ bits. This is approximately 3.28 megabytes for a single state transition.

### Results

| Action                     | Bits                                                                               |
| -------------------------- | ---------------------------------------------------------------------------------- |
| Send input to server       | $2 * 8 = 16$                                                                       |
| Inter-server communication | $\|\Sigma\| * \|S\| * \log_{2}{\|\Sigma\|} * 10 = 256 * 1024 * 10 * 10 = 26214400$ |
| Total                      | $16 + 26214400 = 26214416$                                                         |

## Private State Machine: Optimised Protocol

Similar to the naive protocol, we will be running a state machine on remote servers called Alice and Bob. The client called Charlie will send Alice and Bob send [DPF](https://en.wikipedia.org/wiki/Distributed_point_function) keys of the inputs. This **is** a private state machine as Alice and Bob will not know the current state or Charlie's inputs.

### Communication: Send Input

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

### Results

| Action                     | Bits                          |
| -------------------------- | ----------------------------- |
| Send input to server       | $2 * 8 = 16$                  |
| Inter-server communication | $\|\Sigma\| * \|S\| 2  = 256$ |
| Total                      | 8                             |
