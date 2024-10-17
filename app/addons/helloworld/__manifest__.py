{
    "id": "AAAA",
    "name": "Hello World",
    "version": "1.0",
    "path": "helloworld",
    "nav": [
        {
            "id": "0",
            "type": "single",
            "icon": "fa-home",
            "name": "Home",
            "path": "",
            "leveling": ["parent", "member"]
        },
        {
            "id": "1",
            "type": "dropdown",
            "icon": "fa-file-word-o",
            "name": "Settings",
            "leveling": ["parent", "member"],
            "child": [
                {
                    "name": "Sub menu 1",
                    "icon": "fa-circle-o",
                    "path": "sub-menu-1",
                    "leveling": ["parent"]
                },
                {
                    "name": "Sub menu 2",
                    "icon": "fa-circle-o",
                    "path": "sub-menu-2",
                    "leveling": ["parent", "member"]
                }
            ]
        },
    ]
}