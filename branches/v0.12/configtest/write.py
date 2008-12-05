#!/usr/bin/env python

from configobj import ConfigObj

config = ConfigObj(indent_type='    ')
config.filename = "settings.conf"

config['menu_topmenu'] = {
    "NautilusSvn::Commit": {
        "label": "",
        "tooltip": "",
    },
    "NautilusSvn::Update": {
        "label": "",
        "tooltip": "",
    },
    "NautilusSvn::NautilusSvn": {
        "label": "",
        "tooltip": "",
        "submenu":{
            "NautilusSvn::Diff": {
                "label": "Diff",
                "tooltip": "",
            },
            "NautilusSvn::Showlog": {
                "label": "Show log",
                "tooltip": "",
            },
            "NautilusSvn::Repobrowser": {
                "label": "Repo Browser",
                "tooltip": "",
            }
        }
    }
}

config.write()
