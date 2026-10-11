from flask import Flask, render_template, request
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    artwork = None
    image_url = None
    error = None
    user_prompt = None

    if request.method == "POST":
        user_prompt = request.form.get("prompt", "").strip()
        if not user_prompt:
            error = "Please provide an object description."
            return render_template("index.html", error=error)

        try:
            # 1. Generate the museum tombstone and extended label using GPT
            label_prompt = f"""An audience member has submitted the following ordinary everyday object:
"{user_prompt}"

Re-contextualize this ordinary object as a prestigious work of contemporary art currently installed in a major contemporary art museum or gallery.
Return a JSON object with the following fields:
1. "artist_name": An invented contemporary artist's name (e.g., "Kaelen Chen-Mercier" or "Søren Lindqvist").
2. "artist_bio": A short biographical line for the artist (e.g., "b. 1997, lives and works between Verdun and the cloud").
3. "title": A high-concept, ironic, poetic, or pretentious contemporary art title (e.g., "The Dialectic of Deferred Maintenance", "A Posture of Unattended Gravity").
4. "year": Year of creation (e.g., "2024" or "2026").
5. "medium": Medium line that mixes real physical materials with abstractions or emotional states (e.g., "Polyester, elastic, fatigue", "Oxidized tin, lint, bureaucratic inertia").
6. "dimensions": Physical dimensions (e.g., "14 × 8 × 3 cm", or "Dimensions variable").
7. "provenance": The object's history of ownership tracing how it ended up in the museum (e.g., "Found under a radiator, 2026; private collection of a dépanneur; acquired by the museum after a tense negotiation").
8. "credit_line": An institutional credit line or acquisition credit (e.g., "Gift of the artist's backpack", "Purchased with funds provided by the Society for Ambient Residues").
9. "extended_label": An extended curatorial wall label of 80 to 120 words. It MUST cite one invented theorist and their invented book (e.g., "As cultural theorist Éloïse Vane observes in 'The Poetics of the Discarded'..."). The label should analyze the object with deep intellectual gravity and deadpan art-historical critique."""

            chat_completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a serious, pretentious contemporary art museum curator and cataloger. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": label_prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.9
            )

            raw_json = chat_completion.choices[0].message.content
            artwork = json.loads(raw_json)

            # 2. Generate an image of the object installed as contemporary art in an exhibition
            image_prompt = (
                f"Contemporary art museum exhibition installation view of {user_prompt}, displayed as a high-concept modern artwork. "
                f"White cube gallery with neutral white museum walls, clean concrete gallery floor, professional museum track spotlight illuminating the object. "
                f"The object is displayed on a minimalist white plinth or within a museum vitrine. High resolution architectural photography, art documentation style."
            )

            candidate_models = ["gpt-image-1-mini", "gpt-image-1", "chatgpt-image-latest", "dall-e-3"]
            img_item = None
            last_img_err = None

            for img_model in candidate_models:
                try:
                    img_resp = client.images.generate(
                        model=img_model,
                        prompt=image_prompt
                    )
                    img_item = img_resp.data[0]
                    break
                except Exception as err:
                    last_img_err = err
                    continue

            if img_item is None:
                raise Exception(f"Image generation failed: {str(last_img_err)}")

            if getattr(img_item, "b64_json", None):
                image_url = f"data:image/png;base64,{img_item.b64_json}"
            elif getattr(img_item, "url", None):
                image_url = img_item.url

        except Exception as e:
            error = f"Error generating exhibition: {str(e)}"

    return render_template(
        "index.html",
        artwork=artwork,
        image_url=image_url,
        error=error,
        user_prompt=user_prompt
    )

if __name__ == "__main__":
    app.run(debug=True)