# occdash

View and interact with causal graphs of occasions.

Expects redis to be running on port 6379 for caching. Start using:

    $ redis-server
    
Dash sometimes gets stuck running in the background. This alias is useful to kill it:
 
    alias killdash='kill -9 `lsof -i:8050 -t`'
    
 
    
  

