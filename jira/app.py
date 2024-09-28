# Required libraries
import requests
from requests.auth import HTTPBasicAuth
import json

# Define your Jira credentials and the base URL
JIRA_BASE_URL = 'https://your-domain.atlassian.net'
JIRA_EMAIL = 'your-email@example.com'
JIRA_API_TOKEN = 'your-api-token'

# Authentication
auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

# Headers for the API request
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Example: Get details of a specific issue
def get_jira_issue(issue_key):
    url = f'{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}'
    
    response = requests.get(url, headers=headers, auth=auth)
    
    if response.status_code == 200:
        issue_data = response.json()
        return issue_data
    else:
        print(f"Failed to retrieve issue: {response.status_code}")
        return None

# Example usage: Fetch a Jira issue
issue_key = 'PROJECT-123'  # Replace with your issue key
issue_details = get_jira_issue(issue_key)

if issue_details:
    print(json.dumps(issue_details, indent=4))
