import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        # animal = request.form["animal"]
        anime = request.form["anime"]
        response = openai.Completion.create(
            model="text-davinci-003",
            # prompt=generate_prompt(animal),
            prompt=generate_anime_recsys_prompt_noprimer(anime),
            temperature=0.9,
            max_tokens=512
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    # return render_template("index.html", result=result)
    return render_template("index_animeQA.html", result=result)


def generate_prompt(animal):
    return """Suggest three names for an animal that is a superhero.

Animal: Cat
Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
Animal: Dog
Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
Animal: {}
Names:""".format(
        animal.capitalize()
    )

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