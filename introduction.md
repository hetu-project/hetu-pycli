# Hetu Client Introduction

## Overview

Hetu is a decentralized protocol designed to create a network of specialized subnets where participants can stake HETU tokens, register as nodes (miners or validators), and contribute to the network's computational capabilities. The protocol establishes an economic incentive structure that rewards participants for contributing computational resources while maintaining network security through staking mechanisms.

## System Architecture

### Core System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Hetu Network                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  Subnet 1   │    │  Subnet 2   │    │  Subnet N   │        │
│  │ (AI/ML)     │    │ (DeFi)      │    │ (Gaming)    │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│           │                 │                 │                │
│           ▼                 ▼                 ▼                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   Miners    │    │   Miners    │    │   Miners    │        │
│  │  (Xylem)    │    │  (Xylem)    │    │  (Xylem)    │        │
│  │ • Compute   │    │ • Compute   │    │ • Compute   │        │
│  │ • Services  │    │ • Services  │    │ • Services  │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│           ▲                 ▲                 ▲                │
│           │                 │                 │                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   Metastruct                               │ │
│  │              (Service Discovery)                           │ │
│  │  • Dendron Registry                                        │ │
│  │  • Service Endpoints                                       │ │
│  │  • Stake Information                                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│           │                 │                 │                │
│           ▼                 ▼                 ▼                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │ Validators  │    │ Validators  │    │ Validators  │        │
│  │(Phloem)     │    │(Phloem)     │    │(Phloem)     │        │
│  │ • Discovery │    │ • Discovery │    │ • Discovery │        │
│  │ • Requests  │    │ • Requests  │    │ • Requests  │        │
│  │ • Validation│    │ • Validation│    │ • Validation│        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Blockchain Layer                            │ │
│  │              (EVM Smart Contracts)                         │ │
│  │  • Dendron Manager                                         │ │
│  │  • Subnet Manager                                          │ │
│  │  • Global Staking                                          │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### User Registration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Node Registration Process                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐ │
│  │   Phase 1   │         │   Phase 2   │         │   Phase 3   │ │
│  │ Stake HETU  │         │ Allocate    │         │ Register    │ │
│  │             │         │ to Subnet   │         │ Dendron     │ │
│  └─────────────┘         └─────────────┘         └─────────────┘ │
│           │                       │                       │      │
│           ▼                       ▼                       ▼      │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐ │
│  │   User      │         │   User      │         │   User      │ │
│  │ • CLI       │────────▶│ • CLI       │────────▶│ • CLI       │ │
│  │ • Wallet    │         │ • Wallet    │         │ • Wallet    │ │
│  └─────────────┘         └─────────────┘         └─────────────┘ │
│           │                       │                       │      │
│           ▼                       ▼                       ▼      │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐ │
│  │ Smart       │         │ Smart       │         │ Smart       │ │
│  │ Contracts   │         │ Contracts   │         │ Contracts   │ │
│  │ • Staking   │         │ • Subnet    │         │ • Dendron   │ │
│  └─────────────┘         └─────────────┘         └─────────────┘ │
│           │                       │                       │      │
│           ▼                       ▼                       ▼      │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐ │
│  │ Blockchain  │         │ Blockchain  │         │ Blockchain  │ │
│  │ • Execute   │         │ • Execute   │         │ • Execute   │ │
│  │ • Confirm   │         │ • Confirm   │         │ • Confirm   │ │
│  └─────────────┘         └─────────────┘         └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Smart Contract Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                   Smart Contract Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    User Interface                          │ │
│  │  • CLI Commands                                           │ │
│  │  • Wallet Management                                      │ │
│  │  • Parameter Validation                                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                │                                │
│                                ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   Processing Layer                         │ │
│  │  • Transaction Builder                                    │ │
│  │  • Gas Estimation                                         │ │
│  │  • Nonce Management                                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                │                                │
│                                ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Mainnet Smart Contracts                    │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Subnet      │  │ Global      │  │ Dendron    │        │ │
│  │  │ Manager     │  │ Staking     │  │ Manager    │        │ │
│  │  │             │  │             │  │            │        │ │
│  │  │ • Create    │  │ • Stake     │  │ • Register │        │ │
│  │  │ • Activate  │  │ • Allocate  │  │ • Manage   │        │ │
│  │  │ • Configure │  │ • Lock      │  │ • Validate │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                │                                │
│                                ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   Blockchain Layer                          │ │
│  │  • EVM Execution                                          │ │
│  │  • Transaction Pool                                       │ │
│  │  • Block Production                                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Core Functionality

### Subnet Management
The protocol enables users to create specialized subnets, each with its own AMM pool and Alpha tokens. Subnets can be customized for specific computational tasks like AI vision, data processing, or machine learning. Each subnet operates as an independent network with its own governance parameters, staking requirements, and reward distribution mechanisms. The SubnetManager contract handles the creation, activation, and lifecycle management of these specialized networks.

