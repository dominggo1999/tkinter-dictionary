import base64
import httpx
from bs4 import BeautifulSoup
import asyncio
from fake_http_header import FakeHttpHeader
import re


def create_url(url, query):
    return url.replace("QUERY", query)

# async
# https://stackoverflow.com/questions/32456881/getting-values-from-functions-that-run-as-asyncio-tasks


async def load_url(url, json=False, audioBase64=False):

    async with httpx.AsyncClient() as client:
        try:
            fake_user_agent = FakeHttpHeader(domain_name="en").as_header_dict()[
                "User-Agent"]
            r = await client.get(url, headers={"User-Agent": fake_user_agent})

            if(audioBase64):
                # Transform audio into base64
                uri = str(base64.b64encode(r.content).decode("utf-8"))
                content_type = r.headers['Content-Type']
                data = "data:" + content_type + ";base64," + uri
                return {"audioBase64": data}

            if(json):
                return {"json": r.json()}

            return {"html": r.text}
        except:
            print("Something went wrong")
            return {"Error": "something went wrong"}


def scrape():
    URL = "https://realpython.github.io/fake-jobs/"
    page = httpx.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    print(soup)


def google_TTS(word):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if not word:
        return

    url = create_url(
        'https://translate.googleapis.com/translate_tts?client=gtx&ie=UTF-8&tl=en&q=QUERY', word)
    result = loop.run_until_complete(asyncio.gather(
        load_url(url, audioBase64=True)))[0]

    audio_file = result["audioBase64"]

    loop.close()

    if(audio_file):
        return {"audioBase64": audio_file}


def hippoSentences(word):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if not word:
        return

    url = create_url(
        'https://www.wordhippo.com/what-is/sentences-with-the-word/QUERY.html', word)

    result = loop.run_until_complete(asyncio.gather(
        load_url(url)))[0]

    html = result["html"]
    soup = BeautifulSoup(html, 'html.parser')
    valid_sentences = []
    for row in soup.find_all("tr"):
        if row.has_attr('class'):
            className = row["class"][0]
            if(className == "exv2row1" or className == "exv2row2"):
                valid_sentences.append(row.get_text().strip())

    loop.close()

    return {"sentences": valid_sentences}


def power_thesaurus_synonyms(word):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if not word:
        return
    url = create_url(
        'https://www.powerthesaurus.org/QUERY/synonyms', word)

    result = loop.run_until_complete(asyncio.gather(
        load_url(url)))[0]

    html = result["html"]
    soup = BeautifulSoup(html, 'html.parser')

    synonyms = []

    for link in soup.find_all('a'):
        if link.has_attr('title'):
            if re.search(r'\bsynonym\b', link["title"]):
                synonyms.append(link.get_text().strip())
    loop.close()

    return {"synonyms": synonyms}


def vocab_com_definitions(word):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if not word:
        return

    url = create_url(
        'https://www.vocabulary.com/dictionary/definition.ajax?search=QUERY&lang=en', word)

    result = loop.run_until_complete(asyncio.gather(
        load_url(url)))[0]

    html = result["html"]
    soup = BeautifulSoup(html, 'html.parser')

    short = soup.find("p", {"class": "short"})
    long = soup.find("p", {"class": "long"})

    definitions = {
        "short": short.get_text().strip() if short else "",
        "long": long.get_text().strip() if long else ""
    }

    loop.close()

    return {"english": definitions}


def indo_definitions(word):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if not word:
        return

    url = create_url(
        'https://inter.youdao.com/intersearch?q=QUERY&from=en&to=id&interversion=23', word)

    result = loop.run_until_complete(asyncio.gather(
        load_url(url, json=True)))[0]

    try:
        definitions = result["json"]["data"]["eh"]["trs"]
    except KeyError:
        definitions = None

    loop.close()

    if (not definitions):
        return {}

    filtered_definitions = [item for item in definitions if item["i"]]

    valid_definitions = []
    for item in filtered_definitions:
        split = item["i"].split(".")

        if(len(split) < 2):
            valid_definitions.append({})
        else:
            valid_definitions.append({
                "type": split[0],
                "def": split[1]
            })

    return {"indonesia": valid_definitions}
