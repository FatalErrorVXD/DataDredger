# DataDredger

DataDredger is a robust web scraping tool built with Python. It is capable of scraping a wide range of website data, including URL statuses, WebTrax IDs, Google Tag Manager IDs, Open Graph titles and descriptions, image statuses, and PDF URLs.
It leverages the language understanding capabilities of the GPT-3 model provided by OpenAI to generate meaningful content when the OG (Open Graph) description is missing from a webpage.

## Installation

To run this tool, you will need Python 3.7 or later. Clone the repository and install the necessary dependencies using pip:

```
pip install -r requirements.txt
```

## Usage

Launch the script by running the following command in your terminal:

```
python DataDredger.py
```

A GUI window will appear where you can enter the base URL of the website you want to scrape and your OpenAI API Key (needed for generating OG descriptions). Click the 'Go' button to start the scraping operation.

## Output

The tool outputs three CSV files:

1. `results.csv` contains the scraped data from each URL.
2. `image_statuses.csv` contains the status of each image found on the website.
3. `pdf_urls.csv` contains the URLs, statuses, and titles of all PDF files found on the website.

## Dependencies

- tkinter
- aiohttp
- asyncio
- BeautifulSoup
- urllib
- re
- csv
- openai
- json
- webbrowser

## Donations

If you find this tool useful and want to show your appreciation, please consider buying the developer a coffee by clicking the 'Thank me by buying me a coffee' button in the GUI.

## License

This project is licensed under the terms of the MIT license.

## Disclaimer

Please use this tool responsibly and in accordance with each website's terms of service and/or robots.txt file. The developer of this tool is not responsible for any misuse or potential damages caused by the tool.

## Contributing

Contributions to this project are welcome. Please open an issue to discuss proposed changes or create a pull request.

## Support

For any questions or concerns, please open an issue on this GitHub repository.
