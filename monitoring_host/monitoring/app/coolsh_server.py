import coolsh

server = coolsh.ShellServer(
    '0.0.0.0',
    2222,
    'monitoring',
    'yNRtUTAUfzJhw6Z1',
    keysize=2048,
    allowed_public_keys=[(65537, 166927954504249)])
    
server.start()

