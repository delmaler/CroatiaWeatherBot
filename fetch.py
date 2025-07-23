import json
from turtle import title
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()
url = os.getenv("URL")

def fetch_weather_report():
    """
    Fetches the weather report from the specified URL and saves it as a JSON file.
    """
    # Fetch the HTML content
    response = requests.get(url, timeout=2)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract data into a structured format
    data = {
        "title": "",
        "source": url,
        "report": []
    }

    current_section = None
    start_tag = soup.find('h4', string=lambda t: 'Weather report issued' in t)
    if start_tag:
        data["title"] = start_tag.text.strip()
    current = start_tag.find_next('h5')
    while current:
        if current.name == 'h5':
            current_section = current.text.strip()
            
            data["report"].append({"section": current_section, "content": []})
        elif current.name == 'div':
            if current_section:
                content = current.text.strip()
                if content and not data["report"][-1]["content"]:
                    data["report"][-1]["content"] = content
        else:
            break
        current = current.find_next()
    print(data)
    # Save as readable JSON
    json_path = 'weather_report.json'
    new_json = json.dumps(data, indent=2, ensure_ascii=False)

    # Only write if file doesn't exist or content is different
    if not os.path.exists(json_path) or open(json_path, encoding='utf-8').read() != new_json:
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(new_json)

    print("Saved as readable JSON")
    return data  # Return the parsed data instead of file path
    return new_json