### Staking and Economic Security
Participants stake HETU tokens to participate in the network. The staking mechanism provides economic security and determines participation rights across different subnets. The GlobalStaking contract manages the global staking pool, allowing users to allocate their staked tokens to specific subnets based on their interests and computational capabilities. This creates a dynamic ecosystem where capital flows to the most valuable and efficient subnets.

### Dendron Registration System
Users can register as either miners (computational contributors) or validators (network validators), each with different stake requirements and responsibilities. Miners are responsible for providing computational resources and executing tasks, while validators ensure network integrity and validate operations. The DendronManager contract handles the registration process, role assignment, and ongoing management of network participants.

### AMM Trading and Liquidity
Automated market makers enable seamless trading between HETU and subnet-specific Alpha tokens, providing liquidity and price discovery. Each subnet maintains its own AMM pool where users can trade HETU for Alpha tokens or vice versa. This creates a dynamic pricing mechanism that reflects the perceived value of each subnet's computational capabilities and the demand for its services.

## How Users Register as Nodes

### 1. Staking Requirements and Preparation
- **Miners**: Require 500 HETU minimum stake allocation to ensure sufficient economic commitment
- **Validators**: Require 200 HETU minimum stake allocation, reflecting their different role and responsibility level
- Users must first stake HETU globally through the GlobalStaking contract, then allocate specific amounts to target subnets
- The staking process involves locking tokens for a specified period, creating economic incentives for long-term participation

### 2. Registration Process and Technical Requirements
Users register through the CLI by providing comprehensive information:
- **Wallet credentials and stake amount**: Ensuring sufficient economic commitment and identity verification
- **Network endpoint information**: Including Xylem endpoints for communication and Cambium endpoints for monitoring
- **Role selection**: Choosing between miner (computational contributor) or validator (network validator) based on capabilities
- **Subnet identification**: Specifying the target subnet using its unique netuid identifier
- **Technical specifications**: Providing network configuration details for seamless integration

### 3. Node Activation and Network Integration
Once registered, nodes become active participants in the subnet, contributing computational resources or validating network operations based on their role. The activation process involves:
- **Smart contract verification**: Ensuring all registration parameters meet subnet requirements
- **Network synchronization**: Establishing connections with other nodes and the subnet infrastructure
- **Role assignment**: Activating specific functions based on the chosen role (miner or validator)
- **Performance monitoring**: Enabling real-time tracking of node contributions and network health

## Technical Architecture and Smart Contract Design

### Core Smart Contracts
The protocol consists of several interconnected smart contracts that work together to create a robust and scalable network:

- **SubnetManager**: Manages subnet creation, lifecycle, and governance parameters. Handles subnet activation, parameter updates, and overall network coordination.

- **GlobalStaking**: Manages the global staking pool and token allocation. Provides mechanisms for users to stake HETU tokens and allocate them across different subnets based on their preferences and risk tolerance.

- **DendronManager**: Manages dendron registration, role assignment, and ongoing participation. Handles the technical aspects of node integration and ensures proper role-based access control.

- **SubnetAMM**: Provides liquidity pools for token trading between HETU and subnet-specific Alpha tokens. Implements automated market making algorithms to ensure fair pricing and sufficient liquidity.

### Network Interaction Patterns
The protocol implements several key interaction patterns that ensure efficient operation:

- **Stake Allocation**: Users can dynamically allocate their staked tokens across multiple subnets, creating a flexible investment strategy
- **Role-based Access**: Different roles (miner/validator) have different permissions and responsibilities within the network
- **Economic Incentives**: Reward mechanisms ensure that participants are compensated for their contributions and network security
- **Liquidity Management**: AMM pools provide continuous liquidity for token trading, enabling efficient capital allocation

## Economic Model and Incentive Structure

### Token Economics
The protocol uses a dual-token system where HETU serves as the base staking and governance token, while Alpha tokens represent subnet-specific value and utility. This creates a layered economic model where:

- **HETU tokens** provide network-wide security and governance rights
- **Alpha tokens** represent the value of specific subnet services and computational capabilities
- **Staking rewards** incentivize long-term participation and network security
- **Trading fees** from AMM pools provide additional revenue streams for participants

### Network Security
The staking mechanism ensures network security by requiring participants to lock significant capital. This creates economic disincentives for malicious behavior while encouraging honest participation. The validator role provides an additional layer of security through consensus mechanisms and transaction validation.

This comprehensive design creates a flexible, scalable network where participants can contribute computational resources, validate network operations, and trade tokens in a decentralized manner. The protocol's architecture enables continuous innovation and adaptation to changing computational needs while maintaining robust economic incentives and security measures. 