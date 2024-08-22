import coolsh

client = coolsh.ShellClient(
    'monitoring.ctf-challenge.edu',
    2222,
    username='monitoring',
    password='yNRtUTAUfzJhw6Z1',
    keysize=2048)

client.start()

