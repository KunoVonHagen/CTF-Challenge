import coolsh

client = coolsh.ShellClient(
    'backend.ctf-challenge.edu',
    2222,
    username='backend',
    password='LQK29BSrr5NJ6EqB',
    keysize=2048)

client.start()

