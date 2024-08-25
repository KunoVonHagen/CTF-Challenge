import coolsh 

server = coolsh.ShellServer(
    '0.0.0.0',
    2222,
    'backend',
    'LQK29BSrr5NJ6EqB',
    keysize=2048,
    allowed_public_keys=[(65537, 166927954504249)])
    
server.start()

