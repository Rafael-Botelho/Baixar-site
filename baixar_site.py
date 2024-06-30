import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def sanitize_filename(filename):
    # Remove caracteres inválidos do nome do arquivo
    return "".join(c for c in filename if c.isalnum() or c in (' ', '_')).rstrip()

def download_image(image_url, folder_path):
    response = requests.get(image_url)
    image_name = os.path.basename(urlparse(image_url).path)
    image_path = os.path.join(folder_path, image_name)
    with open(image_path, 'wb') as file:
        file.write(response.content)

def get_high_res_image(img):
    # Verifica se há uma versão de alta resolução disponível
    if 'srcset' in img.attrs:
        srcset = img['srcset']
        # Pega a última imagem do srcset (normalmente a de maior resolução)
        high_res_url = srcset.split(',')[-1].split()[0]
        return high_res_url
    return img.get('src')

def save_page_content(url, base_folder_path):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('title').get_text().strip() if soup.find('title') else 'No Title'
    title_sanitized = sanitize_filename(title)
    page_folder = os.path.join(base_folder_path, title_sanitized)
    os.makedirs(page_folder, exist_ok=True)
    
    # Remove header and footer
    header = soup.find('header')
    if header:
        header.decompose()
    footer = soup.find('footer')
    if footer:
        footer.decompose()
    
    # Extract the main content
    content = soup.find('div', class_='entry-content')
    texts = content.get_text().strip() if content else "No Content"

    # Save title and texts
    page_path = os.path.join(page_folder, f'{title_sanitized}.txt')
    with open(page_path, 'w', encoding='utf-8') as file:
        file.write(f"Title: {title}\n\n")
        file.write(texts)

    # Download images
    for img in content.find_all('img') if content else []:
        img_url = get_high_res_image(img)
        if img_url:
            img_url = urljoin(url, img_url)
            download_image(img_url, page_folder)

def crawl_updates_page(updates_url, base_folder_path):
    page_num = 1
    print(str(page_num))
    while True:
        url = f"{updates_url}/page/{page_num}"
        response = requests.get(url)
        if response.status_code != 200:
            break  # Sai do loop quando não há mais páginas
        soup = BeautifulSoup(response.content, 'html.parser')
        h2_tags = soup.find_all('h2', class_='entry-title') #pode mudar de acordo com a arquiterura da pagina
        if not h2_tags:
            break  # Sai do loop se não há mais links de histórias
        for h2 in h2_tags:
            link_tag = h2.find('a') #pode mudar de acordo com a arquiterura da pagina
            if link_tag and 'href' in link_tag.attrs:
                story_url = link_tag['href']
                save_page_content(story_url, base_folder_path)
        page_num += 1


updates_url = 'https://site_para_baixar.com'
output_folder = 'pasta_destino'
os.makedirs(output_folder, exist_ok=True)
crawl_updates_page(updates_url, output_folder)