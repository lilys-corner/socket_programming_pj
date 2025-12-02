# socket_programming_pj

## Project Objective:
This project's goal is to design, implment, and evaluate a distributed file sharing system using a server-client architecture. Essentially socket programming.

## Project Overview:
This project includes:
- Server-Client Architecture
- File Transfer Protocols: Through TCP
- Multithreading: Multiple concurrent clients
- File Types and Sizes
  - System has the ability to handle .txt, .mp3, and .mp4 files with a minimum size of:
      - Text: 25 MB
      - Audio: 1 GB
      - Video: 2 GB
- File Operations
  - Client-side has these following file operations
    - Upload: Clients upload files to the server. Server will prompt a client if a file already exists and ask a user whether a file should be overwritten.
    - Download: Clients can download files from the server. Server will respond with an error message if a file does not exist
    - Delete: Clients can delete files from the server. Server will respond with an error message if a file does not exist
    - Dir: Clients can view a list of files and subdirectories in the server's file storage path
    - Subfolder: Create and delete subfolders in the server's file storage path
- Performance Evaluation:
  Collects and analyzes performance metrics:
  - Upload and download data rates (MB/sec) of upload and download operations
  - File transfer times
  - System response times
- Error Handling

## Project Assumptions
Assume the project:
- Server and Client take place through localhost
- Takes place in the current directory. (Wherever the server, client, and analyis files are downloaded)
