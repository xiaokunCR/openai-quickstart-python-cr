import os
import requests
import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_movie_image(movie_name):
    # Format the search query
    query = movie_name + ' film poster'

    # Search for the movie on Wikipedia
    url = f'https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}&srprop=size&utf8='
    response = requests.get(url)
    response_json = response.json()

    # Retrieve the first result (assuming it's the most relevant)
    if response_json['query']['search']:
        title = response_json['query']['search'][0]['title']
        page_id = response_json['query']['search'][0]['pageid']

        # Get the page content for the movie
        url = f'https://en.wikipedia.org/w/api.php?action=parse&format=json&pageid={page_id}&prop=images&utf8='
        response = requests.get(url)
        response_json = response.json()

        # Find the first image with 'poster' in the file name
        images = response_json['parse']['images']
        for image in images:
            if 'poster' in image.lower():
                # Get the image URL
                url = f'https://en.wikipedia.org/w/api.php?action=query&titles=File:{image}&prop=imageinfo&iiprop=url&format=json&utf8='
                response = requests.get(url)
                response_json = response.json()
                pages = response_json['query']['pages']
                image_url = pages[next(iter(pages))]['imageinfo'][0]['url']
                return image_url
            
@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        # animal = request.form["animal"]
        past_title = request.form["past_title"]
        future_title = request.form["future_title"]
        past_title_image_url = get_movie_image(past_title)
        future_title_image_url = get_movie_image(future_title)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=generate_past_future_prompt_v4(past_title, future_title),
            temperature=0.9,
            max_tokens=512
        )
        return redirect(
            url_for("index",
                    result=response.choices[0].message.content,
                    past_title_image_url=past_title_image_url,
                    future_title_image_url=future_title_image_url
                    )
        )

    result = request.args.get("result")
    past_title_image_url = request.args.get("past_title_image_url")
    future_title_image_url = request.args.get("future_title_image_url")
    # return render_template("index.html", result=result)
    return render_template("index_animeQA.html", 
                           result=result,
                           past_title_image_url=past_title_image_url,
                           future_title_image_url=future_title_image_url)



# get the insparation from here https://www.fandom.com/articles/similar-anime
# feed the model with analogies, 
# then ask it to generate response to target probe
def generate_anime_recsys_prompt(anime):
    return """Suggest a similar anime title in themes and style given a anime title. For examples

Source: Neon Genesis Evangelion
Target: Rahxephon
Reason: When Rahxephon first came out, it received a lot of flak from anime fans for being too similar to Neon Genesis Evangelion. Giant robots, strange creatures attacking Earth, an unstable male lead — no wonder fans considered them carbon copies of each other. But RahXephon takes more time to flesh out its stories, and even includes romantic themes, whereas EVA concentrates more on psychoanalysis and religion.

Source: Trigun Stampede
Target: Cowboy Bebop
Reason: Released within two days of each other, many fans consider Trigun and Cowboy Bebop to be thematically similar. While the former plays out on a desert-like planet, similar to the old west, and the other on various Earth-like worlds, its main leads, Vash and Spike, are mirror images of each other. They are fun, goofy, and carry around some heavy-duty baggage from their past. And the upbeat Jazz tunes of both shows will leave you tapping your feet long after you have finished watching.

Source: BACCANO!
Target: DURARARA!!
Reason: Brain’s Base hit anime gold when they produced Baccano!, and they replicated that success with Durarara!! Both series features a large cast who give their point of view on each episode’s events, whether it’s a psycho on a train or a headless supernatural creature on a motorcycle. It’s the way these series wind their intertwining plots, and how they come together in the end, that makes them seem strikingly similar. Also, if you watch  Durarara!! closely, you’ll spot Baccano!!’s Isaac and Miria hanging around Ikebukuro.

Source: Ghost in the Shell
Target: Ergo Proxy
Reason: Cyberpunk anime were very popular during the ’90s, spawning a myriad of series and movies. Ghost in the Shell is one such title. Over the years, the film has become a dystopian anime staple, with many trying to emulate its success. Ergo Proxy, with its strong female lead who investigates cyber crimes, comes as close as it gets. Re-L Mayer and Motoko’s investigations lead them to explore many themes, such as existentialism and humanism, amidst a cyberpunk backdrop.

Source: {}
Target: """.format(
        anime.capitalize()
    )

def generate_anime_recsys_prompt_noprimer(anime):
    return """I've just finished whole series of {}, what should I watch next on CrunchyRoll?
    and tell me why it would fit my interest""".format(
        anime.capitalize()
    )

def generate_past_future_prompt_v4(past_title, future_title):
    return [{
        "role":"user",
        "content": "You are an expert on the subject of Anime and your job is to convince me to watch {future}. I have enjoyed watching {past}. Tell me how is {future} related to the {past} and why will I like {future}".format(
            past=past_title.capitalize(),
            future=future_title.capitalize()
        )
        }]

def generate_past_future_link_prompt(past_title, future_title):
    return """You are an expert on the subject of Anime and your job is to convince me to watch {future}. I have enjoyed watching {past}. Tell me how is {future} related to the {past} and why will I like {future}""".format(
    past=past_title.capitalize(),
    future=future_title.capitalize()
    )

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000, debug = True)
