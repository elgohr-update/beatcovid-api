import html
import json

import markdown


def _strip_outer_tags(s):
    """ strips outer html tags """

    start = s.find(">") + 1
    end = len(s) - s[::-1].find("<") - 1

    return s[start:end]


def parse_form_label(label):
    if type(label) is not list:
        label = [label]

    _output = "".join(label).replace("\n", "")

    _output = html.unescape(_output)

    _output = markdown.markdown(_output)

    _output = _strip_outer_tags(_output)

    return _output


def _parse_question(si, choices):
    q = {"id": si["$kuid"], "type": si["type"]}

    if "name" in si:
        q["name"] = si["name"]

    if "label" in si:
        q["label"] = parse_form_label(si["label"])

    if "appearance" in si:
        q["appearance"] = si["appearance"]

    if "relevant" in si:
        q["relevant"] = si["relevant"]

    if "hint" in si:
        q["hint"] = si["hint"]

    if "calculated" in si:
        q["value"] = si["calculated"]

    if "required" in si:
        q["required"] = si["required"]
    else:
        q["required"] = False

    if "constraint" in si:
        q["constraint"] = si["constraint"]

    if "constraint_message" in si:
        q["constraint_message"] = si["constraint_message"]

    if "calculation" in si:
        q["calculation"] = si["calculation"]

    if "parameters" in si:
        q["parameters"] = si["parameters"]

    if "appearance" in si:
        q["appearance"] = si["appearance"]

    if "select_from_list_name" in si:
        c = list(filter(lambda d: d["list_name"] == si["select_from_list_name"], choices))
        c = [
            {"id": si["name"], "value": i["name"], "label": parse_form_label(i["label"]),}
            for i in c
        ]
        q["choices"] = c

    return q


def parse_kobo_json(form_json):
    """
        Takes JSON form output from KOBO and translates it into
        something more useful we can use in our clients. preference
        is to do it here on the server to make it consistent for all
        client rather than messing about with managing the JSON on the
        client.

        @TODO write unit tests
    """
    _json = form_json
    choices = _json["content"]["choices"]
    survey = _json["content"]["survey"]
    # pprint(survey)

    _output = {
        "uid": _json["uid"],
        "name": _json["name"],
        "url": _json["url"],
        "date_created": _json["date_created"],
        "summary": _json["summary"],
        "date_modified": _json["date_modified"],
        "version_count": _json["version_count"],
        "has_deployment": _json["has_deployment"],
        "deployed_versions": _json["deployed_versions"],
        "translations": _json["content"]["translations"],
        "user": {},
    }

    steps = []
    step = {"questions": []}
    _globals = []
    _global = {}
    in_step = False
    q = {}
    for si in survey:
        if si["type"] == "begin_group" and not in_step:
            step = {"name": si["name"], "questions": []}
            if "label" in si:
                step["label"] = parse_form_label(si["label"])
            # q = {}
            in_step = True
        elif si["type"] == "end_group" and in_step:
            steps.append(step)
            in_step = False
        elif in_step:
            q = _parse_question(si, choices)
            step["questions"].append(q)
        else:
            _global = _parse_question(si, choices)

            _globals.append(_global)

    _output["survey"] = {"global": _globals, "steps": steps}
    return _output
