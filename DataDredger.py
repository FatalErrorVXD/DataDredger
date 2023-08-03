import tkinter as tk
import threading
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
import re
import csv
import openai
import json
import webbrowser

def open_donation_link():
    webbrowser.open('https://www.paypal.com/donate/?hosted_button_id=MLLQRMZ5YHT2G')

async def get_urls(base_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'}
    base_domain = urlparse(base_url).netloc

    async def process_page(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                try:
                    soup = BeautifulSoup(await response.text(), 'lxml')
                except UnicodeDecodeError:
                    return []
        urls = []
        for link in soup.find_all('a'):
            url = link.get('href')
            if url and not url.startswith('#') and (url.startswith('http://') or url.startswith('https://') or url.startswith('/')):
                full_url = urljoin(base_url, url)
                # Check if the URL doesn't contain a file extension
                if urlparse(full_url).netloc == base_domain and '.' not in urlparse(full_url).path.split('/')[-1]:
                    urls.append(full_url)
        return urls

    async def crawl_site(base_url):
        visited_urls = set()
        queued_urls = set()
        queue = [base_url]
        all_urls = []

        while queue:
            url = queue.pop(0)
            if url not in visited_urls:
                visited_urls.add(url)
                page_urls = await process_page(url)
                if page_urls:
                    all_urls.extend(page_urls)
                    queue.extend(url for url in page_urls if url not in queued_urls)
                    queued_urls.update(page_urls)

        return all_urls

    return await crawl_site(base_url)





async def get_content(url):
    # Existing code for get_content function
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            soup = BeautifulSoup(await response.text(), 'lxml')
    return soup.get_text()

async def get_status_code(url):
    # Existing code for get_status_code function
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return 'Active' if response.status == 200 else 'Inactive'

async def check_webtrax(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                soup = BeautifulSoup(await response.text(), 'lxml')
            except UnicodeDecodeError:
                return 'Non-text content'

            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.text
                # Check for first format
                if 'webtraxs' in script_content.lower():
                    webtrax_id_match = re.search(r'_trxid = "(.*?)"', script_content)
                    if webtrax_id_match:
                        return webtrax_id_match.group(1)

                # Check for second format
                if 'webtrax' in script_content.lower():
                    webtrax_id_match = re.search(r"setWTID', '(.*?)'", script_content)
                    if webtrax_id_match:
                        return webtrax_id_match.group(1)

                # Debug: print the script content if it contains 'webtrax'
                if 'webtrax' in script_content.lower():
                    print(f"WebTrax found in script, but ID not found. Script content: {script_content}")

            return 'N'


async def get_gtm_id(url, session):
    # Existing code for get_gtm_id function
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'}
    async with session.get(url, headers=headers) as response:
        try:
            text = await response.text()
        except UnicodeDecodeError:
            text = await response.text(errors='ignore')

        soup = BeautifulSoup(text, 'lxml')
    scripts = soup.find_all('script')
    for script in scripts:
        match = re.search(r'GTM-\w+', script.string or '')
        if match:
            return match.group(0)
    return 'N'

async def get_og_title(url, session):
    # Existing code for get_og_title function
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'}
    og_title = ""
    description_source = ""

    try:
        async with session.get(url, headers=headers) as response:
            try:
                text = await response.text()
            except UnicodeDecodeError:
                text = await response.text(errors='ignore')

            soup = BeautifulSoup(text, 'html.parser')
            og_title_tag = soup.find('meta', attrs={'property': 'og:title'})

            if og_title_tag:
                og_title = og_title_tag.get('content')
                description_source = "og:title"
            else:
                title_tag = soup.find('title')
                if title_tag:
                    og_title = title_tag.string
                    description_source = "title tag"

            return og_title, description_source
    except Exception as e:
        print(f'Error occurred while getting OG title for URL "{url}": {e}')
        return og_title, description_source

async def get_og_description(url, session):
    # Existing code for get_og_description function
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'}
    async with session.get(url, headers=headers) as response:
        try:
            soup = BeautifulSoup(await response.text(), 'lxml')
        except UnicodeDecodeError:
            return 'Non-text content', 'Non-text content'

    og_description = soup.find('meta', property='og:description')
    if og_description and og_description.get('content'):
        return og_description['content'], 'Existed'
    else:
        # Generate a description using GPT if none is found
        if openai_api_key:
        # Retrieve the title of the webpage
            page_title = soup.title.string if soup.title else 'Webpage'
        
            # Retrieve the first few words of the webpage as an excerpt
            page_excerpt = ' '.join(soup.get_text().split()[:50])
        
            # Set the key topics or keywords as needed
            keywords = 'keyword1, keyword2, keyword3'  # replace with actual keywords if available
        
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant specializing in creating SEO-optimized meta descriptions."
                    },
                    {
                        "role": "user",
                        "content": f"I need a meta description for a webpage titled '{page_title}' which talks about '{page_excerpt}'. The key topics are '{keywords}'."
                    }
                ],
                max_tokens=40,
                temperature=0.2
            )
            return response['choices'][0]['message']['content'].strip(), 'Generated'
        else:
            return 'No OpenAI API key provided', 'Not Generated'

