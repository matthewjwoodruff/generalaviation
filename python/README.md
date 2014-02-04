Python Version of the GAA problem
=================================

The python version is covenient, since it splits up the model and 
the aggregation.  They can either be imported or run as a pipeline. 

To get the ten objectives, data should flow like this:
```
rows of 27 decision variables  -> response.py -> aggregates.py -> 9 min-max objectives -|
              |--------------------------------------> pfpf.py -> PFPF objective -------|
                                                                                        v
                                                                                  ten objectives
                                                                                        
```

The Python version is LGPL3 licensed.
