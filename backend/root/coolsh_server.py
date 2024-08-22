import coolsh 

server = coolsh.ShellServer(
    '0.0.0.0',
    2222,
    'backend',
    'LQK29BSrr5NJ6EqB',
    keysize=2048,
    allowed_public_keys=[(65537, 1723184294512097897)])
    
server.start()