# Function to get the status of each image in the content of the URL
async def get_image_status(url, session):
    # Existing code for get_image_status function
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'}
    image_statuses = []
    try:
        async with session.get(url, headers=headers) as response:
            try:
                soup = BeautifulSoup(await response.text(), 'lxml')
            except UnicodeDecodeError:
                return 'Non-text content', 'Non-text content', 'Non-text content'
                
            images = soup.find_all('img')
            for img in images:
                src = img.get('src')
                if src and not src.startswith('data:'):  # skip data URLs
                    if src.startswith('//'):
                        src = 'http:' + src
                    elif src.startswith('/'):
                        src = urljoin(url, src)
                    async with session.get(src, headers=headers) as response:
                        image_statuses.append({'source_url': url, 'image_url': src, 'status': response.status})
        print(f"Image statuses for {url}: {image_statuses}")
        return image_statuses
    except Exception as e:
        print(f"Exception in get_image_status: {e}")
        return image_statuses

async def get_pdf_urls(base_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'}
    base_domain = urlparse(base_url).netloc

    async def process_page(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                try:
                    soup = BeautifulSoup(await response.text(), 'lxml')
                except UnicodeDecodeError:
                    return

                pdf_urls = []
                for link in soup.find_all('a'):
                    pdf_url = link.get('href')
                    if pdf_url:
                        full_url = urljoin(url, pdf_url)
                        if urlparse(full_url).netloc == base_domain and full_url.endswith('.pdf'):
                            status = await get_status_code(full_url)
                            title = link.string if link.string else ""
                            pdf_urls.append({'source_url': url, 'pdf_url': full_url, 'status': status, 'title': title})

                return pdf_urls

    async def crawl_site(base_url):
        visited_urls = set()
        queue = [base_url]
        pdf_urls = []

        while queue:
            url = queue.pop(0)
            if url not in visited_urls:
                visited_urls.add(url)
                page_pdf_urls = await process_page(url)
                if page_pdf_urls:
                    pdf_urls.extend(page_pdf_urls)

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            try:
                                soup = BeautifulSoup(await response.text(), 'lxml')
                                for link in soup.find_all('a'):
                                    new_url = link.get('href')
                                    if new_url and urlparse(new_url).netloc == base_domain:
                                        full_url = urljoin(url, new_url)
                                        queue.append(full_url)
                            except UnicodeDecodeError:
                                pass

        return pdf_urls

    return await crawl_site(base_url)

async def get_pdf_status_code(url):
    # Existing code for get_pdf_status_code function
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return response.status

from urllib.parse import urlparse

async def execute(base_url):
    # Extract the website name from the base_url
    website_name = urlparse(base_url).netloc
    global results, image_statuses
    print(f'Starting the scraping operation with base URL: {base_url}')

    # Reset results and image_statuses before each new execution
    results = []
    image_statuses = []
    urls = await get_urls(base_url)
    urls = set(urls)  # Convert URLs list to a set to remove duplicates
    pdf_urls = await get_pdf_urls(base_url)


    print("PDF URLs inside execute:", pdf_urls)  # Add this line to check the retrieved PDF URLs

    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks = [
                get_status_code(url),
                check_webtrax(url),
                get_gtm_id(url, session),
                get_og_title(url, session),
                get_og_description(url, session),
                get_image_status(url, session)
            ]
            task_results = await asyncio.gather(*tasks)
            result_dict = {
                "url": url,
                "status": task_results[0],
                "webtrax": task_results[1],
                "gtm_id": task_results[2],
                "og_title": task_results[3][0],
                "description_source": task_results[3][1],
                "og_description": task_results[4][0],
                "description_source": task_results[4][1]
            }
            image_statuses.extend(task_results[5])
            results.append(result_dict)
    
    # Retrieve PDF URLs separately after the execute function has completed
    pdf_urls = await get_pdf_urls(base_url)
    
    # Call the update_gui function with all the required arguments, including pdf_urls
    update_gui(results, image_statuses, pdf_urls, website_name)

def update_gui(results, image_statuses, pdf_urls, website_name):
    gif_label.grid_remove()  # Hide the GIF label

    try:
        with open(f'{website_name}_results.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=results[0].keys())
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        print("Successfully wrote results.csv")
    except Exception as e:
        print(f'Error writing to results.csv: {e}')

    try:
        if image_statuses and isinstance(image_statuses[0], dict):
            with open(f'{website_name}_image_statuses.csv', 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['source_url', 'image_url', 'status'])
                writer.writeheader()
                for image_status in image_statuses:
                    writer.writerow(image_status)
            print("Successfully wrote image_statuses.csv")
    except Exception as e:
        print(f'Error writing to image_statuses.csv: {e}')

    try:
        if pdf_urls:
            with open(f'{website_name}_pdf_urls.csv', 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['source_url', 'pdf_url', 'status', 'title'])
                writer.writeheader()
                for pdf_url in pdf_urls:
                    writer.writerow(pdf_url)
            print("Successfully wrote pdf_urls.csv")
    except Exception as e:
        print(f'Error writing to pdf_urls.csv: {e}')

    print(f'Scraping operation completed. Results written to results.csv, image_statuses.csv, and pdf_urls.csv.')


def start_execute():
    # Show the GIF label and start the GIF animation
    gif_label.grid()
    update_gif_label()

    # Extract the website name from the base_url
    website_name = urlparse(url_entry.get()).netloc
    global openai_api_key, results, image_statuses
    base_url = url_entry.get()
    openai_api_key = api_key_entry.get()
    openai.api_key = openai_api_key
    # Execute the scraping operation in a separate thread
    # Execute the scraping operation in a separate thread
    # Define the function to run an asyncio coroutine
    run_asyncio_coroutine = lambda coro, *args: asyncio.new_event_loop().run_until_complete(coro(*args))

    # Execute the scraping operation in a separate thread
    threading.Thread(target=run_asyncio_coroutine, args=(execute, base_url)).start()



    

from PIL import Image, ImageTk
from itertools import cycle

# Load the GIF frames
gif_folder_path = "C:/winscraper2/green_frames/"
gif_frame_files = [f"{gif_folder_path}frame_{i}.gif" for i in range(100)]
gif_frames = cycle(ImageTk.PhotoImage(Image.open(frame_file)) for frame_file in gif_frame_files)

root = tk.Tk()
root.title("DataDredger")
root.iconbitmap('neonogin.ico')
root.geometry("400x300")  # Set initial window size

# Create a label to display the GIF frames
gif_label = tk.Label(root)
gif_label.grid(row=7, column=0, columnspan=3)

def update_gif_label():
    gif_label.config(image=next(gif_frames))
    root.after(100, update_gif_label)  # Update every 100 ms


url_label = tk.Label(root, text='Base URL:')
url_label.grid(row=0, column=0)

url_entry = tk.Entry(root)
url_entry.grid(row=0, column=1)

api_key_label = tk.Label(root, text='OpenAI API Key:')
api_key_label.grid(row=1, column=0)

api_key_entry = tk.Entry(root)
api_key_entry.grid(row=1, column=1)

go_button = tk.Button(root, text='Go', command=start_execute)
go_button.grid(row=5, column=0, columnspan=3)

donate_button = tk.Button(root, text='Thank me by buying me a coffee', command=open_donation_link)
donate_button.grid(row=6, column=0, columnspan=3)

root.mainloop()
