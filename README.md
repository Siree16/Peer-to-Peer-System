# 📁 Peer-to-Peer (P2P) File Sharing System 🌐

Welcome to the Peer-to-Peer (P2P) File Sharing System project! This project is part of the Software and Data Engineering course and aims to create a decentralized system that allows users to share files directly between their devices without relying on a centralized server. 🚀

## 📜 Problem Statement

In this assignment, we were tasked with designing and implementing a Peer-to-Peer (P2P) system that facilitates file sharing directly between peers. The goal is to understand the fundamental concepts of distributed systems, networking, and data management. 📡

## 🛠️ Solution Overview

### 1. System Design (20 points)
- **Architecture**: The P2P system is designed using a decentralized architecture where each peer acts both as a client and a server. This allows for direct communication and file sharing between peers. 
- **Peer Connection and Communication**: Peers discover each other using a bootstrapping mechanism. Each peer maintains a list of known peers and shares it with new peers joining the network.
- **Security**: Data transmission is secured using encryption to prevent unauthorized access. Additionally, peers authenticate each other using digital signatures.

### 2. Implementation (30 points)
- **Network Protocol**: We implemented a custom protocol for peer communication, including message types for file requests, file transfers, and peer discovery.
- **File Sharing**: Peers can upload and download files. The system handles file fragmentation and reassembly to ensure efficient transfer of large files.
- **Error Handling**: Robust error handling mechanisms are in place to manage network failures, peer disconnections, and data corruption.

### 3. Efficiency and Scalability (30 points)
- **Performance**: The system is optimized to handle an increasing number of peers without significant degradation in performance.
- **File Discovery**: A distributed hash table (DHT) is used for efficient file discovery and lookup across the network.
- **Load Balancing**: Peers share the load of file transfers to prevent bottlenecks and ensure smooth operation.

### 4. User Interface (10 points)
- **UI Design**: The user interface is designed to be intuitive and user-friendly. Users can easily upload, download, and search for files.
- **Functionality**: The UI displays the status of file transfers, connected peers, and available files in the network.

### 5. Follow-up Question (10 points)
- **Decentralized vs. Hybrid Architecture**:
  - **Advantages of Decentralized P2P**:
    - Eliminates the need for a central server, reducing the risk of a single point of failure.
    - Enhances privacy and security as data is not stored centrally.
    - Improves scalability as new peers can join and leave the network dynamically.
  - **Challenges of Decentralized P2P**:
    - More complex peer discovery and network management.
    - Potential for inconsistent data due to lack of central control.
    - Higher overhead for maintaining peer connections and data consistency.
  - **Hybrid Architecture**: Combines elements of both centralized and decentralized architectures, offering a balance between control and scalability. However, it still relies on some degree of centralization, which may introduce vulnerabilities.

## 📂 Project Structure

- **/src**: Contains the source code for the P2P system.
- **/docs**: Includes the project report and documentation.
- **/demo**: Recording of the demo for executive students.
- **README.md**: This file.

## 🚀 Getting Started

### Prerequisites
- Install necessary dependencies (e.g., networking libraries, encryption libraries).

### Running the Project
1. **Compile the code**:
   ```bash
   make
2. **Start a peer** : ./peer --bootstrap <bootstrap-peer-address>

3. **Share a file**: Use the UI to select and upload a file.
4. **Download a file**:Use the UI to search and download a file from the network.

## 📝 Report and Documentation 
The detailed report explaining the approach, design decisions, and assumptions is available in the /docs folder. It includes step-by-step explanations of the system design and implementation. 📖

## 🎥 Demo 
For executive students, a recording of the demo is included in the /demo folder. 🎬

## 🤝 Contribution
Feel free to fork this project and contribute by submitting pull requests. Let's build a robust P2P file sharing system together! 🌟

## 📧 Contact
For any queries or support, please reach out to me. 📬

Thank you for checking out our P2P File Sharing System project! Happy sharing! 😊
