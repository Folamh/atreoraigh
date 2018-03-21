test_dict = {
    "2": [
        {
            "1": {
                "src": "127.0.0.1",
                "dst": "127.0.0.1",
                "dport": 55555,
                "data": "Test0"
            }
        },
        {
            "2": {
                "src": "127.0.0.1",
                "dst": "127.0.0.1",
                "dport": 55555,
                "data": "Test1"
            }
        },
        {
            "3": {
                "src": "127.0.0.1",
                "dst": "127.0.0.1",
                "dport": 55555,
                "data": "Test2"
            }
        }
    ]
}

for name, value in test_dict.items():
    print(name)
    for step in value:
        for name, value in step.items():
            print(name)
            for name, value in value.items():
                print(name, value)
