from collections import defaultdict
import json
from openai import OpenAI
import os



def jsn_text(booker):
    def text_summ(prompt):

        OPENAI_KEY = os.getenv('OPENAI')

        client = OpenAI(api_key=OPENAI_KEY)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system",
                 "content": "You are a powerful summarizer that cleans a text paragraph and return its orginal_text(string),environment (string), action(string), characters[list],summary(string), in json - Dont write add 'json: true'"},
                {"role": "user", "content": prompt}
            ]
        )
        return (response.choices[0].message.content)

    def divider(book_name):
        import docx

        # Load the document (replace with your actual file path)
        doc = docx.Document(f"{book_name}")

        # Combine paragraphs into a single string with proper line breaks
        full_text = "\n".join([para.text for para in doc.paragraphs])

        # Define chapter start points with leading/trailing whitespace removed
        chapter_markers = [
            "In my younger and more vulnerable years my father gave me some advice that I’ve been turning over in my mind ever since.",
            "About halfway between West Egg and New York the motor road hastily joins the railroad and runs beside it for a quarter of a mile",
            "There was music from my neighbor’s house through the summer nights.",
            "On Sunday morning while church bells rang in the villages alongshore, the world and its mistress returned to Gatsby’s house and twinkled hilariously on his lawn.",
            "When I came home to West Egg that night I was afraid for a moment that my house was on fire.",
            "About this time an ambitious young reporter from New York arrived one morning at Gatsby’s door and asked him if he had anything to say.",
            "It was when curiosity about Gatsby was at its highest that the lights in his house failed to go on one Saturday night",
            "I couldn’t sleep all night; a fog-horn was groaning incessantly on the Sound, and I tossed half-sick between grotesque reality and savage, frightening dreams.",
            "After two years I remember the rest of that day, and that night and the next day"
        ]

        # Divide the text into chapters
        chapters = []
        current_pos = 0
        for marker in chapter_markers:
            next_pos = full_text.find(marker.strip(), current_pos)
            if next_pos != -1:
                if current_pos != 0:
                    chapters.append(full_text[current_pos:next_pos].strip())  # Extract and strip chapter text
                current_pos = next_pos
        # Add the final chapter (assuming no marker at the end)
        chapters.append(full_text[current_pos:].strip())

        # Function to divide text into scenes and panels
        def divide_text(text, chapter_number, scene_length=2000, panel_length=500):
            words = text.split()
            scenes = []
            current_scene = []
            current_scene_word_count = 0

            for word in words:
                current_scene.append(word)
                current_scene_word_count += 1
                if current_scene_word_count >= scene_length:
                    scenes.append({
                        "chapter": chapter_number,
                        "scene": " ".join(current_scene)
                    })
                    current_scene = []
                    current_scene_word_count = 0

            if current_scene:
                scenes.append({
                    "chapter": chapter_number,
                    "scene": " ".join(current_scene)
                })

            divided_scenes = []
            for scene in scenes:
                words = scene["scene"].split()
                panels = []
                current_panel = []
                current_panel_word_count = 0

                for word in words:
                    current_panel.append(word)
                    current_panel_word_count += 1
                    if current_panel_word_count >= panel_length:
                        panels.append(" ".join(current_panel))
                        current_panel = []
                        current_panel_word_count = 0

                if current_panel:
                    panels.append(" ".join(current_panel))

                divided_scenes.append({
                    "chapter": scene["chapter"],
                    "scene": scene["scene"],
                    "panels": panels
                })

            return divided_scenes

        # Divide each chapter into scenes and panels
        book_structure = {}
        for i, chapter in enumerate(chapters):
            book_structure[f"Chapter {i + 1}"] = divide_text(chapter, i + 1)

        # Function to divide a text into panels of approximately 200 words each
        def divide_into_panels(text, panel_length=200):
            words = text.split()
            panels = []
            current_panel = []
            current_panel_word_count = 0

            for word in words:
                current_panel.append(word)
                current_panel_word_count += 1
                if current_panel_word_count >= panel_length:
                    panels.append(" ".join(current_panel))
                    current_panel = []
                    current_panel_word_count = 0

            if current_panel:
                panels.append(" ".join(current_panel))

            return panels

        # Final processing to include chapters, scenes, and panels
        final_panels = []
        for chapter_name, scenes in book_structure.items():
            for scene in scenes:
                scene_panels = divide_into_panels(scene["scene"], 200)
                for i, panel in enumerate(scene_panels):
                    final_panels.append({
                        "chapter": scene["chapter"],
                        "scene_number": scenes.index(scene) + 1,
                        "panel_number": i + 1,
                        "panel_text": panel
                    })

        # Ensure panels end at sentences
        for i in range(len(final_panels)):
            j = 0
            for x in range(len(final_panels[i])):
                p = final_panels[i]['panel_text']
                j += 1
                if p and p[-1] != '.' and x != len(final_panels[i]) - 1:
                    st = ''
                    for k in range(len(final_panels[i + 1]['panel_text'])):
                        st = st + (final_panels[i + 1]['panel_text'])[k]
                        if (final_panels[i + 1]['panel_text'])[k] == '.':
                            final_panels[i + 1]['panel_text'] = (final_panels[i + 1]['panel_text'])[k + 1:]
                            break
                    final_panels[i]['panel_text'] = final_panels[i]['panel_text'] + st
                elif p and p[-1] != '.' and x == len(final_panels[i]) - 1 and i != len(final_panels) - 1:
                    st = ''
                    for k in range(len(final_panels[i + 1]['panel_text'])):
                        st = st + final_panels[i + 1]['panel_text'][k]
                        if final_panels[i + 1]['panel_text'][k] == '.':
                            final_panels[i]['panel_text'] = final_panels[i]['panel_text'] + ' ' + st
                            final_panels[i + 1]['panel_text'] = final_panels[i + 1]['panel_text'][k + 1:]
                            break

        # Print the first few panels to verify the structure
        chp = 0
        texter = []
        for panel in final_panels:
            Xt = panel['panel_text']
            for i in range(len(chapter_markers)):
                marker = chapter_markers[i]
                next_pos = Xt.find(marker.strip(), current_pos)
                if next_pos != -1:
                    chp += 1
                    print(chp)
            texter.append(
                f"Chapter {chp} - Scene {panel['scene_number']} - Panel {panel['panel_number']}" + "-\n" + panel[
                    'panel_text'] + "\n")

        return texter

    C = booker
    PP = (divider(C))
    book = ''
    D = '\\'
    for i in range(len(C) - 1, -1, -1):
        if C[i] != D:
            book = book + C[i]
        else:
            break

    # Function to parse the input list
    def parse_input(input_list):
        data = defaultdict(lambda: defaultdict(dict))
        for item in input_list:
            parts = item.split(" - ")
            chapter = parts[0].strip().lower().replace(' ', '_')
            scene = parts[1].strip().lower().replace(' ', '_')
            panel_and_text = parts[2].split(' ', 1)
            panel = panel_and_text[0].strip().lower().replace(' ', '_')
            text = panel_and_text[1].strip() if len(panel_and_text) > 1 else ""
            print('working on chapter : ' + chapter + " Scene : " + scene + parts[2].split('-')[0])
            text = (''.join(parts[2].split('-')[1:]))
            if text:
                print(text)
                print(text_summ(text))
                data[chapter][scene][parts[2].split('-')[0]] = text_summ(text)
        print(data)
        return data

    # Convert the parsed data to the required JSON format
    def convert_to_json(data, book):
        chapters = {}
        for chapter, scenes in data.items():
            chapters[chapter] = scenes

        final_output = {
            "title": book,
            "chapters": chapters
        }
        return json.dumps(final_output, indent=4)

    
    PP = divider(C)
    book = os.path.basename(C)

    parsed_data = parse_input(PP)
    json_output = convert_to_json(parsed_data, book)
    data = json.loads(json_output)

    # Optionally, save the JSON output to a file

    with open("L.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    print("Done")
