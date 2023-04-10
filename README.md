# Private Multiparty State Machine

> This is a fork of [TinySMPC](https://github.com/kennysong/tinysmpc), A tiny library for [secure multi-party computation](https://en.wikipedia.org/wiki/Secure_multi-party_computation), in pure Python. For more information on TinySMPC, please refer to the original repository and its fantastic tutorial!

## **Introduction**

The goal of the protocol is to run a private [state machine](https://en.wikipedia.org/wiki/Finite-state_machine). Privacy in this case means that those who are running this machine should not know what state it currently is in (the number in the circle). They should also no know what inputs are being fed into the machine (the 'a' and 'b' characters on arrows). The only thing that they have knowledge on is the specific machine that they are running.

![State Machine Example](./images/ab_transition_graph.png)

## **Example: 2-Server, 1-Client Private State Machine**

The following diagram shows the communication between 2 servers and 1 client. In the protocol Charlie is the client and Alice and Bob are the servers. Charlie has no knowledge of the state machine that is being run whereas Alice and Bob do. Charlie continually sends inputs to Alice and Bob, causing the private state machine to transition.

```mermaid
flowchart LR
  subgraph Client
   Charlie((Charlie))
  end
  subgraph Servers
   Alice((Alice))
   Bob((Bob))
  end
  Charlie -- Input Share 0 --> Alice
  Charlie -- Input Share 1 --> Bob
```

### **Privacy Properties**

> **WARNING**: If Alice and Bob collude, they can learn the state of the machine as well as the inputs.

- **Private State**: Alice and Bob do not know the current state.
- **Private Input**: Alice and Bob do not know the input.

## **Communication Analysis**

> **INFO**: [Click here to see full analysis](./communication_analysis.md)

Both the naive and optimised protocols have been analyzed for their communication costs. The following table shows the number of messages that are sent between each participant in the protocol.

| Communication Type | State Machine Bits | Naive Protocol Bits   | Optimised Protocol Bits |
| ------------------ | ------------------ | --------------------- | ----------------------- |
| Send Input         | 8                  | 16 (x2)               | 512 (x64)               |
| Compute Next State | 0                  | 26214400              | 156000                  |
| Total              | 8                  | 26214416 (x3,276,802) | 156512 (x19,564)        |

## **Notebooks**

These notebooks contains simple reference implementations in Python of the naive and optimised protocols. They are not intended to be used in production, but rather to provide a simple reference implementation.

- [Naive Private State Machine](./naive_private_state_machine.ipynb)
- [Optimised Private State Machine](./optimised_private_state_machine.ipynb)
