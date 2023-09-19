import requests
from requests_oauthlib import OAuth2Session
from bs4 import BeautifulSoup
import spacy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# LinkedIn API credentials (replace with your actual credentials)
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
redirect_uri = 'YOUR_REDIRECT_URI'

# LinkedIn login credentials
linkedin_email = "YOUR_LINKEDIN_EMAIL"
linkedin_password = "YOUR_LINKEDIN_PASSWORD"

# LinkedIn API endpoint for people search
people_search_url = 'https://api.linkedin.com/v2/people-search'

# Initialize spaCy with the appropriate model
nlp = spacy.load("en_core_web_sm")

# Function to generate a personalized connection request message
def generate_personalized_message(about_us_text, job_description_text, recent_posts_text):
    # Initialize lists to store extracted keywords from each section
    about_us_keywords = []
    job_description_keywords = []
    recent_posts_keywords = []

    # Process the 'About Us' text and extract keywords
    about_us_doc = nlp(about_us_text)
    for token in about_us_doc:
        if token.is_alpha and not token.is_stop:
            about_us_keywords.append(token.text)

    # Process the job description text and extract keywords
    job_description_doc = nlp(job_description_text)
    for token in job_description_doc:
        if token.is_alpha and not token.is_stop:
            job_description_keywords.append(token.text)

    # Process the recent posts text and extract keywords
    recent_posts_doc = nlp(recent_posts_text)
    for token in recent_posts_doc:
        if token.is_alpha and not token.is_stop:
            recent_posts_keywords.append(token.text)

    # Join the extracted keywords into a single string
    about_us_keywords_str = ', '.join(about_us_keywords)
    job_description_keywords_str = ', '.join(job_description_keywords)
    recent_posts_keywords_str = ', '.join(recent_posts_keywords)

    # Create a personalized message incorporating the extracted keywords
    personalized_message = f"Hello, I noticed your interest in {about_us_keywords_str}, {job_description_keywords_str}, and recent posts about {recent_posts_keywords_str}. Let's connect!"

    return personalized_message

# Function to send a connection request
def send_connection_request(profile_url, personalized_message):
    try:
        # Set up the webdriver for Chrome
        driver = webdriver.Chrome('path/to/chromedriver.exe')  # Download ChromeDriver from https://chromedriver.chromium.org/

        # Log in to your LinkedIn account programmatically
        driver.get('https://www.linkedin.com/login')
        driver.find_element_by_id('username').send_keys(linkedin_email)
        driver.find_element_by_id('password').send_keys(linkedin_password)
        driver.find_element_by_xpath('//button[text()="Sign in"]').click()

        # Wait for the homepage to load
        driver.implicitly_wait(10)

        # Visit the connection's profile
        driver.get(profile_url)

        # Click the 'Connect' button
        connect_button = driver.find_element_by_xpath('//button[text()="Connect"]')
        if connect_button:
            connect_button.click()

            # Add a personalized message in the connection request
            custom_message = driver.find_element_by_id('custom-message')
            if custom_message:
                custom_message.send_keys(personalized_message)

                # Click the 'Send' button to send the request
                send_button = driver.find_element_by_xpath('//button[text()="Send"]')
                if send_button:
                    send_button.click()

        # Close the browser window
        driver.quit()

        print(f"Connection request sent successfully to {profile_url}")
    except Exception as e:
        print(f"Error sending connection request to {profile_url}: {str(e)}")

# Set up OAuth2Session for LinkedIn API
linkedin = OAuth2Session(client_id, redirect_uri=redirect_uri)

# Generate the authorization URL and open it in a web browser for user consent
authorization_url, state = linkedin.authorization_url('https://www.linkedin.com/oauth/v2/authorization')
print('Please go here and authorize:', authorization_url)

# Get the authorization response (code) after user consent
authorization_response = input('Enter the full callback URL: ')

# Fetch the access token using the authorization code
token = linkedin.fetch_token('https://www.linkedin.com/oauth/v2/accessToken', authorization_response=authorization_response, client_secret=client_secret)

# Store the access token securely
access_token = token['access_token']

# Define your search parameters (e.g., competitor's decision makers)
search_params = {
    'keywords': 'Competitor Decision Maker',
    'network': 'F',
    'facet': 'network,location,industry',
}

# Make a request to LinkedIn API to search for people
response = requests.get(people_search_url, headers={'Authorization': f'Bearer {access_token}'}, params=search_params)

# Parse and process the response data (e.g., extract new connections)
data = response.json()

# Iterate through the search results to monitor new connections
for person in data['elements']:
    # Extract and process information about each person (e.g., new connections)
    profile_url = person['publicIdentifier']
    about_us_text = ''  # Extract 'About Us' section using web scraping
    job_description_text = ''  # Extract job description using web scraping
    recent_posts_text = ''  # Extract recent posts using web scraping

    # Generate a personalized connection request message
    personalized_message = generate_personalized_message(about_us_text, job_description_text, recent_posts_text)

    # Send the connection request with the personalized message
    send_connection_request(profile_url, personalized_message)
    
    # To avoid sending requests too quickly and getting blocked, add a delay
    time.sleep(5)
