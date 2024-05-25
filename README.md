# ChatBot Project

## Overview
This project implements a chatbot using Python and various libraries such as AIML, NLTK, Flask, BeautifulSoup, and more. The chatbot is designed to interact with users, answer questions, perform web scraping, analyze sentiment, and maintain user data.

## Features
- **AIML Integration**: Utilizes AIML (Artificial Intelligence Markup Language) for natural language processing and conversation management.
- **Web Scraping**: Utilizes web scraping techniques to fetch information from the web for certain queries.
- **Sentiment Analysis**: Analyzes the sentiment of user messages using the NLTK Vader sentiment analysis tool.
- **User Data Management**: Maintains user data including name, email, gender, and conversation history.
- **Prolog Integration**: Integrates Prolog for logic-based reasoning and knowledge representation.
- **Neo4j Integration**: Utilizes Neo4j as a graph database for storing and querying relationships between entities.

## Requirements
- Python 3.x
- Flask
- NLTK
- BeautifulSoup
- Py2neo
- Pytholog

## Installation
1. Clone the repository: `git clone https://github.com/username/ChatBot.git`
2. Navigate to the project directory: `cd ChatBot`
3. Install dependencies: `pip install -r requirements.txt`

## Usage
1. Run the Flask server: `python main.py`
2. Access the chatbot interface via a web browser at `http://localhost:5000`
3. Interact with the chatbot by typing messages into the input field and pressing Enter.

## File Structure
- `main.py`: Main Python script containing the Flask app and chatbot logic.
- `website.py`: Python script defining the Flask application.
- `userData.py`: Module for managing user data.
- `database.py`: Module for interacting with the database.
- `MyBot/`: Directory containing AIML files for chatbot responses.
- `uploads/`: Directory for storing uploaded files.
- `README.md`: This file providing information about the project.

## Additional Notes
- Ensure that all required Python packages are installed before running the application.
- Make sure to configure Neo4j credentials and connection settings for proper Neo4j integration.
