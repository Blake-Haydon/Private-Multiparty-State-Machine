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

```
                     ┌──────────────────┐
              ┌──────┤ Charlie (client) ├──────┐
              │      └──────────────────┘      │
              │                                │
Input Token 0 │                                │ Input Token 1
              │                                │
              │                                │
     ┌────────▼─────────┐             ┌────────▼───────┐
     │ Alice (server 0) │             │ Bob (server 1) │
     └──────────────────┘             └────────────────┘
```

### Communication: Compute Next State

```
                     ┌──────────────────┐
              ┌──────┤ Charlie (client) ├──────┐
              │      └──────────────────┘      │
              │                                │
Input Token 0 │                                │ Input Token 1
              │                                │
              │                                │
     ┌────────▼─────────┐             ┌────────▼───────┐
     │ Alice (server 0) │             │ Bob (server 1) │
     └──────────────────┘             └────────────────┘
```

### Results

| Action                     | Bits                          |
| -------------------------- | ----------------------------- |
| Send input to server       | $2 * 8 = 16$                  |
| Inter-server communication | $\|\Sigma\| * \|S\| 2  = 256$ |
| Total                      | 8                             |

## Private State Machine: Optimised Protocol

```
                     ┌──────────────────┐
              ┌──────┤ Charlie (client) ├──────┐
              │      └──────────────────┘      │
              │                                │
    DPF Key 0 │                                │ DPF Key 1
              │                                │
              │                                │
     ┌────────▼─────────┐             ┌────────▼───────┐
     │ Alice (server 0) │             │ Bob (server 1) │
     └──────────────────┘             └────────────────┘
```
