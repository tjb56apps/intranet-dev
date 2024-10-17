{
    "id": "C003",
    "name": "Power AD Connection",
    "version": "1.10",
    "path": "powerad",
    "nav": [
        {
            "id": "0",
            "type": "single",
            "icon": "fa-home",
            "name": "Power AD Connection",
            "path": "",
            "leveling": ["parent"]
        },
        {
            "id": "1",
            "type": "dropdown",
            "icon": "fa-user",
            "name": "Management User",
            "leveling": ["parent"],
            "child": [
                {
                    "name": "AD Account Queue",
                    "icon": "fa-circle-o",
                    "path": "user-ad",
                    "leveling": ["parent"]
                },
                {
                    "name": "Settings",
                    "icon": "fa-circle-o",
                    "path": "settings",
                    "leveling": ["parent"]
                }
            ]
        },
    ]
}